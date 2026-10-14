-- STOCKFLOW: INITIAL SEED DATA

-- 1. Warehouses
INSERT INTO warehouses (name, location)
VALUES
    ('Almacen Central', 'San Luis Potosi'),
    ('Sucursal Norte', 'Zona Norte'),
    ('Sucursal Sur', 'Zona Sur');


-- 2. Products
INSERT INTO products
    (sku, name, description, unit, min_stock)
VALUES
    ('CEM001', 'Cemento Gris 50kg',
     'Cemento para construccion', 'Bulto', 20),

    ('BLK001', 'Block 12x20x40',
     'Block de concreto', 'Pieza', 100),

    ('ARE001', 'Arena Triturada',
     'Arena para construccion', 'M3', 10),

    ('GRA001', 'Grava 3/4',
     'Grava para concreto', 'M3', 10),

    ('VAR001', 'Varilla 3/8',
     'Varilla de acero', 'Pieza', 50);


-- 3. Initial inventory
INSERT INTO inventory
    (product_id, warehouse_id, quantity)
SELECT
    p.product_id,
    w.warehouse_id,
    initial.quantity
FROM (
    VALUES
        ('CEM001', 'Almacen Central', 120),
        ('BLK001', 'Almacen Central', 500),
        ('ARE001', 'Almacen Central', 25),
        ('GRA001', 'Almacen Central', 8),
        ('VAR001', 'Almacen Central', 75),
        ('CEM001', 'Sucursal Norte', 35),
        ('BLK001', 'Sucursal Norte', 80),
        ('CEM001', 'Sucursal Sur', 15),
        ('BLK001', 'Sucursal Sur', 150)
) AS initial(sku, warehouse_name, quantity)
JOIN products p
    ON p.sku = initial.sku
JOIN warehouses w
    ON w.name = initial.warehouse_name;
