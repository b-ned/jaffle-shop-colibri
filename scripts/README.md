# scripts

## gen_project.py

Generates a large synthetic dbt project (default use: 1000 models, ~6,600 tests)
on top of a copy of this jaffle shop, for performance testing of tooling such as
the Colibri VS Code extension. Deterministic (fixed seed), contains no real data.

```bash
python scripts/gen_project.py . ../big1000 1000   # <src> <out_dir> <n_models>
cd ../big1000 && dbt deps && dbt parse
```

Layers: sources -> staging (30%) -> intermediate (40%) -> marts (30%). Needs
`dbt_utils` (see `packages.yml`) and the `cents_to_dollars` macro.
