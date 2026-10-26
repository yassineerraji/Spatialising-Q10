# 05 — Données synthétiques par copules

Notebook : `notebooks/05_donnees_synthetiques.ipynb` (données : `data/dataset_v4.csv` ; protocole : `src/protocole.py`). Référence de méthode : Haugh (2016), `context/An Introduction to Copulas.pdf`.

## Question
Des sites synthétiques tirés d'une copule aident-ils à prédire Q10 dans des régions sans mesure ?

**Attente théorique, posée avant l'expérience :** un générateur ajusté sur nos sites n'en sait pas plus qu'eux. Les sites synthétiques ne peuvent donc pas apporter d'information nouvelle ; au mieux, ils ont un effet de régularisation.

## Choix de méthode
| Choix | Décision | Raison |
|---|---|---|
| Copule | gaussienne | la plus simple pour 12 variables aux dépendances de signes et d'intensités variés ; les copules archimédiennes imposent la même dépendance à toutes les paires |
| Marginales | empiriques : pseudo-observations rang / (n + 1), retour par quantiles empiriques | aucune hypothèse de forme ; contrepartie : aucune valeur synthétique hors de l'intervalle observé |
| Estimation de P | corrélation des scores normaux Φ⁻¹(u) (pseudo-maximum de vraisemblance, Haugh 4.2) | simple, et la matrice obtenue est toujours valide |
| Variables | 11 candidats numériques de la v4 + `log_Q10` | la typologie est catégorielle, et une copule décrit des variables continues ; le log ne change rien à la copule (invariance) |
| Pas de fuite | copule ajustée sur les seuls sites d'entraînement de chaque pli | sinon, l'information des sites de test passe dans l'entraînement |
| Évaluation | protocole commun (`src/protocole.py`) et références du notebook 04 | comparabilité avec la comparaison des modèles |

## Résultats
**Fidélité :**
- Les marginales sont reproduites par construction.
- Le tau de Kendall respecte la relation τ = (2/π)·arcsin(P) : écart moyen 0.03, pour un bruit d'échantillonnage de 0.06. La copule gaussienne est donc plausible paire par paire, avec une légère atténuation des dépendances fortes.
- **Test du classifieur :** une forêt distingue les sites synthétiques des vrais avec une AUC de 0.69, contre 0.86 pour la copule d'indépendance. La dépendance est donc en bonne partie captée, mais pas entièrement.
- **Géographie irréaliste :** chaque bande de longitude est remplie de 20 à 65°N (sites « au Sahara », dans le nord du Canada). Ces sites n'ont pas pour autant de climats nouveaux : leurs valeurs sont recombinées à partir des nôtres.

**Utilité** (validation croisée spatiale ; écart avec le même modèle sur les vrais sites, ± erreur standard de Nadeau-Bengio) :

| Variante | RMSE | Écart | Gain vs 2.0 |
|---|---|---|---|
| *Q10 = 2.0 (valeur fixe)* | *1.083* | — | — |
| *moyenne* | *0.980* | — | *9.5 %* |
| Hacopian réentraîné (référence) | 0.963 | — | 11.1 % |
| **Ridge, réels** | **0.933** | — | **13.8 %** |
| Ridge, réels + 131 synth. | 0.954 | +0.021 ± 0.023 | 11.9 % |
| Ridge, réels + 1000 synth. | 0.973 | **+0.040 ± 0.028** | 10.2 % |
| forêt, réels | 1.000 | — | 7.7 % |
| forêt, réels + 131 synth. | 0.988 | −0.012 ± 0.030 | 8.8 % |
| forêt, réels + 1000 synth. | 0.971 | −0.029 ± 0.037 | 10.4 % |

Référence : valeur fixe **2.0** (`INSTRUCTIONS.md`, constante `Q10_REFERENCE` de `src/protocole.py`). Les gains étaient auparavant exprimés par rapport à 2.2 ; seuls la ligne de référence et la colonne de gain ont changé, tous les RMSE sont identiques.

- **Pourquoi le Ridge se dégrade :** `RidgeCV` est trompé par les sites synthétiques. La pénalité par site α / n passe de 0.474 à 0.037, soit une régularisation 13 fois plus faible.
- **À pénalité par site égale :** l'effet disparaît (+0.004 ± 0.012). Les sites synthétiques n'apportent aucune information.
- **Forêt :** le gain, non significatif, est une régularisation : la forêt, qui sur-apprend seule, apprend à la place la relation lisse de la copule.
- **Avec 1 000 synthétiques**, Ridge et forêt convergent vers la relation de la copule (≈ 0.97), entre la moyenne et Hacopian réentraîné.

## Partie D — Contre le sur-apprentissage, est-ce un succès ? Non.
Question de l'équipe : le seul but est d'empêcher le sur-apprentissage, en particulier dans les régions denses.

| Test | Résultat |
|---|---|
| Écart entre erreur de test et erreur d'entraînement (sur-apprentissage) | Ridge : 0.031 → **0.076** ; forêt : 0.566 → 0.585 (la forêt colle même un peu plus à ses sites) |
| Part de l'Asie de l'Est | 58 % des vrais sites, **56 %** des synthétiques : le déséquilibre est reproduit |
| Erreur sur les sites denses (≥ 15 voisins à moins de 1 000 km) | inchangée (+0.001 Ridge, −0.008 forêt) |
| Erreur sur les sites isolés | Ridge **+0.062** (moins bon dans 100 % des répétitions) ; forêt −0.044 (mieux dans 80 %) |
| Forêt : copule contre régularisation classique | 0.971, contre 0.962–0.990 pour `min_samples_leaf` de 5 à 40 et 0.980 pour la forêt réglée du projet : indiscernables (écarts sous une erreur standard) |
| Pondération par zone (alternative directe) | sans effet sur la forêt (1.003), nuisible au Ridge (+0.021 ± 0.020) |

- **Mécanisme :** les sites synthétiques tirent le modèle vers la relation de la copule, elle-même estimée sans pénalité sur nos sites. Le modèle s'améliore s'il fait moins bien que cette relation (forêt), il se dégrade sinon (Ridge). L'effet porte sur l'extrapolation (sites isolés), pas sur les régions denses.
- **Utilité précise :**
  - un peu, pour un modèle flexible peu régularisé, mais pas plus qu'une régularisation classique ;
  - nuisible pour un modèle déjà régularisé ;
  - risquée pour tout modèle réglé par validation interne (les 8 modèles de 04) ;
  - nulle pour les régions denses et pour les régions sans mesure ;
  - réelle pour les études de simulation.
- **Le vrai problème des régions peu mesurées** est un manque d'information, pas un sur-apprentissage des régions denses. Tous les modèles font ≈ 1.1–1.2 sur les sites isolés, contre ≈ 0.8 sur les sites denses, et ni la copule ni la pondération ne réduisent nettement cet écart.

## Conclusion et décision proposée (à valider)
- L'attente théorique est confirmée : l'augmentation par copule ne rapproche pas de l'objectif, et elle ne limite pas non plus le sur-apprentissage. **Proposition : ne pas l'utiliser dans la suite.** Pour les modèles de 04, s'appuyer sur leur régularisation native, réglée par validation croisée spatiale interne, comme prévu.
- **Autres méthodes de génération :** je n'ai pas de raison forte de penser qu'elles feraient mieux. La limite est l'information contenue dans 131 sites, pas la fidélité du générateur.
  - Une copule en vigne ou une copule de Student amélioreraient la fidélité, pas l'information.
  - Les GAN et les auto-encodeurs variationnels demandent des milliers d'exemples.
  - Bruiter les sites existants équivaut à une pénalité Ridge (Bishop, 1995).
- **Usage des copules qui reste pertinent : un laboratoire de simulation.** On peut générer des données réalistes avec une relation connue, pour tester si le LASSO et la validation croisée spatiale la retrouvent. Cela rendrait reproductible la simulation de puissance de 02, aujourd'hui faite hors notebook.

## Points d'attention
- **Pour le notebook 04 :** le Ridge sur les 11 candidats numériques, sans la typologie, fait 0.933, contre ≈ 0.953 pour le Ridge de 02 (partie C) avec la typologie. C'est cohérent avec 02 (partie B, étape 3), où la végétation dégradait le Ridge. Écart à confirmer par une comparaison appariée dans 04 (variantes V1 / V2).
- Le contrôle à pénalité égale utilise un α choisi sur les 131 sites, sites de test compris. La comparaison entre ses deux variantes reste juste, mais ses scores ne sont pas des scores finaux.
- Les R² restent proches de 0 (0.04 pour le meilleur modèle) : battre 2.0 ne veut pas encore dire bien prédire. La simple moyenne de nos sites bat déjà 2.0 de 9.5 %.
