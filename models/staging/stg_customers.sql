with

source as (

    select * from {{ source('ecom', 'raw_customers') }}

),

hardcoded_ref as (
    select * from TEST_DB.PUBLIC.CUSTOMERS_HARDCODED
),

renamed as (

    select

        ----------  ids
        s1.id as customer_id,

        ---------- text
        s1.name as customer_name,
        s2.customer_name as hardcoded_name,

    from source s1
    left join hardcoded_ref s2 
        on s1.id = s2.customer_id

)

select * from renamed
