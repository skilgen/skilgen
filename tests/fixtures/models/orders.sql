{{ config(materialized='table') }}

with source_orders as (
    select * from {{ source('raw', 'orders') }}
),
customer_orders as (
    select * from {{ ref('stg_customers') }}
),
legacy_payments as (
    select * from analytics.stripe.payments
)

select
    source_orders.id as order_id,
    source_orders.user_id,
    customer_orders.customer_name,
    {{ cents_to_dollars('source_orders.amount_cents') }} as amount,
    legacy_payments.status,
    current_timestamp as updated_at
from source_orders
left join customer_orders on source_orders.user_id = customer_orders.user_id
left join legacy_payments on legacy_payments.order_id = source_orders.id
