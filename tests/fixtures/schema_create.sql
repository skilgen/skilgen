CREATE TABLE public.customers (
    customer_id BIGINT PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES public.customers(customer_id),
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    amount_cents INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_amount_positive CHECK (amount_cents >= 0)
);

CREATE INDEX idx_orders_customer_id ON public.orders (customer_id);
CREATE INDEX idx_orders_notes ON public.orders (notes);

COMMENT ON TABLE public.orders IS 'Customer order facts';
COMMENT ON COLUMN public.orders.status IS 'Current order lifecycle status';
