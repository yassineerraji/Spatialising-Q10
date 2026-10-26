# 01 — Analyse exploratoire

Notebook : `notebooks/01_EDA.ipynb`.

## Partie A — Sites aux variables identiques mais aux Q10 différents

### Observation
- 63 lignes sur 173 (21 sites) ont exactement les mêmes variables explicatives qu'au moins une autre ligne, car elles ont été mesurées **au même point GPS** : parcelles, peuplements ou publications différentes sur une même station.
- Leurs Q10 diffèrent pour des raisons locales (essence, âge du peuplement, peuplement pur ou mélangé…) que des cartes mondiales ne peuvent pas voir. Exemple : `mgrsd_7587`, 4 peuplements au même point, Q10 de 2.77 à 3.72.
- Pour un modèle, c'est une même entrée associée à plusieurs réponses : le mieux qu'il puisse faire est de prédire leur moyenne.

### Conséquences
1. **Plancher d'erreur** : l'écart-type intra-site est d'environ 0.45, contre 0.96 au total. Même un modèle parfait n'expliquerait donc qu'environ 78 % de la variance de Q10. C'est un ordre de grandeur seulement (estimé sur 21 sites).
2. **Validation croisée** : un découpage aléatoire est trop optimiste. Avec une forêt aléatoire, le RMSE vaut ≈ 0.90 en découpage aléatoire, contre ≈ 0.93 en découpage groupé par site. Il faut donc toujours grouper, au minimum par site.

### Décision : agréger par site (validée)

→ `data/dataset_v2.csv` (131 sites), créé dans `00_preparation_donnees.ipynb`, étape 4. Options qui avaient été comparées :

| Option | Avantage | Inconvénient |
|---|---|---|
| A. Garder séparées (173 lignes) | aucune information perdue | un site à 9 parcelles (`mgrsd_4155`) pèse 9 fois plus qu'un site isolé, à l'entraînement comme à l'évaluation |
| B. Agréger par site, Q10 moyen (131 lignes) | 1 ligne = 1 lieu, comme sur la carte finale ; chaque lieu pèse autant ; cible moins bruitée | moins de lignes (le nombre de mesures par site peut être gardé en colonne) |

**Option retenue : B.** Notre livrable est une carte, donc une valeur par lieu, et l'option B évalue exactement cela. La validation croisée reste groupée par zone géographique, car des sites voisins se ressemblent aussi.

### Suite de l'EDA (sur `dataset_v2.csv`)
- Partie B : distributions de Q10 et des variables, carte des sites.
- Partie C : relations entre Q10 et les variables, corrélations entre variables.
- Ensuite, un notebook dédié pour reproduire la régression de Hacopian dans notre protocole de validation croisée.
