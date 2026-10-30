# 07 — Niveau de confiance et valeur de repli

Notebook : `notebooks/07_confiance_repli.ipynb` (données : `data/dataset_v4.csv`, `data/grille_05deg.csv.gz` ; prédictions en cache de 04 ; cache propre : `resultats/07/`). **Premier jet, à relire.**

## Question
Construire une carte qui n'utilise le modèle **que là où nos données le justifient**, et qui revient ailleurs à **Q10 = 2.0**, la valeur actuelle d'ORCHIDEE (décision de l'équipe).

Exigence de l'équipe : **aucune valeur fixée sans recherche sur grille**, avec des graphiques qui montrent qu'elle est optimale dans notre contexte. Elle doit aussi être justifiée par l'objectif final : la carte pour ORCHIDEE, avec des données appelées à augmenter un peu.

## Règle étudiée
- **Confiance** $c(x)$, calculée à partir de $n_r(x)$, le nombre de sites à moins de $r$ km :
  - **seuil** : $c = 1$ si $n_r \geq n^*$, sinon $c = 0$ ;
  - **mélange** : $c = \min\big(1,\ n_r/n^*\big)$.
- **Prédiction** : $\log Q_{10} = c\,\log \hat{f} + (1 - c)\,\log 2.0$, avec $\hat{f}$ l'Elastic Net V2 bridé.

| Fixé (et pourquoi) | Choisi par les données |
|---|---|
| repli 2.0 (décision de l'équipe) ; modèle Elastic Net V2 bridé (proposition de 04, non validée ; robustesse vérifiée) ; protocole commun | $r$, $n^*$, la forme, et la perte qui sert à les choisir |

## Méthode
- **Pas de fuite** : la confiance d'un site de test n'est calculée qu'avec les sites d'entraînement de son pli.
- **Grille** :
  - $r$ de 100 à 3 000 km, par pas de 100 km ;
  - $n^*$ de 1 à 30 ;
  - 2 formes (seuil, mélange) ;
  - 2 pertes, soit 3 600 règles × 100 plis.
- **Deux pertes**, selon la valeur de repli utilisée pendant l'évaluation :
  - **repli sur 2.0** : la règle telle qu'elle sera livrée ;
  - **repli sur la moyenne d'entraînement** : une constante de même niveau que le modèle, qui ne récompense que l'information locale.
- **Robustesse de l'optimum** :
  - optimum de chacune des 20 répétitions ;
  - optimum pour chacune des 17 configurations de 04 ;
  - sous-échantillons de 60 à 90 % des sites, avec le modèle réentraîné ;
  - validation croisée imbriquée, avec le réglage choisi dans chaque pli (5 plis × 4 répétitions internes).
- **Critères propres à ORCHIDEE** : sauts de Q10 au bord des cercles ; changement de la carte quand on retire un site.

## Résultats
| Question | Résultat |
|---|---|
| Le gain dépend-il des voisins ? ($r = 1\,000$ km, illustration) | 0 voisin : −0.8 % contre 2.0, −10.8 % contre la moyenne. **À partir de 2 voisins**, gain sur les deux références (+4 à +12 % contre la moyenne). À 500 km ou 2 000 km, les classes de voisins ne séparent plus les sites isolés des autres. |
| Optimum des 4 surfaces | (1 400, 3), (1 100, 3) avec repli 2.0 ; (1 000, 2), (1 000, 3) avec repli moyenne. Jamais sur un bord de la grille. |
| Netteté de l'optimum | 103 à 455 règles sur 900 restent à moins d'une erreur standard de l'optimum : **l'emplacement est solide, la marge ne l'est pas**. |
| Stabilité (repli moyenne, mélange) | Écart interquartile entre répétitions : 100 km et 0.25 ; **9 configurations sur 17** donnent ($r$ de 900 à 1 100 km, $n^* = 3$). Avec repli 2.0 : dispersion de 500 à 900 km. |
| Seuil contre mélange (validation croisée) | −0.003 ± 0.013 : indiscernables. |
| Sauts au bord des cercles | médiane 0.15 (mélange) contre 0.36 (seuil) ; 90e centile 0.44 contre 1.17. |
| Retrait d'un site (changement maximal de la carte) | 90e centile 0.59 (mélange) contre 1.32 (seuil) ; maximum 0.84 contre 1.97. |
| **Règle retenue** | **mélange, $r = 1\,000$ km, $n^* = 3$** ; $r$ égal à la portée du semi-variogramme (02), trouvé sans être imposé. |
| Quantité de données | même optimum avec 80 % et 90 % des sites ; instable sous ≈ 100 sites. |
| Validation croisée imbriquée (livrée : choix « moyenne », repli 2.0) | **0.979** : −0.104 ± 0.043 contre 2.0 ; **+0.029 ± 0.035 contre le modèle seul** ; −0.001 ± 0.050 contre la moyenne. |
| Idem, choix avec la perte « 2.0 » | 0.953 (+0.004 ± 0.019 contre le modèle seul), mais réglages instables (écart interquartile de 825 km), souvent $r = 1\,600$ km avec $n^* = 1$ ou 2. |
| Carte | $c = 1$ : 20 % des terres ; $0 < c < 1$ : 9.7 % ; $c = 0$ (2.0) : 70.3 %. Q10 moyen : 2.08 (modèle seul : 2.16). Régions froides : 2.1 (modèle seul : 3.4). |
| Aire d'applicabilité | 4 % seulement des cas de test sont hors de l'aire de leur pli : la validation croisée ne peut pas trancher. 5.8 % des terres ont $c > 0$ hors de l'aire (Tibet, nord du Canada et de la Scandinavie, etc.). |

## Lecture
- **La méthode ne rend pas la carte meilleure sur nos sites.** Son rôle est d'éviter d'extrapoler là où le modèle n'a pas d'information locale. Notre partie A montre que, sans voisin, le modèle ne fait pas mieux que 2.0.
- **Le prix de cette prudence, mesuré sur nos sites, est d'environ 0.03 de RMSE**, sous une erreur standard. Il vient entièrement de l'écart entre 2.0 et le niveau de nos sites (2.51). Le bénéfice, lui, est hors de portée de la validation croisée, puisque nos sites ne couvrent pas les régions où la règle revient à 2.0.
- **Pourquoi la perte « repli sur la moyenne »** :
  - elle mesure exactement ce que la confiance doit dire ;
  - son optimum est stable et ne dépend pas du modèle ;
  - la perte « repli sur 2.0 » récompense le niveau de nos sites, et pousse à étendre le modèle plus loin de ces sites.

## Décisions à valider
1. **La perte de sélection « repli sur la moyenne »**, avec son coût d'environ 0.03 sur nos sites. L'alternative est la perte « repli sur 2.0 » : +0.004 sur nos sites, mais des réglages instables et plus larges.
2. **Le mélange** plutôt que le seuil.
3. **L'aire d'applicabilité** : mettre $c = 0$ hors de l'aire ? Cela touche 5.8 % des terres. Ce n'est pas appliqué dans ce premier jet.
4. **Les régions froides passent à 2.0** (2.1 en moyenne), alors que tous les modèles y prédisent plus de 2.8 : à discuter avec B. Guenet.

## Limites et pistes
- Tous les sites comptent autant, qu'ils soient à 50 ou à 990 km. Des sites très proches d'une même étude comptent plusieurs fois, et c'est là que se produisent les plus grands sauts. Deux pistes : une pondération par la distance (un paramètre de plus) ; compter les études plutôt que les sites.
- Si de nouveaux sites changent la géographie des données (par exemple beaucoup de sites tropicaux), il faudra refaire la recherche sur grille.

## Points techniques
- **Durée d'exécution** : ≈ 30 s avec le cache, ≈ 15 min sans (3 000 ajustements de l'Elastic Net V2 bridé).
- **Origine du cache `resultats/07/`** (100 fichiers pour la validation croisée imbriquée, 20 pour les sous-échantillons) : il a été produit par un script séparé, avec les mêmes fonctions et les mêmes graines. Deux fichiers ont été recalculés par le code du notebook, avec un résultat identique (écart nul).
- **Calcul de la grille** : vectorisé sur $n^*$ (`rmse_pli` renvoie les 30 valeurs d'un coup).
- **`distance_km`** est défini dans le notebook, comme dans `presentation/figures.py`. À déplacer dans `src/` s'il sert à l'export NetCDF.
