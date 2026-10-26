# Présentation (Beamer, 16:9)

- `slides.tex` : source LaTeX de la présentation ; `slides.pdf` : version compilée.
- `figures/` : figures en PDF, générées par `figures.py` à partir des données et des résultats en cache (`resultats/04/`).

Reconstruire, depuis la racine du dépôt :

```
.venv/bin/python presentation/figures.py      # ≈ 1 min 30
cd presentation && tectonic -X compile slides.tex
```
