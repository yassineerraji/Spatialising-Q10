# Récapitulatif du projet

État au 26/10/2026. Le détail de chaque partie est dans le fichier AgentDiscussion correspondant et dans son notebook.

## 1. Cadrage et environnement
- **Objectif** : prédire Q10 à l'échelle mondiale pour ORCHIDEE, et faire mieux que la valeur fixe (**2.0** depuis la mise à jour d'`INSTRUCTIONS.md`).
- **Outils mis en place** : environnement `.venv`, accès Google Earth Engine (`crp-geosciences`), fonctions communes dans `src/protocole.py` et `src/modeles.py`.

## 2. Préparation des données (`00_preparation_donnees`)
- **Point de départ** : 173 mesures, venant de 6 sources (Hacopian, plus les ajouts de l'équipe).
- **v1** : on ne garde que les colonnes dont le sens est clair. 5 colonnes à l'origine inconnue sont retirées, dont `SWC_warm_rel` et `cluster`.
- **v2** : une ligne par site, avec Q10 moyenné, soit **131 sites**.

## 3. Analyse exploratoire (`01_EDA`)
- **Mesures multiples au même endroit** : 63 mesures, sur 21 sites, ont les mêmes variables mais des Q10 différents.
- **Plancher d'erreur** : ces écarts locaux valent environ 0.45, pour un écart-type total de 0.96. Au mieux, on peut expliquer environ 78 % de la variance de Q10.
- **Conséquence** : une validation croisée aléatoire est trop optimiste ; il faut grouper les plis.

## 4. Premier tri des variables (`02_selection_variables`, partie A)
- **Exclues** : les identifiants et les métadonnées. **Gardées** : lat et lon (décision de l'équipe).
- **Sites très concentrés** : 99 % dans l'hémisphère Nord, 58 % en Asie de l'Est, aucun en Afrique ni en Amérique du Sud.
- **On ne juge pas une variable seule** : un lien faible pris isolément ne suffit pas pour exclure, car l'effet de MAP est masqué par MAT.

## 5. Enrichissement (`03_enrichissement_donnees` → v3)
- **Nouvelles variables** :
  - **Sol** (SoilGrids) : argile, sable, carbone organique (SOC), rapport C:N ;
  - **Végétation** : biome RESOLVE ;
  - **Humidité du sol** (ERA5-Land, via Earth Engine) : `SWC_mean` et `SWC_warm_rel`.
- **Validations** : N515 est en mg/kg (corrélation 0.98) ; MAT et MAP viennent bien d'ERA5-Land 1995–2024 (corrélations supérieures à 0.99) ; la définition de `SWC_warm_rel` est retrouvée (0.98).
- **SOC est exclu**, car il varie presque comme N515 (corrélation 0.91).
- **Les sites méditerranéens** ont le Q10 le plus bas, et aussi l'été le plus sec.

## 6. Biomes, protocole d'évaluation, végétation (`02_selection_variables`, partie B)
- **Biomes à un seul site** : les conifères tropicaux sont rattachés aux forêts tropicales humides, les déserts aux prairies tempérées (et non au méditerranéen).
- **47 % des terres** sont dans des biomes représentés par un site ou moins.
- **Protocole d'évaluation** : des sites voisins se ressemblent jusqu'à environ 1 000 à 1 500 km. On évalue donc par zones de 10°, avec 5 plis répétés 20 fois.
- **Végétation** : la typologie en 3 classes fait mieux que les 7 biomes, mais aucune des deux n'améliore le modèle. Le biome décrit la végétation de la région, pas celle de la parcelle mesurée.
- **Limite du test** : il manquerait un effet du biome de taille réaliste une fois sur trois. « Pas d'amélioration » ne veut donc pas dire « pas d'effet ».
- **Table de modélisation v4** : cible log(Q10), log de MAP et de N515, typologie, zone. Aucun biais selon la source des mesures.

## 7. Sélection rigoureuse par LASSO (`02_selection_variables`, partie C)
- **La règle d'un écart-type ne convient pas** : elle ne retient aucune variable dans 66 % des plis. On utilise la pénalité minimale.
- **Noyau stable** : azote (+), humidité estivale (+), longitude (+), MAT (−), végétation ouverte (+). Le pH n'est retenu que dans 5 % des plis.
- **La ressemblance entre sites voisins n'est pas expliquée par nos variables.**

## 8. Références et comparaison des 8 modèles (`04_comparaison_modeles`, parties A et B)
- **Références** : Q10 = 2.0 fait 1.083 ; la moyenne 0.980 (−9.5 %) ; le modèle de Hacopian réentraîné 0.963 (−11.1 %).
- **L'équation publiée de Hacopian ne généralise pas** : sur les sites qu'elle n'a pas vus, elle fait moins bien que 2.0.
- **Règle de choix** : comparaison des modèles sur les mêmes plis, avec la correction de Nadeau et Bengio. Il faut un écart d'environ 0.03 pour qu'un modèle soit jugé meilleur.
- **Résultats** :
  - le meilleur est Elastic Net V1 (0.950) ;
  - **10 configurations sont équivalentes**, et la plus simple est **Elastic Net V2** (0.956, −11.7 % par rapport à 2.0) ;
  - le boosting, CatBoost et le GP font moins bien que la simple moyenne ;
  - **la sélection LASSO en amont aide ou est neutre pour tous les modèles.**
- **R²** (`04_comparaison_modeles`, partie D) : le R² d'ajustement va de 0.15 à 0.21 pour les modèles retenus et jusqu'à 0.88 pour les plus flexibles, qui sur-apprennent. En régions nouvelles (validation croisée spatiale), il vaut au mieux 0.013. Plus un modèle explique ses propres sites, moins il prédit bien ailleurs.

## 9. Données synthétiques par copules (`05_donnees_synthetiques`, autre session)
- Elles n'apportent aucune information nouvelle : elles dégradent le Ridge et ne font que régulariser la forêt. **Recommandation : ne pas les utiliser.**

## 10. Grille mondiale (`06_grille_mondiale`)
- **64 745 cellules de 0.5°**, avec les mêmes sources et définitions qu'à l'entraînement. Les valeurs concordent avec celles des sites (corrélations de 0.92 à 0.99).
- Une perte de 11 % des cellules côtières a été corrigée.

## 11. Comportement hors du domaine des données (`04_comparaison_modeles`, partie C)
- **Aire d'applicabilité** : 36 % des terres. Le modèle extrapole sur les 64 % restants.
- **Dans cette aire, les modèles s'accordent** (Q10 ≈ 2.4). **En dehors, ils divergent**, surtout dans les régions froides : 3.4 pour l'Elastic Net, contre 2.9 pour le BART.
- **Le Q10 moyen mondial prédit est de 2.1 à 2.2.** L'apport d'une carte tient donc surtout à la répartition spatiale de Q10.
- **Un artefact au Sahara** (Q10 jusqu'à 6.4), dû à `SWC_warm_rel`, est supprimé en bridant chaque variable à la plage de nos sites. Le bridage améliore même légèrement la validation croisée (0.950).

## 12. Niveau de confiance et valeur de repli (`07_confiance_repli`, premier jet du 30/10/2026)
- **Règle** : le modèle est utilisé là où des sites sont proches, et la carte revient à **2.0** (valeur actuelle d'ORCHIDEE, décision de l'équipe) ailleurs. Formule : $c = \min\big(1,\ n_{1000}/3\big)$, puis $\log Q_{10} = c\,\log \hat{f} + (1 - c)\,\log 2.0$.
- **Chaque valeur vient d'une recherche sur grille** ($r$ de 100 à 3 000 km, $n^*$ de 1 à 30, seuil ou mélange), suivie de tests de robustesse : répétitions, 17 configurations, sous-échantillons, validation croisée imbriquée. Le rayon trouvé (1 000 km) est la portée du semi-variogramme.
- **Le mélange** est indiscernable du seuil en validation croisée, mais il crée des sauts deux fois plus petits et il est deux fois moins sensible à l'ajout d'un site.
- **Sur nos sites, la règle bat 2.0 de 0.10**, mais fait un peu moins bien que le modèle seul (+0.03, sous une erreur standard) : c'est le prix du repli sur 2.0, plus bas que le niveau de nos sites.
- **Carte** : modèle sur 20 % des terres, mélange sur 10 %, 2.0 sur 70 % ; Q10 moyen 2.08 ; régions froides ramenées à 2.1.

## Ce qu'on a appris
1. **Les données sont le facteur limitant** : peu de sites, très concentrés géographiquement, et un R² proche de 0 dans des régions nouvelles.
2. **Battre 2.0 est facile, mais surtout grâce au niveau moyen.** Les variables n'ajoutent qu'environ 2.5 points, ce qui ne se distingue ni de la moyenne ni du modèle de Hacopian réentraîné.
3. **Les modèles simples gagnent.** La complexité n'apporte rien avec 131 sites.
4. **Les signaux robustes** sont l'azote, la sécheresse estivale, MAT, l'effet Asie de l'Est et la végétation ouverte. Le pH n'en fait pas partie.
5. **L'incertitude de la carte vient surtout de l'extrapolation**, et elle est maximale dans les régions froides, les plus importantes pour le permafrost.

## Ce qui reste à décider ou à faire
- **Valider les 3 propositions de la partie C** : Elastic Net V2 avec bridage, carte livrée avec son aire d'applicabilité, et carte BART comme variante de sensibilité.
- **Harmoniser `context/context.md`**, qui dit toujours 2.2.
- **Questions pour B. Guenet** : grille et format ; Q10 fixe ou fonction du climat ; Q10 par type de végétation (PFT) ; régions froides ; comment juger un résultat « mondial ».
- **Valider les 4 décisions de `07`** (niveau de confiance et repli) : perte de sélection, mélange, aire d'applicabilité, régions froides à 2.0.
- **Prochaine étape** : produire la carte finale, avec son export NetCDF pour ORCHIDEE.
