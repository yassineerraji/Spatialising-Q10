# 02 — Sélection des variables

Notebook : `notebooks/02_selection_variables.ipynb` (données : `data/dataset_v2.csv`, 131 sites).

## Partie A — Screening naïf

### Critères pour entrer dans X
1. **Disponible partout** (carte mondiale), sinon pas de carte de Q10 pour ORCHIDEE.
2. **Plausible physiquement** : un moteur de Q10, pas un artefact de l'échantillonnage.
3. **Exploitable** : pas de manquants, non constante, non redondante (seuil |r| = 0.8).

### Décisions
| Colonne | Décision | Raison |
|---|---|---|
| `site`, `study`, `source`, `n_mesures` | exclues | pas de carte mondiale (`n_mesures` pourra servir de poids) |
| `Q10` | cible | — |
| `lat`, `lon` | **candidats** (décision de l'équipe) | effet indirect mais probablement réel : elles peuvent porter des informations qu'aucune autre variable ne mesure |
| `MAT_public`, `MAP_public`, `pH_public`, `N515` | **candidats** | disponibles partout, aucun manquant, pas de redondance |

### Points de vigilance sur `lat` / `lon`
- Sites très concentrés : 99 % au Nord, 58 % en Asie de l'Est, aucun en Afrique ni en Amérique du Sud. La validation croisée devra être groupée par zone, sinon l'apport des coordonnées sera surestimé.
- Avec les 6 candidats, `lon` obtient le plus fort coefficient (+0.30). Elle sépare surtout l'Asie de l'Est (Q10 moyen 2.67) du reste (2.28). Est-ce un vrai signal régional ou un effet d'échantillonnage (méthodes de mesure propres à certaines études) ? La validation croisée spatiale le dira.
- Sur la carte mondiale, les prédictions dans les zones sans site seront à interpréter avec prudence. Et la part de la prédiction portée par les coordonnées restera figée si le climat change.

### Autres points notables
- Liens avec Q10 faibles : MAT −0.30 et N515 +0.35 (Spearman) ; MAP, pH et `lat` ≈ 0 pris isolément.
- Les coefficients changent fortement selon les variables présentes. MAP vaut 0 seul, +0.12 avec MAT et −0.05 avec les 6 candidats. **On ne peut donc trancher ni variable par variable, ni sur un lien pris isolément** : la décision viendra du LASSO et de la validation croisée spatiale (partie B).
- MAP et N515 sont asymétriques (asymétrie 1.0 et 1.4) : un passage au log est à tester pour les modèles linéaires.

## Premières conséquences pour le choix des modèles
- **Peu de données** : 131 sites pour une dizaine de candidats après enrichissement. C'est correct pour un modèle linéaire régularisé, mais juste pour des modèles flexibles (forêts, boosting, réseaux) qui risquent de sur-apprendre.
- **Signal faible** : les liens sont faibles et il existe un plancher d'erreur (≈ 0.45, cf. 01_EDA). Il faut s'attendre à des gains modestes, ce qui favorise les modèles simples et régularisés.
- **Extrapolation** : nos sites couvrent MAT de −5 à 25 °C et MAP de 230 à 3400 mm. Or la carte mondiale contient des conditions jamais vues : déserts chauds, Sibérie très froide, tropiques très humides. Hors de ce domaine, un modèle à arbres prédit une constante, et un modèle linéaire prolonge sa droite, parfois vers des valeurs absurdes. Le comportement hors domaine compte donc autant que le score en validation croisée.
- **Première liste de modèles à discuter** : régression linéaire régularisée (Ridge, LASSO), modèle additif à splines peu flexibles (GAM), processus gaussien, et une forêt aléatoire comme point de comparaison.

## Enrichissement (décision de l'équipe : avant le LASSO)
Fait dans `03_enrichissement_donnees.ipynb` → `data/dataset_v3.csv`. Voir `AgentDiscussion/03_enrichissement_donnees.md`.

## Partie B — Sélection rigoureuse (à venir)
Sur `dataset_v3.csv`, avec 10 candidats : `lat`, `lon`, `MAT_public`, `MAP_public`, `pH_public`, `N515`, `clay`, `sand`, `CN`, `biome`.
