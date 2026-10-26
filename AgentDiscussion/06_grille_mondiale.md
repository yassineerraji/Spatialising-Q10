# 06 — Variables explicatives sur la grille mondiale

Notebook : `notebooks/06_grille_mondiale.ipynb` → produit `data/grille_05deg.csv.gz` (64 745 cellules).

Numéroté 06 parce qu'un notebook `05_donnees_synthetiques` a été ajouté entre-temps, par une autre session de travail.

## Choix
| Choix | Décision | Raison |
|---|---|---|
| Grille | régulière, 0.5° × 0.5°, de 90° N à 60° S (Antarctique exclu) | résolution habituelle d'ORCHIDEE ; **grille exacte à confirmer avec B. Guenet** |
| Sources | ERA5-Land 1995–2024 (via Earth Engine), SoilGrids 2.0 à 5 km, RESOLVE 2017 | les mêmes qu'à l'entraînement |
| Agrégation | moyenne sur la cellule (ERA5-Land 0.1° → 0.5° ; SoilGrids 5 km reprojeté en moyenne) | valeur représentative de la maille ORCHIDEE |
| Végétation | biome du polygone contenant le centre de la cellule ; pour les cellules côtières dont le centre est en mer, polygone touchant la cellule | sans cela, ≈ 7 400 cellules côtières (11 %) étaient perdues, dont 6 de nos sites |
| Cellules gardées | toutes les variables disponibles ; glaces et lacs (biome « N/A ») écartés | — |

## Validation aux sites (changement d'échelle ≈ 15 km → ≈ 55 km)
- Les 131 sites ont une cellule complète.
- Corrélations entre valeur du site et valeur de sa cellule : de 0.92 (`SWC_mean`) à 0.99 (MAT, pH) ; écarts médians quasi nuls (argile et sable : ± 0.3 point de %).
- 95 % des sites ont la même classe de végétation que leur cellule.
→ Un modèle entraîné sur les sites peut être appliqué à la grille.

## Points techniques
- Earth Engine : le composite mensuel perd la projection d'ERA5-Land, qu'il faut réattribuer (`setDefaultProjection`) avant d'agréger. Les cellules sans terre émergée reviennent à 0 : elles sont marquées par une valeur sentinelle (−9999), puis mises à vide.
- Temps d'exécution : ≈ 2 min (3 requêtes Earth Engine de ≈ 40 s).
