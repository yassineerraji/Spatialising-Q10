# 03 — Enrichissement du dataset

Notebook : `notebooks/03_enrichissement_donnees.ipynb` → produit `data/dataset_v3.csv` (131 sites, 18 colonnes, aucune valeur manquante).

## Variables ajoutées
| Variable | Source | Méthode | Statut |
|---|---|---|---|
| `clay`, `sand` (%) | SoilGrids 2.0, 5–15 cm | version à 5 km, moyenne des pixels valides sur 3×3 (≈ 15 km) | candidats |
| `SOC` (g/kg) | idem | idem | **non candidat** : redondant avec `N515` (Spearman 0.91) |
| `CN` | SOC / azote, même extraction | — | candidat (son information, avec `N515`, équivaut à celle de SOC) |
| `biome` | RESOLVE Ecoregions 2017 | polygone contenant le site | candidat (catégoriel) |
| `SWC_mean` (m³/m³) | ERA5-Land 1995–2024, couche 0–7 cm, via Google Earth Engine | moyenne annuelle, disque de ≈ 15 km | candidat |
| `SWC_warm_rel` | idem | 3 mois les plus chauds / moyenne annuelle | candidat |

## Choix de méthode et pourquoi
- **Sol, profondeur 5–15 cm** : la même que `N515`.
- **Moyenne sur ≈ 15 km plutôt qu'un pixel** : à 250 m, 8 sites tombent sur des pixels masqués (villes, plans d'eau). La moyenne limite aussi l'effet de l'imprécision GPS et se rapproche de l'échelle de la carte ORCHIDEE (0.5°). Même règle pour ERA5-Land.
- **ERA5-Land 1995–2024** : même source et même période que MAT et MAP, pour la cohérence des variables climatiques.

## Validations (notre extraction contre les colonnes de l'équipe)
| Variable | Corrélation | Conclusion |
|---|---|---|
| azote → `N515` | 0.98 (rapport ×10) | `N515` est l'azote SoilGrids en **mg/kg** (et non en cg/kg comme je l'avais écrit) |
| MAT → `MAT_public` | 0.996 | MAT vient bien d'ERA5-Land 1995–2024 |
| MAP → `MAP_public` | 0.992 | MAP vient bien d'ERA5-Land 1995–2024 |
| `SWC_warm_rel` → colonne d'origine | 0.983 | **définition retrouvée** : humidité ERA5-Land 0–7 cm, 3 mois les plus chauds / moyenne annuelle |

Notre méthode d'extraction reproduit donc celle de l'équipe. On saura recalculer chaque variable partout pour la carte mondiale.

## Ce qu'on observe
- **Biomes** : 9 représentés, très inégalement (71 sites en forêts tempérées feuillues et mixtes ; 2 biomes avec un seul site).
- **Cohérence avec Hacopian** : Q10 le plus élevé en prairies de montagne (médiane 3.49) et plus bas en forêts tropicales humides (2.10).
- **Nouveau** : les sites méditerranéens ont le Q10 le plus bas (médiane 1.27) et le `SWC_warm_rel` le plus bas (0.61, contre 0.94 à 1.11 ailleurs). C'est cohérent avec l'hypothèse « sol sec en été → microbes bridés quand il fait chaud ».
- `SWC_warm_rel` est, après `SOC`, la nouvelle variable la plus liée à Q10 (Spearman +0.21).

## Points ouverts
1. **Biomes rares** : à regrouper avant l'encodage. Proposition : rattacher « Tropical & Subtropical Coniferous Forests » (1 site) aux forêts tropicales humides, et « Deserts & Xeric Shrublands » (1 site) au méditerranéen. À trancher en partie B.
2. **Variables non reprises** : `Ts_mean` et `Ts_max` sont probablement des températures du sol ERA5-Land (`Ts_mean` ≈ MAT + 0.7 °C). Elles sont redondantes avec MAT (corrélations 0.99 et 0.86, au-dessus du seuil de 0.8), donc inutile de les recalculer.
3. **Google Earth Engine** : exécuter le notebook 03 demande un compte Earth Engine authentifié avec accès au projet `crp-geosciences`.
