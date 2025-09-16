with

locations as (

    select * from {{ ref('STG_LOCATIONS') }}

)

select * from locations
