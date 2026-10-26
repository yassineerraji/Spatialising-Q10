"""Les 8 modèles comparés dans 04_comparaison_modeles.

Chaque fonction renvoie un modèle « vierge ». Ceux qui ont des hyperparamètres à régler sont enveloppés dans une
recherche sur grille (GridSearchCV) dont la validation croisée interne est spatiale : on passe les zones des sites
d'entraînement au moment de l'ajustement (cf. ajuster). Tous apprennent log(Q10).
"""
from functools import reduce
from operator import add

import numpy as np
from catboost import CatBoostRegressor
from pygam import LinearGAM, l, s
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor

from src.protocole import lasso_spatial

CV_INTERNE = GroupKFold(5)  # validation croisée interne, par zones (les zones sont passées à l'ajustement)


def recherche(modele, grille):
    """Recherche sur grille des hyperparamètres, notée par la RMSE en validation croisée spatiale interne."""
    return GridSearchCV(modele, grille, cv=CV_INTERNE, scoring="neg_root_mean_squared_error")


def ajuster(modele, X, y, zones):
    """Ajuste le modèle ; les zones ne servent qu'aux modèles qui règlent leurs hyperparamètres."""
    return modele.fit(X, y, groups=zones) if isinstance(modele, GridSearchCV) else modele.fit(X, y)


class GAM(BaseEstimator, RegressorMixin):
    """Modèle additif généralisé (pygam) : une spline pénalisée par variable continue, un effet linéaire par variable
    binaire (classes de végétation) ; lam règle la souplesse des courbes."""

    def __init__(self, lam=1.0, n_splines=8):
        self.lam, self.n_splines = lam, n_splines

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        termes = reduce(add, [l(j, lam=self.lam) if len(np.unique(X[:, j])) <= 2 else s(j, n_splines=self.n_splines, lam=self.lam)
                              for j in range(X.shape[1])])
        self.gam_ = LinearGAM(termes).fit(X, np.asarray(y))
        return self

    def predict(self, X):
        return self.gam_.predict(np.asarray(X, dtype=float))


class CatBoost(BaseEstimator, RegressorMixin):
    """CatBoost ; les variables catégorielles (par leur nom) sont traitées nativement, sans one-hot."""

    def __init__(self, depth=4, l2_leaf_reg=3, categorielles=()):
        self.depth, self.l2_leaf_reg, self.categorielles = depth, l2_leaf_reg, categorielles

    def fit(self, X, y):
        self.cb_ = CatBoostRegressor(iterations=300, learning_rate=0.05, depth=self.depth, l2_leaf_reg=self.l2_leaf_reg,
                                     random_seed=0, verbose=0, thread_count=4, allow_writing_files=False)
        self.cb_.fit(X, y, cat_features=[c for c in self.categorielles if c in X.columns])
        return self

    def predict(self, X):
        return self.cb_.predict(X)


class BART(BaseEstimator, RegressorMixin):
    """BART (stochtree) : somme d'arbres bayésienne avec les lois a priori par défaut ; prédiction = moyenne a posteriori.
    Échantillonnage : 10 itérations d'initialisation rapide (« grow-from-root »), 200 de chauffe, 500 conservées."""

    def __init__(self, graine=0):
        self.graine = graine

    def fit(self, X, y):
        # Import tardif : stochtree embarque sa propre copie d'OpenMP qui, chargée avant XGBoost, le fait planter (macOS)
        from stochtree import BARTModel
        self.bart_ = BARTModel()
        self.bart_.sample(X_train=np.asarray(X, dtype=float), y_train=np.asarray(y, dtype=float), num_gfr=10, num_burnin=200,
                          num_mcmc=500, general_params={"random_seed": self.graine})
        return self

    def predict(self, X):
        pred = self.bart_.predict(X=np.asarray(X, dtype=float))
        return (pred["y_hat"] if isinstance(pred, dict) else pred).mean(axis=1)


def elastic_net():
    return recherche(make_pipeline(StandardScaler(), ElasticNet(max_iter=50000)),
                     {"elasticnet__alpha": np.logspace(-3, 0, 10), "elasticnet__l1_ratio": [0.1, 0.5, 0.9]})


def gam():
    return recherche(make_pipeline(StandardScaler(), GAM()), {"gam__lam": [0.1, 1, 10, 100, 1000]})


def svr():
    return recherche(make_pipeline(StandardScaler(), SVR(kernel="rbf")),
                     {"svr__C": [0.3, 1, 3, 10], "svr__gamma": ["scale", 0.03, 0.1], "svr__epsilon": [0.05, 0.1, 0.2]})


def gp(n_variables):
    """Processus gaussien : une échelle par variable (ARD) + bruit ; hyperparamètres par vraisemblance marginale."""
    noyau = ConstantKernel() * RBF(length_scale=np.ones(n_variables), length_scale_bounds=(1e-2, 1e3)) + WhiteKernel()
    return make_pipeline(StandardScaler(), GaussianProcessRegressor(noyau, normalize_y=True, n_restarts_optimizer=2, random_state=0))


def random_forest():
    return recherche(RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=-1),
                     {"max_features": [0.5, 1.0], "min_samples_leaf": [2, 5]})


def xgboost():
    return recherche(XGBRegressor(n_estimators=300, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, min_child_weight=3, random_state=0, n_jobs=4),
                     {"max_depth": [2, 3], "reg_lambda": [1, 10]})


def catboost(categorielles=()):
    return recherche(CatBoost(categorielles=tuple(categorielles)), {"depth": [2, 4], "l2_leaf_reg": [3, 10]})


def bart():
    return BART()


def predire_v1(fabrique, X, y_log, zones, tr, te, brider=False):
    """Variante V1 : modèle entraîné sur log(Q10) avec toutes les variables de X ; prédictions ramenées à Q10.
    fabrique(p) renvoie un modèle vierge pour p variables. brider=True : variables des sites de test limitées
    à la plage [min ; max] des sites d'entraînement avant la prédiction."""
    modele = ajuster(fabrique(X.shape[1]), X.iloc[tr], y_log.iloc[tr], zones.iloc[tr])
    X_test = X.iloc[te].clip(X.iloc[tr].min(), X.iloc[tr].max(), axis=1) if brider else X.iloc[te]
    return np.exp(modele.predict(X_test))


def ajuster_final(fabrique, X, y_log, zones, selection=True):
    """Ajuste une configuration sur tous les sites, pour prédire sur la grille mondiale.
    selection=True (V2) : sélection LASSO sur tous les sites d'abord. Renvoie le modèle et la liste de ses variables."""
    colonnes = list(X.columns[lasso_spatial(X, y_log, zones)[-1].coef_ != 0]) if selection else list(X.columns)
    return ajuster(fabrique(len(colonnes)), X[colonnes], y_log, zones), colonnes


def predire_v2(fabrique, X, y_log, zones, tr, te, brider=False):
    """Variante V2 : sélection LASSO (pénalité minimale) sur les seuls sites d'entraînement, puis le modèle
    sur les variables retenues. Si aucune n'est retenue : moyenne géométrique des Q10 d'entraînement."""
    garde = lasso_spatial(X.iloc[tr], y_log.iloc[tr], zones.iloc[tr])[-1].coef_ != 0
    if not garde.any():
        return np.full(len(te), np.exp(y_log.iloc[tr].mean()))
    return predire_v1(fabrique, X.loc[:, garde], y_log, zones, tr, te, brider)
