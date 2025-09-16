-- macros/create_customers_hardcoded.sql
{% macro create_customers_hardcoded() %}
    {% set schema_sql %}
        create schema if not exists public
    {% endset %}

    {% set table_sql %}
        create or replace table public.customers_hardcoded as
        select * from {{ source('ecom', 'RAW_CUSTOMERS') }}
    {% endset %}

    {{ run_query(schema_sql) }}
    {{ run_query(table_sql) }}
{% endmacro %}