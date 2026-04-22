# Forum Crawl

This tree stores raw and analyzed crawls of the public WorldQuant BRAIN support community.

Use it when you want to mine reusable templates, workflow heuristics, or forum evidence without immediately promoting the material to the external knowledge base.

## Layout

- `YYYY-MM-DD-support-worldquantbrain/`
  - `raw/pages/*.json`: per-page crawl metadata
  - `raw/pages/*.html`: rendered page HTML
  - `raw/pages/*.txt`: text snapshot used for local analysis
  - `analysis/template-catalog.json`: structured template catalog
  - `analysis/template-catalog.md`: readable summary of template families
  - `analysis/template-excerpts.md`: concrete workflow and template skeletons
  - `analysis/knowledge-link-map.md`: project-to-KB promotion map
  - `analysis/decision-notes.md`: project-local promotion posture

## Promotion Rules

- Workflow rules that repeat across sessions are good `skill-candidate` material.
- Template families that can seed constrained alpha variants are good `kb-candidate` material.
- One-off post snippets and page-specific formulas should stay project-local until they prove reusable.

## Latest Run

- `./2026-04-22-support-worldquantbrain/`
