"""Generate a large synthetic dbt project on top of a copy of jaffle-shop.

Usage: python gen_project.py <src_jaffle_dir> <out_dir> <n_models>
Layers: sources -> staging (30%) -> intermediate (40%) -> marts (30%).
Each model gets a yml with column descriptions and ~5 generic tests, so tests ~= 5x models.
"""
import random
import shutil
import sys
from pathlib import Path

src, out, n_models = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
random.seed(42)
if out.exists():
    shutil.rmtree(out)
shutil.copytree(src, out, ignore=shutil.ignore_patterns(
    "target", "logs", ".git", ".venv*", "dbt_packages", "examples", ".claude", "*.duckdb"))
gen = out / "models" / "gen"
gen.mkdir(parents=True)

DOMAINS = ["finance", "sales", "marketing", "ops", "hr", "product", "support", "logistics", "billing", "risk"]
n_stg, n_int = int(n_models * 0.3), int(n_models * 0.4)
n_mart = n_models - n_stg - n_int
n_src = max(10, n_stg // 3)

COLS = [f"attr_{i:02d}" for i in range(40)]
LOREM = ("Business attribute captured from the operational system; nullable when the upstream record "
         "was created before the field existed. Owned by the domain team and reviewed quarterly.")


def columns(k):
    return ["id", "parent_id", "status", "amount_cents", "created_at", "updated_at"] + random.sample(COLS, k)


def yml_columns(cols, rel_to=None, accepted=True):
    lines = []
    for c in cols:
        lines.append(f"      - name: {c}\n        description: \"{c.replace('_', ' ').title()}. {LOREM}\"")
        tests = []
        if c == "id":
            tests += ["not_null", "unique"]
        if c == "status" and accepted:
            tests.append("accepted_values:\n              values: ['active', 'inactive', 'pending', 'closed']")
        if c == "parent_id" and rel_to:
            tests.append(f"relationships:\n              to: ref('{rel_to}')\n              field: id")
        if c in ("created_at", "amount_cents"):
            tests.append("not_null")
        if tests:
            lines.append("        data_tests:\n" + "\n".join(f"          - {t}" for t in tests))
    return "\n".join(lines)


# Sources: one yml per domain.
src_tables = []
for d in DOMAINS:
    tables = [f"raw_{d}_{i:03d}" for i in range(n_src // len(DOMAINS) + 1)]
    src_tables += [(d, t) for t in tables]
    body = "\n".join(
        f"      - name: {t}\n        description: \"Raw {t} extract. {LOREM}\"\n        loaded_at_field: updated_at\n"
        f"        columns:\n          - name: id\n            data_tests: [not_null, unique]"
        for t in tables)
    (gen / f"_src_{d}.yml").write_text(f"version: 2\nsources:\n  - name: src_{d}\n    schema: raw_{d}\n    tables:\n{body}\n")

models = {"stg": [], "int": [], "mart": []}

# Staging: one source each, renames + macros.
for i in range(n_stg):
    d, t = src_tables[i % len(src_tables)]
    name = f"stg_{d}__{i:04d}"
    cols = columns(random.randint(8, 18))
    select = ",\n        ".join(
        "{{ cents_to_dollars('amount_cents') }} as amount" if c == "amount_cents" else
        "{{ dbt.date_trunc('day', 'created_at') }} as created_at" if c == "created_at" else
        f"cast({c} as varchar) as {c}" if c.startswith("attr") else c
        for c in cols)
    sql = f"""with

source as (

    select * from {{{{ source('src_{d}', '{t}') }}}}

),

renamed as (

    select
        {select}

    from source
    where id is not null

)

select * from renamed
"""
    (gen / "staging" / d).mkdir(parents=True, exist_ok=True)
    (gen / "staging" / d / f"{name}.sql").write_text(sql)
    (gen / "staging" / d / f"{name}.yml").write_text(
        f"version: 2\nmodels:\n  - name: {name}\n    description: \"Staged {t}. {LOREM}\"\n"
        f"    config:\n      materialized: view\n      tags: ['staging', '{d}']\n    columns:\n{yml_columns(cols)}\n")
    models["stg"].append((name, d, cols))


def layer(kind, count, upstream_pools, joins):
    for i in range(count):
        d = DOMAINS[i % len(DOMAINS)]
        name = f"{kind}_{d}__{i:04d}"
        pool = [m for p in upstream_pools for m in models[p]]
        ups = random.sample(pool, min(len(pool), random.randint(*joins)))
        cols = columns(random.randint(10, 22))
        ctes = ",\n\n".join(f"u{j} as (\n\n    select * from {{{{ ref('{u[0]}') }}}}\n\n)" for j, u in enumerate(ups))
        join = "\n".join(f"    left join u{j} on u0.id = u{j}.parent_id" for j in range(1, len(ups)))
        select = ",\n        ".join(
            f"u{random.randrange(len(ups))}.{c}" if c.startswith("attr") else f"u0.{c}" for c in cols)
        agg = ""
        if kind == "mart":
            agg = ("\n\n, summary as (\n\n    select\n        id,\n        count(*) as row_count,\n"
                   "        sum(amount) as total_amount,\n        {{ dbt_utils.generate_surrogate_key(['id', 'status']) }} as sk\n"
                   "    from joined\n    group by id, status\n\n)")
        final = "select joined.*, summary.row_count, summary.total_amount from joined left join summary using (id)" \
            if kind == "mart" else "select * from joined"
        sql = f"""with

{ctes},

joined as (

    select
        {select},
        u0.amount
    from u0
{join}

){agg}

{final}
"""
        folder = gen / ("intermediate" if kind == "int" else "marts") / d
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.sql").write_text(sql)
        (folder / f"{name}.yml").write_text(
            f"version: 2\nmodels:\n  - name: {name}\n    description: \"{kind} model for {d}. {LOREM}\"\n"
            f"    config:\n      materialized: {'table' if kind == 'mart' else 'ephemeral' if i % 5 == 0 else 'view'}\n"
            f"      tags: ['{kind}', '{d}']\n      meta:\n        owner: team_{d}\n        tier: {i % 3}\n"
            f"    data_tests:\n      - dbt_utils.expression_is_true:\n          expression: \"amount >= 0\"\n"
            f"    columns:\n{yml_columns(cols, rel_to=ups[0][0])}\n")
        models[kind].append((name, d, cols))


layer("int", n_int, ["stg", "int"], (2, 4))
layer("mart", n_mart, ["int", "stg"], (2, 5))
print(f"models: stg={n_stg} int={n_int} mart={n_mart} sources={len(src_tables)}")
