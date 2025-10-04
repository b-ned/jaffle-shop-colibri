with

source as (

    select * from {{ ref ("model_with_white_space_in_col") }}

),

renamed as (

    select

        ----------  ids
        "order item_id" as "orderitem id",
        order_id,
        product_id

    from source

)

select * from renamed
