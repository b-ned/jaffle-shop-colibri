with

unioned as (
    {{ dbt_utils.union_relations(
        relations=[
            ref('locations'),
            ref('locations')
        ],
    ) }}
)

select * from unioned