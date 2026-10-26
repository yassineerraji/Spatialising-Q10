Tout au long de ce projet de recherche, tu seras mon partenaire et devras IMPÉRATIVEMENT respecter les règles suivantes :

1. NOUS DEVONS CODER DE LA MANIÈRE LA PLUS SIMPLE POSSIBLE.

Par « simple », nous entendons :

Une cellule Python ne doit effectuer qu'une seule tâche à la fois.
Nous privilégions toujours un code minimaliste : ce qui peut être réalisé en deux lignes de code doit l'être en deux lignes, systématiquement.
Nous privilégions la simplicité et l'exactitude plutôt que la complexité ou un code trop long, difficile à appréhender visuellement.
Chaque cellule Python doit comporter, au début, des commentaires expliquant l'opération effectuée.
Les étapes codées doivent s'appuyer sur les précédentes.


2. Toute hypothèse ou décision prise ne doit jamais rester implicite; elle doit être formalisée dans des cellules Markdown concises qui contiennent tous les élements de raisonnement qui ont mené à une décision.
Ces cellules Markdown doivent suivre une structure claire et cohérente tout au long de chaque notebook.

3. Dans le dossier « context », tu trouveras :

- Un fichier `context.md` qui présente, de manière concise, l'objectif final de notre projet.
- La description initiale du projet de recherche, validée par le superviseur et mon établissement. Considérez ce document comme une base de travail, et non comme une vérité absolue.
- L'article de recherche à l'origine de ce travail ; il constitue une référence et un point de comparaison pertinent pour les travaux que nous allons mener.


4. Le workflow que nous suivrons sera le suivant :

Pour chaque grande problématique du projet sur laquelle nous travaillerons, on créera un notebook (dans le dossier `notebooks/`) qui contiendra le code associé, l'objectif étant de maintenir une codebase claire, lisible et structurée.
Les grandes problématiques peuvent concerner la séléction de variables par LASSO, la recherche sur des méthodes de génération de données synthétiques, l'identification et test de modèles de machine learning potentiellement adaptés etc...

1. Nous procéderons étape par étape, plutôt que de tenter de réaliser l'intégralité du sous-projet en une seule fois.

Tu exposeras, de façon très concise, tes réflexions, hypothèses et raisonnements dans un dossier nommé « AgentDiscussion ». Pour chaque partie du projet, tu y ajouteras un fichier Markdown dédié.
J'examinerai attentivement ces fichiers Markdown et, le cas échéant, j'y apporterai des modifications.
Tu prendras en compte la version la plus récente de ces cellules Markdown pour poursuivre le développement.

Une fois le codage terminé, tu rédigeras un fichier Markdown récapitulatif dans ce même dossier « AgentDiscussion ».


5. Précisions sur le projet :

- **Données** : `data/dataset.csv` est un dataset enrichi construit par notre équipe. Il contient le dataset public de Hacopian, complété par d'autres mesures de Q10 (bibliothèque privée du CNRS, recherche en ligne, etc.). Ses métadonnées sont incomplètes : le fichier original n'est jamais modifié, et on crée dans `data/` de nouvelles versions qui ne gardent que ce qui est clair et utile (décrites dans `data/README.md`).
- **Objectif « battre 2.2 »** : il s'agit de battre la valeur fixe 2.2 **au niveau mondial**, pas seulement sur nos sites. Sur notre dataset, même une simple constante (la moyenne) bat 2.2 : ce résultat ne prouve donc rien. Toute la difficulté est de **généraliser à toute la planète à partir de peu de données**. Chaque modèle doit être jugé sur sa capacité à prédire des sites et des régions qu'il n'a jamais vus.
- **Évaluation** : validation croisée groupée (des mesures d'un même site ou d'une même zone ne sont jamais à la fois en entraînement et en test). Métriques : RMSE et R². Chaque modèle est comparé à trois références : la constante 2.2, la moyenne d'entraînement et la régression linéaire de Hacopian (MAT + MAP + pH).
- **Langue** : les notebooks et les fichiers « AgentDiscussion » sont rédigés en français.