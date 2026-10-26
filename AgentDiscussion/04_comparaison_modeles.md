# 04 — Comparaison des modèles

Notebook : `notebooks/04_comparaison_modeles.ipynb` (données : `data/dataset_v4.csv`). Fonctions communes : `src/protocole.py`.

## Protocole
- **Modèles à comparer** (choix de l'équipe) : Gaussian Process, GAM, Random Forest, CatBoost, XGBoost, SVR (RBF), Elastic Net, BART.
- **Deux variantes par modèle**, sur les mêmes plis : **V1** avec les 12 candidats ; **V2** avec une sélection LASSO refaite dans chaque pli d'entraînement. Pourquoi pas une sélection unique pour tous ? Elle verrait les sites de test (score trop optimiste), et le LASSO, linéaire, désavantagerait les modèles non linéaires. Pourquoi pas une sélection propre à chaque modèle ? Elle serait instable avec 131 sites et coûteuse, et la plupart des modèles régularisent déjà eux-mêmes.
- **Validation croisée spatiale** : zones de 10°, 5 plis × 20 répétitions ; hyperparamètres réglés par une validation croisée spatiale interne.
- **Cible** log(Q10), erreurs mesurées sur Q10 (retour par simple exponentielle).

## Précisions apportées en cours de route (validées par l'équipe)
1. **Sélection V2 : pénalité minimale, et non la règle d'un écart-type.** Cette règle, proposée par défaut au départ, ne retient aucune variable dans 66 % des plis (cf. 02, partie C). Réduit à rien, le LASSO entraîné sur log(Q10) prédit la moyenne géométrique (2.32), plus basse que la moyenne (2.51), d'où une RMSE de 0.99, moins bonne que celle de la moyenne (0.980).
2. **Calcul de la règle de choix du modèle** : l'erreur standard calculée sur les plis d'un seul modèle (≈ 0.12) dépasse tous les écarts entre modèles, et la règle choisirait alors la constante. On utilise donc l'**écart apparié** sur les mêmes plis, avec l'erreur standard corrigée de **Nadeau et Bengio (2003)**, qui tient compte du recouvrement des jeux d'entraînement. Ordre de grandeur obtenu : ≈ 0.03.
3. **Ordre de simplicité** (proposé, non contesté) : Elastic Net < GAM < SVR < GP < Random Forest < XGBoost = CatBoost = BART ; à modèle égal, V2 est plus simple que V1.

## Choix d'implémentation (partie B)
- Modèles définis dans `src/modeles.py`. Les variantes V1 et V2 sont des fonctions communes (`predire_v1`, `predire_v2`). Si le LASSO ne retient aucune variable en V2, on prédit la moyenne géométrique des Q10 d'entraînement.
- Petites grilles d'hyperparamètres, réglées par validation croisée spatiale interne ; GP réglé par vraisemblance marginale ; BART avec les lois a priori par défaut.
- **GAM** : spline pénalisée pour les variables continues, effet linéaire pour les classes de végétation (une courbe n'a pas de sens sur deux valeurs).
- **CatBoost** : typologie en variable catégorielle native en V1.
- **BART : pymc-bart abandonné** (avec pymc 6, les prédictions sur de nouveaux sites gardent la taille du jeu d'entraînement) → **stochtree**, implémentation maintenue par des auteurs de la méthode, ≈ 1 s par ajustement.
- Résultats mis en cache dans `resultats/04/` (ignoré par git).
- **Plantage de XGBoost sur macOS** (segmentation fault) : stochtree embarque sa propre copie d'OpenMP, alors que XGBoost utilise celle de Homebrew. Chargées toutes les deux, elles font planter XGBoost. Correction : stochtree n'est importé qu'au moment d'ajuster le BART. Testé : RF → XGBoost → CatBoost → BART → XGBoost fonctionne.
- pygam impose scipy < 1.17 : scipy est passé de 1.18.1 à 1.16.3.

## Changement de référence : 2.0 au lieu de 2.2
`INSTRUCTIONS.md` fixe désormais la valeur à battre à **2.0** (`context/context.md` indique encore « ~2.2 » : à harmoniser). La valeur est définie une seule fois, dans `src/protocole.py` (`Q10_REFERENCE`). Tous les chiffres ci-dessous sont recalculés. Les résultats des modèles ne changent pas ; seuls la référence et les gains changent.

## Partie A — Références (fait)
| Référence | RMSE | Gain vs 2.0 |
|---|---|---|
| Q10 = 2.0 | 1.083 | — |
| moyenne | 0.980 | 9.5 % |
| Hacopian publié | 0.994 | 8.3 % |
| **Hacopian réentraîné** | **0.963** | **11.1 %** |
| *pour mémoire : Ridge / LASSO (02, partie C)* | *≈ 0.953* | *≈ 12 %* |

- **Battre 2.0 est à la portée d'une simple constante** : la moyenne de nos sites (Q10 = 2.51) bat 2.0 de 9.5 % (−0.103 ± 0.049, mieux dans 89 % des plis). L'essentiel du gain sur 2.0 vient du niveau moyen de Q10. Réserve : rien ne garantit que le Q10 moyen mondial soit proche de celui de nos sites.
- **L'équation publiée de Hacopian ne généralise pas** : elle bat nettement 2.0 sur ses 70 sites d'origine (0.914 contre 1.118), mais fait moins bien que 2.0 sur les 61 autres (1.124 contre 1.106).
- **Hacopian réentraîné** : contre 2.0, −0.120 ± 0.046 (mieux dans 92 % des plis) ; contre la moyenne, −0.017 ± 0.028 (indiscernables).
- **Barre à franchir** : faire mieux que Hacopian réentraîné d'au moins ≈ 0.03 de RMSE.

## Partie B — Les 8 modèles (fait)
| Configuration | RMSE | Gain vs 2.0 |
|---|---|---|
| Elastic Net V1 | **0.950** | 12.2 % |
| BART V2 | 0.954 | 11.9 % |
| SVR V2 | 0.956 | 11.7 % |
| **Elastic Net V2** (retenue) | 0.956 | 11.7 % |
| BART V1 | 0.958 | 11.5 % |
| GAM V2 | 0.960 | 11.3 % |
| *Hacopian réentraîné* | *0.963* | *11.1 %* |
| SVR V1 | 0.968 | 10.6 % |
| Random Forest V2 / V1 | 0.973 / 0.982 | 10.2 / 9.3 % |
| *moyenne* | *0.980* | *9.5 %* |
| GAM V1 | 0.996 | 8.0 % |
| CatBoost V2 / V1 | 1.000 / 1.003 | 7.7 / 7.4 % |
| GP V2 | 1.001 | 7.6 % |
| XGBoost V2 / V1 | 1.008 / 1.022 | 6.9 / 5.6 % |
| GP V1 | 1.049 | 3.1 % |
| *Q10 = 2.0* | *1.083* | — |

- **La complexité ne paie pas** : le meilleur est l'Elastic Net. Tous les modèles battent 2.0, mais le boosting, CatBoost, le GP et le GAM V1 font moins bien que la simple moyenne. R² ≤ 0.013 partout.
- **Règle de choix** : 10 configurations sont équivalentes à la meilleure ; la plus simple est **Elastic Net V2**.
- **Elastic Net V2 face aux références** : contre 2.0, −0.127 ± 0.056 (plus de deux erreurs standard ; mieux dans 92 % des plis) ; contre la moyenne, −0.024 ± 0.059 ; contre Hacopian réentraîné, −0.007 ± 0.062 (indiscernables).
- **V2 contre V1** : la sélection LASSO en amont aide ou est neutre pour tous les modèles sauf l'Elastic Net (+0.005). Elle aide nettement le GAM (−0.036, au-delà d'une erreur standard) et peut-être le GP (−0.049 ± 0.062). → La sélection linéaire n'a pas désavantagé les modèles non linéaires.

## Lecture d'ensemble et pistes
- **Battre 2.0 : oui, nettement (≈ 12 %)**. Mais ≈ 9.5 points viennent du seul niveau moyen de Q10 sur nos sites. Le supplément apporté par les variables (≈ 2.5 points) n'est distinguable ni de la moyenne ni de la forme de modèle de Hacopian réentraînée. Le plafond semble venir des **données** (nombre de sites, couverture géographique, variables disponibles) plus que du choix du modèle.
- **Conséquence pour la carte** : le niveau moyen de Q10 sur la carte compte autant que sa variation spatiale, et il dépend de la représentativité de nos sites.
- Pistes pour aller au-delà : plus de sites dans les régions sous-représentées ; une variable de végétation réelle (MODIS / PFT) ; exploiter la structure spatiale non expliquée (krigeage des résidus) là où il y a des sites ; ou changer d'objectif (par exemple un Q10 par PFT, cf. question à B. Guenet).

## Partie C — Comportement en extrapolation (fait)
Grille mondiale de 0.5° construite dans `06_grille_mondiale.ipynb` (64 745 cellules ; concordance avec les sites vérifiée).

- **Hors domaine** : 64 % des terres ont au moins une variable hors de la plage de nos sites (MAT seule : 38 %). L'**aire d'applicabilité** (Meyer et Pebesma, 2021, sur les 6 variables du modèle retenu) ne couvre que **36 % des terres** : Amérique du Nord tempérée, Europe, Asie de l'Est, nord de l'Inde. Toute l'Amérique du Sud, l'Afrique, l'Australie intérieure, l'Arctique et la Sibérie sont hors de l'aire.
- **Dans l'aire, les modèles s'accordent** (Q10 moyen ≈ 2.4) ; **hors de l'aire, ils divergent**.
- **Q10 moyen mondial prédit : 2.06 à 2.25** selon le modèle, proche de 2.0. L'apport d'une carte tient donc surtout à la **répartition spatiale** de Q10 (plus élevé au froid, plus bas au chaud), pas à son niveau moyen.
- **Artefact saharien** (Elastic Net, GAM : Q10 jusqu'à 6.4) : `SWC_warm_rel` est un rapport de deux quasi-zéros dans les déserts hyper-arides (humidité ≈ 0.001 m³/m³). **Bridage** des variables à la plage des sites → maximum au Sahara 6.40 → 2.68, moyenne mondiale inchangée, validation croisée légèrement meilleure (0.950 contre 0.956 ; −0.006 ± 0.013).
- **Désaccord persistant dans les régions froides** (MAT < −5.2 °C, 10 % des terres) : Elastic Net V2 bridé 3.40 contre BART 2.92, SVR 2.82, Hacopian publié 2.97. Nos données ne permettent pas de trancher (aucun site aussi froid).

### Décisions proposées (à valider)
1. Carte : **Elastic Net V2 avec bridage des variables** (le plus simple, artefact supprimé, validation croisée légèrement meilleure).
2. Livrer la carte **avec son aire d'applicabilité**.
3. Régions froides : produire aussi la carte **BART V2** comme variante de sensibilité ; demander l'avis de B. Guenet ou s'appuyer sur la littérature des hautes latitudes.

### Points techniques
- `src/modeles.py` : `ajuster_final` (entraînement sur tous les sites) et option `brider` dans `predire_v1` / `predire_v2` (désactivée par défaut, donc les résultats en cache restent valides).
- Le nom de colonne de `resumer` est devenu « gain vs référence (%) » : le notebook 05 (copules) passe la RMSE de sa propre constante (2.2), et une étiquette « vs 2.0 » y aurait été fausse.
