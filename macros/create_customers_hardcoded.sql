-- macros/create_customers_hardcoded.sql
{% macro create_customers_hardcoded() %}
    {% set table_sql %}
        create table {{ target.schema }}.customers_hardcoded as
        select * from {{ source('ecom', 'RAW_CUSTOMERS') }}
    {% endset %}

    {% do run_query(table_sql) %}
{% endmacro %}