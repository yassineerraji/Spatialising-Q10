# Données

| Fichier | Description | Créé par |
|---|---|---|
| `dataset.csv` | Dataset enrichi original (173 mesures, 15 colonnes). **Ne jamais modifier.** | l'équipe |
| `dataset_v1.csv` | Colonnes claires et utiles uniquement (173 lignes, 10 colonnes). | `notebooks/00_preparation_donnees.ipynb` |
| `dataset_v2.csv` | v1 agrégée : une ligne par site (131 lignes, 11 colonnes). | `notebooks/00_preparation_donnees.ipynb` |
| `dataset_v3.csv` | v2 enrichie de variables de sol et du biome (131 lignes, 16 colonnes). **Version de référence.** | `notebooks/03_enrichissement_donnees.ipynb` |
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

Sources de MAT, MAP et pH : identiques à Hacopian (vérifié dans son script R), très probables pour tout le dataset.
