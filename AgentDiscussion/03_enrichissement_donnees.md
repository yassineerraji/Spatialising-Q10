# 03 — Enrichissement du dataset

Notebook : `notebooks/03_enrichissement_donnees.ipynb` → produit `data/dataset_v3.csv` (131 sites, 16 colonnes, aucune valeur manquante).

## Variables ajoutées
| Variable | Source | Méthode | Statut |
|---|---|---|---|
| `clay`, `sand` (%) | SoilGrids 2.0, 5–15 cm | version à 5 km, moyenne des pixels valides sur 3×3 (≈ 15 km) | candidats |
| `SOC` (g/kg) | idem | idem | **non candidat** : redondant avec `N515` (Spearman 0.91) |
| `CN` | SOC / azote, même extraction | — | candidat (son information, avec `N515`, équivaut à celle de SOC) |
| `biome` | RESOLVE Ecoregions 2017 | polygone contenant le site | candidat (catégoriel) |

## Choix de méthode et pourquoi
- **Profondeur 5–15 cm** : la même que `N515`.
- **5 km + moyenne 3×3 plutôt que le pixel de 250 m** : à 250 m, 8 sites tombent sur des pixels masqués (villes, plans d'eau). La moyenne limite aussi l'effet de l'imprécision GPS et se rapproche de l'échelle de la carte ORCHIDEE (0.5°).
- **Validation** : l'azote ré-extrait par cette méthode est corrélé à 0.98 avec `N515`, avec un rapport de 10. Notre méthode reproduit donc celle de l'équipe.
- **Correction** : `N515` est en **mg/kg**, et non en cg/kg comme je l'avais écrit au départ.

## Ce qu'on observe
- **Biomes** : 9 représentés, très inégalement (71 sites en forêts tempérées feuillues et mixtes ; 2 biomes avec un seul site).
- **Cohérence avec Hacopian** : Q10 le plus élevé en prairies de montagne (médiane 3.49) et plus bas en forêts tropicales humides (2.10).
- **Nouveau par rapport à Hacopian** : les sites méditerranéens ont le Q10 le plus bas (médiane 1.27, n = 7). C'est cohérent avec des étés secs qui brident les microbes quand il fait chaud, ce qui renforce l'intérêt d'une variable d'humidité du sol.

## Points ouverts
1. **Biomes rares** : à regrouper avant l'encodage. Proposition : rattacher « Tropical & Subtropical Coniferous Forests » (1 site) aux forêts tropicales humides, et « Deserts & Xeric Shrublands » (1 site) au méditerranéen ou aux prairies tempérées. À trancher en partie B.
2. **Humidité du sol : reportée.** Le serveur TerraClimate (climatologie mensuelle 1991–2020, sans compte requis) est devenu inaccessible pendant le travail. Deux options :
   - réessayer TerraClimate plus tard ;
   - utiliser ERA5-Land via le Climate Data Store, ce qui demande un compte gratuit et une clé API. C'est plus cohérent avec MAT et MAP, qui viennent déjà d'ERA5-Land.
3. **Échelle** : les variables de sol sont moyennées sur ≈ 15 km, alors que MAT, MAP et pH viennent de l'équipe (échelle exacte inconnue, mais N515 suggère une résolution grossière comparable).
