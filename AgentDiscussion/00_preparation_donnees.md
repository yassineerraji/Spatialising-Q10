# 00 — Préparation des données

Notebook : `notebooks/00_preparation_donnees.ipynb` → produit `data/dataset_v1.csv` et `data/dataset_v2.csv`.

## Contexte
Le dataset enrichi (`data/dataset.csv`, 173 lignes, 15 colonnes) a des métadonnées incomplètes. On crée des versions qui ne gardent que ce qui est clair et utile. Le fichier original n'est jamais modifié.

## Version 1 — colonnes claires et utiles
- **Gardé** : `site`, `source`, `study`, `Q10`, `lat`, `lon`, `MAT_public`, `MAP_public`, `pH_public`, `N515`.
- **Retiré** (origine ou sens inconnus) : `Ts_max`, `Ts_mean`, `SWC_warm_rel`, `new`, `cluster`.
- Critère : une variable explicative n'est utile que si on sait ce qu'elle mesure **et** qu'elle existe en carte mondiale (sinon, pas de carte possible pour ORCHIDEE).

## Version 2 — une ligne par site (décision validée)
- Agrégation des mesures d'un même point GPS : `Q10` = moyenne arithmétique, `n_mesures` = nombre de mesures agrégées, `site` / `source` / `study` concaténés.
- Résultat : 131 sites, 173 mesures, aucune perte. **Version de référence pour la suite.**
- Point d'attention : la moyenne arithmétique a été choisie pour sa simplicité. Une moyenne géométrique serait plus cohérente avec la définition de Q10 (exponentielle d'une pente), mais l'écart ne compte que pour les sites très dispersés. Le plus grand écart est 0.15, pour `paper_31` (3.25 contre 3.10).

## Origine des variables
- `MAT_public`, `MAP_public`, `pH_public` : mêmes sources que Hacopian, vérifiées dans son script R publié (`github.com/melaniehacopian/microbial_Q10_workflow`). MAT = température moyenne de l'air à 2 m (ERA5-Land), MAP = précipitations totales annuelles (ERA5-Land), pH = SoilGrids `phh2o`, 0–5 cm. L'équipe confirme que c'est très probablement le cas pour tout le dataset.
- `N515` : azote SoilGrids, 5–15 cm, en **mg/kg**. Vérifié dans `03_enrichissement_donnees.ipynb` : N515 vaut 10 fois l'azote SoilGrids (exprimé en cg/kg), avec une corrélation de 0.98. L'unité cg/kg indiquée au départ était fausse.
- Pour mémoire, le modèle publié par Hacopian (données publiques) est : Q10 = 0.1093 − 0.0315·MAT + 0.0002·MAP + 0.4112·pH.

## `SWC_warm_rel` : ce que l'on sait
- **Introuvable en ligne** : aucune source publique n'utilise ce nom, et il est absent du script de Hacopian. C'est probablement une variable calculée par l'équipe ou par une base intermédiaire.
- **Hypothèse déduite des valeurs** : humidité du sol pendant la saison chaude ÷ humidité moyenne annuelle. Indices :
  - valeurs centrées sur ≈ 0.95 (de 0.47 à 1.37), ce qui ressemble à un rapport et non à une humidité absolue ;
  - les plus basses (0.47–0.67) sont dans des climats à été sec (Oregon, Californie, Italie, Espagne, Provence) ;
  - les plus hautes (1.12–1.37) sont dans des climats à été humide (mousson du sud de la Chine, Floride) ;
  - corrélation faible avec MAP (≈ 0.2), peu compatible avec une humidité absolue.
- **Intérêt** : c'est la seule colonne retirée qui apporte une information nouvelle (corrélée à seulement 0.10 avec MAT, et à +0.20 avec Q10). `Ts_mean` est redondante avec MAT (corrélation 0.99).
- **Décision** : non réintégrée tant que sa définition exacte (produit, profondeur, mois « chauds ») est inconnue.
- **Option** : la recalculer nous-mêmes depuis ERA5-Land avec une définition explicite. Elle serait alors claire et disponible en carte mondiale.
