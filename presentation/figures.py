"""Figures de la présentation (slides.tex), régénérées en haute qualité à partir des données et des résultats en cache.
À lancer depuis la racine du dépôt : .venv/bin/python presentation/figures.py  (≈ 3 min)"""
import sys
import warnings
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, pdist
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold, KFold, cross_val_score

from src import modeles as M
from src.protocole import Q10_REFERENCE, comparer, decoupages_spatiaux, evaluer, lasso_spatial

FIG = RACINE / "presentation" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
DATA = RACINE / "data"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight", "savefig.dpi": 200})
BLEU, ORANGE, GRIS, ROUGE, VERT = "#1f4e79", "#e07b39", "#8c8c8c", "#c0392b", "#2e8b57"
ETENDUE = (-180, 180, -60, 90)

# Noms lisibles des variables
NOMS = {"lat": "latitude", "lon": "longitude", "MAT_public": "MAT", "logMAP": "log MAP", "pH_public": "pH", "logN515": "log N",
        "clay": "argile", "sand": "sable", "CN": "C:N", "SWC_mean": "SWC moyen", "SWC_warm_rel": "SWC été relatif",
        "végétation ouverte": "végétation ouverte", "forêts tropicales": "forêts tropicales", "forêts extratropicales": "forêts extratropicales"}


def sauver(nom):
    plt.savefig(FIG / f"{nom}.pdf")
    plt.close("all")
    print("figure :", nom)


def carte(serie):
    tableau = np.full(300 * 720, np.nan)
    tableau[serie.index] = serie.values
    return tableau.reshape(300, 720)


def fond_terres(ax):
    ax.imshow(carte(pd.Series(1.0, index=grille.index)), extent=ETENDUE, cmap="Greys", vmin=0, vmax=5)
    ax.set_xlim(-180, 180); ax.set_ylim(-60, 90); ax.set_xticks([]); ax.set_yticks([])
    for cote in ax.spines.values():
        cote.set_visible(False)


v1 = pd.read_csv(DATA / "dataset_v1.csv")
v3 = pd.read_csv(DATA / "dataset_v3.csv")
v4 = pd.read_csv(DATA / "dataset_v4.csv")
grille = pd.read_csv(DATA / "grille_05deg.csv.gz", index_col="cellule")
candidats = ["lat", "lon", "MAT_public", "logMAP", "pH_public", "logN515", "clay", "sand", "CN", "SWC_mean", "SWC_warm_rel"]
X = v4[candidats].join(pd.get_dummies(v4.typologie, dtype=float))
X_grille = grille[candidats].join(pd.get_dummies(grille.typologie, dtype=float)).reindex(columns=X.columns, fill_value=0.0)
decoupages = decoupages_spatiaux(v4.bloc)

# 1. Carte des sites
fig, ax = plt.subplots(figsize=(7, 3.1))
fond_terres(ax)
sc = ax.scatter(v4.lon, v4.lat, c=v4.Q10, cmap="viridis", s=20, edgecolor="k", linewidth=0.4, vmin=0.5, vmax=5)
fig.colorbar(sc, ax=ax, shrink=0.75, label="Q10 mesuré")
sauver("sites")

# 2. Mesures multiples au même point
X1 = ["MAT_public", "MAP_public", "pH_public", "N515"]
v1["groupe"] = v1.groupby(X1).ngroup()
doublons = v1[v1.groupby("groupe").Q10.transform("size") > 1]
moyennes = doublons.groupby("groupe").Q10.mean().sort_values()
rang = doublons.groupe.map({g: i for i, g in enumerate(moyennes.index)})
fig, ax = plt.subplots(figsize=(6.5, 5.2))
ax.scatter(doublons.Q10, rang, alpha=0.7, color=BLEU, s=25)
ax.scatter(moyennes, range(len(moyennes)), marker="|", s=250, c="k")
ax.axvline(Q10_REFERENCE, ls="--", c=ROUGE, label=f"Q10 fixe = {Q10_REFERENCE}")
ax.set_yticks([]); ax.set_ylabel("21 sites (un par ligne)"); ax.set_xlabel("Q10 mesuré"); ax.legend(frameon=False)
sauver("mesures_multiples")

# 3. Q10 par biome
ordre = v3.groupby("biome").Q10.median().sort_values().index
noms_biomes = {"Mediterranean Forests, Woodlands & Scrub": "Méditerranéen", "Deserts & Xeric Shrublands": "Déserts",
               "Tropical & Subtropical Moist Broadleaf Forests": "Forêts tropicales humides", "Temperate Broadleaf & Mixed Forests": "Forêts tempérées feuillues",
               "Tropical & Subtropical Coniferous Forests": "Conifères tropicaux", "Temperate Conifer Forests": "Conifères tempérés",
               "Temperate Grasslands, Savannas & Shrublands": "Prairies tempérées", "Boreal Forests/Taiga": "Forêts boréales",
               "Montane Grasslands & Shrublands": "Prairies de montagne"}
fig, ax = plt.subplots(figsize=(5.8, 4.3))
ax.scatter(v3.Q10, v3.biome.map({b: i for i, b in enumerate(ordre)}), alpha=0.6, color=BLEU, s=22)
ax.set_yticks(range(len(ordre)), [f"{noms_biomes[b]} (n={(v3.biome == b).sum()})" for b in ordre])
ax.axvline(Q10_REFERENCE, ls="--", c=ROUGE, label=f"Q10 fixe = {Q10_REFERENCE}"); ax.set_xlabel("Q10 mesuré"); ax.legend(frameon=False, loc="lower right")
sauver("q10_biomes")

# 4. Validation croisée aléatoire ou par site (forêt aléatoire, 4 variables)
def rmse_cv(cv, groupes=None):
    return -cross_val_score(RandomForestRegressor(random_state=0, n_jobs=-1), v1[X1], v1.Q10, cv=cv, groups=groupes, scoring="neg_root_mean_squared_error").mean()
aleatoire = [rmse_cv(KFold(5, shuffle=True, random_state=s)) for s in range(10)]
groupe = [rmse_cv(GroupKFold(5, shuffle=True, random_state=s), v1.groupe) for s in range(10)]
fig, ax = plt.subplots(figsize=(5.2, 4))
ax.boxplot([aleatoire, groupe], tick_labels=["aléatoire", "groupée par site"], widths=0.5)
ax.set_ylabel("RMSE en validation croisée"); ax.set_title("Même modèle, deux découpages", fontsize=12)
sauver("fuite_validation")
print(f"  aléatoire {np.mean(aleatoire):.3f} | groupé {np.mean(groupe):.3f}")

# 5. Zones de 10° (un découpage)
fig, ax = plt.subplots(figsize=(7, 3.1))
fond_terres(ax)
pli = np.empty(len(v4), int)
for k, (_, tr, te) in enumerate(decoupages[:5]):
    pli[te] = k
for lon in range(-180, 181, 10):
    ax.axvline(lon, c="white", lw=0.6)
for lat in range(-60, 91, 10):
    ax.axhline(lat, c="white", lw=0.6)
couleurs = [BLEU, ORANGE, VERT, ROUGE, "#7b4f9e"]
for k in range(5):
    ax.scatter(v4.lon[pli == k], v4.lat[pli == k], s=16, color=couleurs[k], edgecolor="k", linewidth=0.3, label=f"pli {k + 1}")
ax.legend(ncol=5, loc="lower left", frameon=False, fontsize=9, handletextpad=0.1, columnspacing=0.8)
sauver("zones_spatiales")

# 6. LASSO : stabilité de la sélection et prédictions hors échantillon
coefs = pd.DataFrame([lasso_spatial(X.iloc[tr], v4.log_Q10.iloc[tr], v4.bloc.iloc[tr])[-1].coef_ for _, tr, _ in decoupages], columns=X.columns)
frequence = (coefs != 0).mean().sort_values()
signe = np.sign(coefs.where(coefs != 0).mean())
fig, ax = plt.subplots(figsize=(5.2, 4.2))
ax.barh([NOMS[c] for c in frequence.index], frequence.values * 100, color=[VERT if signe[c] > 0 else ROUGE for c in frequence.index])
ax.axvline(50, ls="--", c=GRIS); ax.set_xlabel("Fréquence de sélection sur 100 plis (%)")
ax.text(98, 0.2, "vert : effet +\nrouge : effet −", ha="right", va="bottom", fontsize=10, color=GRIS)
sauver("lasso_stabilite")
_, oof = evaluer(lambda tr, te: np.exp(lasso_spatial(X.iloc[tr], v4.log_Q10.iloc[tr], v4.bloc.iloc[tr]).predict(X.iloc[te])), decoupages, v4.Q10)

# 7. Semi-variogrammes de Q10 et des résidus
lat, lon = np.radians(v4.lat.values), np.radians(v4.lon.values)
dist = 6371 * 2 * np.arcsin(np.sqrt(np.sin((lat[:, None] - lat) / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat) * np.sin((lon[:, None] - lon) / 2) ** 2))
paires = np.triu_indices(len(v4), 1)
bornes = [0, 50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 20000]
classes = pd.cut(dist[paires], bornes)
variogramme = lambda z: pd.Series((0.5 * (z[:, None] - z) ** 2)[paires]).groupby(classes, observed=True).mean()
residus = v4.Q10.values - oof.mean(axis=0)
etiquettes = ["0–50", "50–100", "100–200", "200–300", "300–500", "500–750", "750–1000", "1000–1500", "1500–2000", "2000–3000", "3000–5000", "> 5000"]
for nom, avec_residus in [("variogramme_q10", False), ("variogramme_residus", True)]:
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(range(12), variogramme(v4.Q10.values), "o-", color=BLEU, label="Q10")
    ax.axhline(v4.Q10.var(), ls="--", c=BLEU, lw=1)
    if avec_residus:
        ax.plot(range(12), variogramme(residus), "o-", color=ORANGE, label="résidus du modèle")
        ax.axhline(residus.var(ddof=1), ls="--", c=ORANGE, lw=1)
    ax.set_xticks(range(12), etiquettes, rotation=45, ha="right"); ax.set_xlabel("Distance entre sites (km)"); ax.set_ylabel("Semi-variance γ(h)")
    ax.legend(frameon=False)
    sauver(nom)

# 8. Comparaison des 16 configurations
ref = f"Q10 = {Q10_REFERENCE}"
H = v4[["MAT_public", "MAP_public", "pH_public"]]
references = {ref: evaluer(lambda tr, te: np.full(len(te), Q10_REFERENCE), decoupages, v4.Q10),
              "moyenne": evaluer(lambda tr, te: np.full(len(te), v4.Q10.iloc[tr].mean()), decoupages, v4.Q10),
              "Hacopian réentraîné": evaluer(lambda tr, te: LinearRegression().fit(H.iloc[tr], v4.Q10.iloc[tr]).predict(H.iloc[te]), decoupages, v4.Q10)}
familles = {"Elastic Net": BLEU, "GAM": BLEU, "SVR": VERT, "GP": VERT, "Random Forest": ORANGE, "XGBoost": ORANGE, "CatBoost": ORANGE, "BART": ORANGE}
resultats = {f"{m} {v}": pd.read_pickle(RACINE / "resultats" / "04" / f"{m.replace(' ', '_')}_{v}.pkl") for m in familles for v in ["V1", "V2"]}
rmse = pd.Series({k: s.rmse.mean() for k, (s, _) in resultats.items()}).sort_values()
meilleure = rmse.index[0]
se = pd.Series({k: comparer(resultats[k][0], resultats[meilleure][0])["erreur standard"] for k in rmse.index})
fig, ax = plt.subplots(figsize=(6.6, 4.4))
for i, k in enumerate(rmse.index):
    ax.errorbar(rmse[k], i, xerr=se[k], fmt="o", color=familles[k.rsplit(" ", 1)[0]], capsize=3, ms=6 if k != "Elastic Net V2" else 10, mfc="white" if k == "Elastic Net V2" else None)
ax.plot([], [], "o", color=BLEU, label="linéaire / additif"); ax.plot([], [], "o", color=VERT, label="noyaux"); ax.plot([], [], "o", color=ORANGE, label="arbres")
for nom, couleur in [("Hacopian réentraîné", "k"), ("moyenne", GRIS), (ref, ROUGE)]:
    valeur = references[nom][0].rmse.mean()
    ax.axvline(valeur, ls="--", c=couleur, lw=1.2, label=f"{nom} ({valeur:.3f})")
ax.set_yticks(range(len(rmse)), rmse.index); ax.invert_yaxis(); ax.set_xlabel("RMSE en validation croisée spatiale")
ax.legend(frameon=True, framealpha=0.95, edgecolor="white", loc="upper right", fontsize=8.5)
sauver("comparaison_modeles")

# 9. Aire d'applicabilité
retenues = list(X.columns[lasso_spatial(X, v4.log_Q10, v4.bloc)[-1].coef_ != 0])
moyenne, ecart_type = X[retenues].mean(), X[retenues].std()
Z_sites, Z_grille = ((X[retenues] - moyenne) / ecart_type).values, ((X_grille[retenues] - moyenne) / ecart_type).values
d_moyenne = pdist(Z_sites).mean()
di_sites = np.empty(len(v4))
for _, tr, te in decoupages[:5]:
    di_sites[te] = cdist(Z_sites[te], Z_sites[tr]).min(axis=1) / d_moyenne
q1, q3 = np.percentile(di_sites, [25, 75])
applicable = pd.Series(cdist(Z_grille, Z_sites).min(axis=1) / d_moyenne <= q3 + 1.5 * (q3 - q1), index=grille.index)
fig, ax = plt.subplots(figsize=(7, 3.1))
ax.imshow(carte(applicable.astype(float)), extent=ETENDUE, cmap=matplotlib.colors.ListedColormap([ORANGE, "#8fb3d9"]), vmin=0, vmax=1)
ax.scatter(v4.lon, v4.lat, s=5, c="k"); ax.set_xticks([]); ax.set_yticks([])
for cote in ax.spines.values():
    cote.set_visible(False)
ax.plot([], [], "s", color="#8fb3d9", label="aire d'applicabilité (interpolation)"); ax.plot([], [], "s", color=ORANGE, label="hors de l'aire (extrapolation)")
ax.legend(loc="lower left", frameon=False, fontsize=9)
sauver("aire_applicabilite")
print(f"  aire d'applicabilité : {grille.aire[applicable].sum() / grille.aire.sum():.1%}")

# 10. Prédictions sur la grille : Elastic Net V2 (avec et sans bridage), SVR V2, BART V2
ajustes = {nom: M.ajuster_final(f, X, v4.log_Q10, v4.bloc, True) for nom, f in {"Elastic Net V2": lambda p: M.elastic_net(), "SVR V2": lambda p: M.svr(), "BART V2": lambda p: M.bart()}.items()}
X_bride = X_grille.clip(X.min(), X.max(), axis=1)
pred = {"Elastic Net V2, sans bridage": np.exp(ajustes["Elastic Net V2"][0].predict(X_grille[ajustes["Elastic Net V2"][1]]))}
for nom, (m, col) in ajustes.items():
    pred[nom + (", bridé" if nom == "Elastic Net V2" else "")] = np.exp(m.predict(X_bride[col]))
pred = pd.DataFrame(pred, index=grille.index)
fig, axes = plt.subplots(1, 4, figsize=(16, 3.8), sharey=True)
for ax, nom in zip(axes, pred.columns):
    ax.scatter(grille.MAT_public, pred[nom], s=0.3, alpha=0.25, color=BLEU, rasterized=True)
    ax.axvspan(v4.MAT_public.min(), v4.MAT_public.max(), color=GRIS, alpha=0.15)
    ax.set_title(nom, fontsize=12); ax.set_xlabel("MAT (°C)"); ax.set_ylim(0, 7)
axes[0].set_ylabel("Q10 prédit")
sauver("formes_reponse")

# 11. Cartes : Elastic Net V2 bridé, BART V2 et leur écart
ecart = pred["Elastic Net V2, bridé"] - pred["BART V2"]
fig, axes = plt.subplots(1, 3, figsize=(15, 3.4))
for ax, (titre, q, cmap, vmin, vmax) in zip(axes, [("Elastic Net V2 (bridé)", pred["Elastic Net V2, bridé"], "viridis", 1, 4.5),
                                                    ("BART V2", pred["BART V2"], "viridis", 1, 4.5),
                                                    ("Écart Elastic Net − BART", ecart, "RdBu_r", -1.5, 1.5)]):
    im = ax.imshow(carte(q), extent=ETENDUE, cmap=cmap, vmin=vmin, vmax=vmax); ax.set_title(titre, fontsize=13)
    ax.set_xticks([]); ax.set_yticks([])
    for cote in ax.spines.values():
        cote.set_visible(False)
    fig.colorbar(im, ax=ax, shrink=0.8)
sauver("cartes_modeles")
froid = grille.MAT_public < v4.MAT_public.min()
for nom in pred.columns:
    print(f"  {nom:30s} Q10 moyen terres {np.average(pred[nom], weights=grille.aire):.2f} | régions froides {np.average(pred[nom][froid], weights=grille.aire[froid]):.2f}")
