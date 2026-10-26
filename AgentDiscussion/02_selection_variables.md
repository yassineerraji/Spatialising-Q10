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

## Partie B — Sélection rigoureuse
Sur `dataset_v3.csv`, avec 12 candidats : `lat`, `lon`, `MAT_public`, `MAP_public`, `pH_public`, `N515`, `clay`, `sand`, `CN`, `SWC_mean`, `SWC_warm_rel`, `biome`.

### Étape 1 — Biomes représentés par un seul site
Critères de décision : proximité environnementale, cohérence écologique, validation croisée. **Jamais Q10** : on ne choisit pas une variable explicative d'après la cible.

| Biome rare | Proposé au départ | Verdict | Chiffres clés |
|---|---|---|---|
| Forêts tropicales de conifères (Inde, « Himalayan subtropical pine forests ») | forêts tropicales humides | **confirmé** | distance 1.28 (suivant : 2.16) ; 0.60 sur le climat |
| Déserts (Arizona, « Chihuahuan desert », prairie semi-aride à mousson d'été) | méditerranéen | **rejeté** → prairies, savanes et matorrals tempérés | distance 2.41 contre 3.32 pour le méditerranéen ; climat 1.62 contre 2.82 ; `SWC_warm_rel` 0.98 contre 0.61 en méditerranéen (pas d'été sec) |

- La validation croisée ne tranche pas : écart de −0.003 entre les deux options, pour un bruit de 0.008.
- Le biome en one-hot **dégrade** légèrement le Ridge (0.961–0.964 contre 0.953 sans biome ; la moyenne seule fait 0.984).
- **Carte mondiale** : les déserts couvrent 20 % des terres (1 site) ; 27 % des terres sont dans des biomes sans aucun site (savanes tropicales, toundra, forêts tropicales sèches, prairies inondables, mangroves). Au total, 47 % des terres sont dans des biomes représentés par un site ou moins.
- **Décision (validée par l'équipe)** : conifères tropicaux → forêts tropicales humides ; déserts → prairies, savanes et matorrals tempérés.

### Étape 2 — Protocole de validation croisée spatiale (pour toute la suite)
- Semi-variogramme de Q10 : semi-variance faible sous 50 km (0.43), le plus souvent 0.5–0.8 jusqu'à ≈ 1 500 km, palier (≈ 1.0) au-delà. Des sites à moins de ≈ 1 000–1 500 km se ressemblent encore un peu. La courbe est bruitée.
- **Protocole** : zones de 10° × 10° (37 zones, la plus grosse = 15 sites), `GroupKFold` à 5 plis, répété 20 fois. Les conclusions sont vérifiées avec des zones de 5°.

### Étape 3 — Encodage de la végétation
| Ridge (11 candidats numériques) + … | RMSE (zones de 10°) |
|---|---|
| rien (sans végétation) | **0.934** |
| B : typologie 3 classes | 0.955 |
| A : one-hot 7 biomes | 0.969 |
| *référence : moyenne* | *0.980* |
| *référence : Q10 = 2.0* | *1.083* |

- **B fait mieux que A** (mieux dans 63 % des plis ; même classement avec des zones de 5°).
- **Aucun encodage n'aide** : la végétation dégrade le Ridge (B : +0.021, A : +0.035).
- **Pourquoi ?** Le biome décrit la végétation **régionale potentielle**, pas celle de la parcelle : des plantations de mélèzes et de pins (`7587_CN-SFC`) sont classées en prairie, des pinèdes du sud-est des États-Unis en « savanes ». La classe « végétation ouverte » mélange vraies prairies et forêts. Le climat et le sol ne la reconnaissent que pour 4 sites sur 13.
- **En passant** : le Ridge sans végétation fait 14 % d'erreur en moins que Q10 = 2.0 en validation croisée spatiale, mais la moyenne seule en fait déjà 9.5 % de moins : l'avance sur 2.0 vient surtout du niveau moyen de Q10.
- **Décision proposée (à valider)** : garder la typologie B comme seule variable de végétation candidate pour le LASSO ; abandonner le one-hot des biomes.
- **Piste** : remplacer le biome par une carte d'**occupation du sol réelle** (par exemple MODIS Land Cover via Earth Engine), plus fidèle à la végétation du site et plus proche des PFT d'ORCHIDEE.

- **Décision (validée)** : typologie en 3 classes comme variable de végétation candidate.

### Étape 4 — Table de modélisation `dataset_v4.csv`
Choix validés par l'équipe : cible **log(Q10)** (erreurs mesurées sur Q10), protocole spatial conservé, règle de choix d'un écart-type. Choix proposés par moi et non contestés : log de MAP et N515, pas de pondération, valeurs extrêmes gardées, métriques RMSE / MAE / R² / gain vs la valeur fixe (2.0 depuis la mise à jour d'`INSTRUCTIONS.md`), référence Hacopian en deux versions.

### Étape 5 — Contrôles avant modélisation
- **Retour à l'échelle de Q10** : la correction de Duan ne gagne que 0.003 (0.953 → 0.950), et prédire Q10 directement donne 0.952. → simple exponentielle.
- **Biais de source** : le Q10 plus élevé de `mgrsd` (médiane 2.74) s'explique par l'environnement (écart restant +0.02) ; les écarts entre sources ne sont pas significatifs (p = 0.35). → toutes les sources sont gardées.

## Partie C — Sélection rigoureuse (LASSO, 100 plis spatiaux)
- **La règle d'un écart-type ne convient pas** : dans 66 % des plis, elle ne retient aucune variable, et fait moins bien que la moyenne (0.990 contre 0.980). → **changement proposé** : pénalité minimale.
- **Noyau stable** avec la pénalité minimale (fréquence de sélection, signe) : `logN515` 99 % (+), `SWC_warm_rel` 97 % (+), `lon` 96 % (+), `MAT` 80 % (−), `végétation ouverte` 70 % (+). Ensuite : `lat` 27 %, `logMAP` 21 %, `forêts tropicales` 20 %, `CN` 16 %… **pH 5 %**.
- **Performance** : LASSO (pénalité minimale) 0.954 ≈ Ridge 0.953, soit ≈ 12 % de mieux que 2.0, dont ≈ 9.5 points obtenus par la simple moyenne ; **R² ≈ 0**.
- **Semi-variogramme des résidus ≈ celui de Q10** : la structure spatiale (≈ 1 000–1 500 km) n'est pas expliquée par nos variables. Les zones de 10° restent adaptées. Des modèles qui exploitent la proximité géographique pourraient en tirer parti près de nos sites, mais pas dans les régions sans mesure.
- Les variables rarement retenues restent dans la variante V1 de la comparaison des modèles (un modèle non linéaire peut les exploiter).

### Question ouverte (à garder en tête) — le biome a-t-il une valeur que nos tests ne voient pas ?
Inquiétude de l'équipe : le biome est peut-être un bon prédicteur, mais notre petit dataset, bruité et biaisé, masque sa valeur. Calculs exploratoires (pas encore dans un notebook) :
- **Écarts restants par biome** une fois le climat et le sol pris en compte (Ridge, validation croisée spatiale) : prairies de montagne +0.90 (5 sites), méditerranéen −0.78 (7 sites), conifères tempérés +0.26. Même sens que chez Hacopian, mais non significatif (p = 0.10).
- **Puissance du protocole** (simulation) : si le biome avait un vrai effet de cette taille, notre test ne le jugerait utile que dans 68 % des cas, pour un gain de +0.013 seulement. Un effet deux fois plus fort serait détecté à 100 %. → « Le biome n'aide pas » ne veut pas dire « le biome n'a pas d'effet » ; on exclut seulement un effet fort.
- **Erreurs les plus fortes** en boréal (1.5) et en montagne (1.8), les biomes clés pour le carbone du permafrost. L'erreur moyenne est dominée par les forêts tempérées (71 sites sur 131).
- **Limites du biome pour la carte** : 47 % des terres sont dans des biomes avec un site ou moins ; une variable catégorielle crée des sauts de Q10 aux frontières ; ORCHIDEE raisonne en PFT (végétation réelle), pas en biomes.
- **Pistes** : modèle hiérarchique (effet aléatoire par classe de végétation) ; garder deux variantes (avec et sans végétation) jusqu'à la comparaison des cartes ; demander à B. Guenet son avis d'expert, et si le carbone du sol d'ORCHIDEE est suivi par PFT (ce qui permettrait un Q10 par PFT).
