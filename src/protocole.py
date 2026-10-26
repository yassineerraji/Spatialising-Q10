"""Fonctions communes du protocole d'évaluation (notebooks 02 et 04).

Protocole (cf. 02_selection_variables, partie B) : validation croisée spatiale par zones de 10° x 10°,
5 plis répétés 20 fois, découpages identiques pour tous les modèles ; erreurs mesurées sur l'échelle de Q10.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso, LassoCV
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Valeur fixe de Q10 à battre (cf. INSTRUCTIONS.md) : seul endroit où elle est définie
Q10_REFERENCE = 2.0


def decoupages_spatiaux(blocs, n_repetitions=20, n_plis=5):
    """Liste de (répétition, indices d'entraînement, indices de test), les zones restant entières."""
    blocs = np.asarray(blocs)
    return [(s, tr, te) for s in range(n_repetitions)
            for tr, te in GroupKFold(n_plis, shuffle=True, random_state=s).split(blocs, groups=blocs)]


def evaluer(predire, decoupages, q10):
    """Applique predire(train, test) -> Q10 prédits sur chaque pli.

    Renvoie les scores par pli (RMSE, MAE) et les prédictions hors échantillon (une ligne par répétition).
    """
    q10 = np.asarray(q10)
    oof = np.full((max(s for s, _, _ in decoupages) + 1, len(q10)), np.nan)
    scores = []
    for s, tr, te in decoupages:
        p = np.asarray(predire(tr, te))
        oof[s, te] = p
        scores.append({"repetition": s, "rmse": np.sqrt(np.mean((q10[te] - p) ** 2)), "mae": np.mean(np.abs(q10[te] - p))})
    return pd.DataFrame(scores), oof


def evaluer_en_cache(fichier, predire, decoupages, q10):
    """Comme evaluer, mais enregistre le résultat dans `fichier` et le relit s'il existe déjà.
    Supprimer le fichier (ou le dossier) pour forcer un nouveau calcul, par exemple après une modification d'un modèle."""
    fichier = Path(fichier)
    if fichier.exists():
        return pd.read_pickle(fichier)
    resultat = evaluer(predire, decoupages, q10)
    fichier.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(resultat, fichier)
    return resultat


def resumer(scores, oof, q10, rmse_reference):
    """RMSE et MAE moyens, R² (prédictions hors échantillon) et gain de RMSE par rapport à une référence
    (dans les notebooks : la RMSE de la valeur fixe Q10_REFERENCE)."""
    q10 = np.asarray(q10)
    r2 = 1 - ((q10 - oof) ** 2).sum(axis=1) / ((q10 - q10.mean()) ** 2).sum()
    return pd.Series({"RMSE": scores.rmse.mean(), "MAE": scores.mae.mean(), "R²": r2.mean(),
                      "gain vs référence (%)": 100 * (1 - scores.rmse.mean() / rmse_reference)})


def comparer(scores_a, scores_b, n_plis=5):
    """Écart apparié de RMSE (a − b) sur les mêmes plis, et son erreur standard corrigée de Nadeau et Bengio (2003),
    qui tient compte du recouvrement des jeux d'entraînement en validation croisée répétée."""
    d = scores_a.rmse.values - scores_b.rmse.values
    se = np.sqrt((1 / len(d) + 1 / (n_plis - 1)) * d.var(ddof=1))
    return pd.Series({"écart": d.mean(), "erreur standard": se, "plis où a fait mieux (%)": 100 * (d < 0).mean()})


def lasso_spatial(X, y, blocs, regle="min", n_plis=5):
    """LASSO sur variables centrées-réduites, pénalité choisie par validation croisée spatiale interne.

    regle="min" : pénalité qui minimise l'erreur interne ;
    regle="1se" : plus forte pénalité dont l'erreur reste à moins d'une erreur standard du minimum.
    Renvoie le modèle ajusté (chaîne mise à l'échelle + LASSO)."""
    Z = StandardScaler().fit_transform(X)
    cv = LassoCV(cv=list(GroupKFold(n_plis).split(Z, y, np.asarray(blocs))), max_iter=50000).fit(Z, y)
    alpha = cv.alpha_
    if regle == "1se":
        moyenne, se = cv.mse_path_.mean(axis=1), cv.mse_path_.std(axis=1) / np.sqrt(n_plis)
        alpha = cv.alphas_[moyenne <= moyenne.min() + se[moyenne.argmin()]].max()
    return make_pipeline(StandardScaler(), Lasso(alpha=alpha, max_iter=50000)).fit(X, y)
