with

source as (

    select * from {{ source('ecom', 'RAW_CUSTOMERS') }}

),

hardcoded_ref as (
    select * from public.customers_hardcoded
),

renamed as (

    select

        ----------  ids
        s1.id as customer_id,

        ---------- text
        s1.name as customer_name,
        s2.name as hardcoded_name

    from source s1
    left join hardcoded_ref s2 
        on s1.id = s2.id

)

select * from renamed
