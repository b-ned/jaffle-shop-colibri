{% snapshot orders_snapshot %}

{{
    config(
        unique_key='order_id',
        strategy='timestamp',
        updated_at='updated_at',
        target_schema='snapshots',
    )
}}

select
    *
from {{ ref('orders') }} -- adjust to your source definition

{% endsnapshot %}