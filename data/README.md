# Données

| Fichier | Description | Créé par |
|---|---|---|
| `dataset.csv` | Dataset enrichi original (173 mesures, 15 colonnes). **Ne jamais modifier.** | l'équipe |
| `dataset_v1.csv` | Colonnes claires et utiles uniquement (173 lignes, 10 colonnes). | `notebooks/00_preparation_donnees.ipynb` |
| `dataset_v2.csv` | v1 agrégée : une ligne par site (131 lignes, 11 colonnes). | `notebooks/00_preparation_donnees.ipynb` |
| `dataset_v3.csv` | v2 enrichie de variables de sol, d'humidité du sol et du biome (131 lignes, 18 colonnes). | `notebooks/03_enrichissement_donnees.ipynb` |
| `dataset_v4.csv` | **Table de modélisation** : v3 avec les choix validés appliqués (cible log Q10, log de MAP et N515, typologie de végétation, zone spatiale). **Version de référence pour la modélisation.** | `notebooks/02_selection_variables.ipynb` (partie B, étape 4) |
| `typologie_biomes.csv` | Correspondance des 14 biomes RESOLVE vers les 3 classes de la typologie de végétation (pour la carte mondiale). | idem |
| `grille_05deg.csv.gz` | Les 12 candidats sur une grille mondiale de 0.5° (64 745 cellules ; index `cellule` = ligne × 720 + colonne ; colonne `aire` = cosinus de la latitude, pour pondérer par la surface). | `notebooks/06_grille_mondiale.ipynb` |
| `externe/` | Fichiers sources téléchargés (SoilGrids, RESOLVE). Ignoré par git, recréé par le notebook 03. | `notebooks/03_enrichissement_donnees.ipynb` |

## `dataset.csv` — origine
Construit par l'équipe : dataset public de Hacopian et al. (2026), complété par d'autres mesures de Q10 (bibliothèque privée du CNRS, recherche en ligne, etc.). L'origine de chaque ligne est indiquée dans la colonne `source`.

## Colonnes

| Colonne | Description | Unité | Versions |
|---|---|---|---|
| `site` | identifiant de la mesure (à partir de v2 : identifiants des mesures agrégées, séparés par ` + `) | — | v1+ |
| `source` | origine de la mesure (`paper` = Hacopian, `mgrsd`, `holisoils`, `root_removal`, `figure`, `new paper`) | — | v1+ |
| `study` | étude / publication d'origine (à partir de v2 : études concaténées si plusieurs) | — | v1+ |
| `Q10` | sensibilité de la respiration microbienne du sol à la température (cible ; à partir de v2 : moyenne du site) | — | v1+ |
| `n_mesures` | nombre de mesures agrégées dans le site | — | v2+ |
| `lat`, `lon` | coordonnées du site | degrés | v1+ |
| `MAT_public` | température moyenne annuelle de l'air à 2 m, ERA5-Land | °C | v1+ |
| `MAP_public` | précipitations moyennes annuelles, ERA5-Land | mm/an | v1+ |
| `pH_public` | pH du sol (eau), SoilGrids, 0–5 cm | — | v1+ |
| `N515` | azote du sol, SoilGrids, 5–15 cm | mg/kg | v1+ |
| `clay` | argile, SoilGrids 5–15 cm, moyenne sur ≈ 15 km (3×3 pixels de 5 km) | % | v3 |
| `sand` | sable, idem | % | v3 |
| `SOC` | carbone organique, idem (non candidat : redondant avec `N515`) | g/kg | v3 |
| `CN` | rapport carbone / azote, SoilGrids 5–15 cm, idem | — | v3 |
| `biome` | biome RESOLVE Ecoregions 2017 (Dinerstein et al., 2017) | catégorie | v3 |
| `SWC_mean` | humidité du sol ERA5-Land 1995–2024, couche 0–7 cm, moyenne annuelle sur un disque de ≈ 15 km (via Google Earth Engine) | m³/m³ | v3 |
| `SWC_warm_rel` | même humidité, moyenne des 3 mois les plus chauds / moyenne annuelle | — | v3 |

Sources de MAT, MAP et pH : identiques à Hacopian (vérifié dans son script R). MAT et MAP sont confirmés par recalcul depuis ERA5-Land 1995–2024 dans le notebook 03 (r > 0.99).

## Colonnes ajoutées dans `dataset_v4.csv`

| Colonne | Description |
|---|---|
| `log_Q10` | logarithme de Q10 : **cible des modèles** |
| `logMAP`, `logN515` | logarithme de `MAP_public` et de `N515` (candidats à la place des valeurs brutes) |
| `typologie` | végétation en 3 classes : forêts extratropicales, forêts tropicales, végétation ouverte |
| `bloc` | zone spatiale (carré de 10° × 10°) utilisée par la validation croisée |

**Les 12 candidats** : `lat`, `lon`, `MAT_public`, `logMAP`, `pH_public`, `logN515`, `clay`, `sand`, `CN`, `SWC_mean`, `SWC_warm_rel`, `typologie`. `MAP_public` brute est gardée pour la référence Hacopian. `SOC`, `N515` brute et `biome` ne sont pas repris.
