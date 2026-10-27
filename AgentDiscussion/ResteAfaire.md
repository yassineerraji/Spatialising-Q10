# Reste à faire

Liste mise de côté le 26/10/2026 : **on n'y travaille pas tout de suite**, on y reviendra plus tard, sur demande explicite de l'équipe.

## Décisions à valider
- [ ] **Les 3 propositions de la partie C** (`04_comparaison_modeles`, cf. `AgentDiscussion/04_comparaison_modeles.md`) :
  1. carte produite avec **Elastic Net V2 et bridage des variables** ;
  2. carte livrée **avec son aire d'applicabilité** (36 % des terres) ;
  3. carte **BART V2** en variante de sensibilité, pour les régions froides.

## Cohérence des documents
- [ ] **Harmoniser `context/context.md`**, qui indique toujours « ~2.2 », alors que `INSTRUCTIONS.md` et tout le code utilisent 2.0 (`Q10_REFERENCE` de `src/protocole.py`).

## Questions pour B. Guenet
- [ ] **Grille et format** attendus pour la carte (résolution, grille exacte, NetCDF).
- [ ] **Q10 fixe ou fonction du climat**, qui évoluerait avec le climat simulé.
- [ ] **Q10 par type de végétation (PFT)** : le carbone du sol d'ORCHIDEE est-il suivi par PFT ?
- [ ] **Régions froides** : quelle valeur est la plus plausible (Elastic Net ≈ 3.4, BART ≈ 2.9) ?
- [ ] **Comment juger un résultat « mondial »**, sans aucun site en Afrique ni en Amérique du Sud ?

## Prochaine étape technique
- [ ] **Produire la carte finale de Q10**, avec son export **NetCDF** pour ORCHIDEE.
- [ ] **Piste proposée dans les slides** : un **niveau de confiance** par cellule (nombre de sites à moins de ≈ 1 000 km, combiné à l'aire d'applicabilité) et une **valeur de repli** (2.0 ou valeur régionale) sous un seuil α. Variante sans saut : mélange pondéré par la confiance.
