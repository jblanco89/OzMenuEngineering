WITH ventas_summary AS (
        SELECT 
        id_plato,
        nombre_plato,
        SUM(unidades_vendidas) AS unidades_vendidas
        FROM
        ventas_productos
        WHERE Fecha >= ? AND Fecha <= ?
        GROUP BY nombre_plato, id_plato

)
SELECT 
p.nombre_plato, 
v.unidades_vendidas, 
p.costo_receta, 
p.precio_venta, 
(p.costo_receta / p.precio_venta * 100) AS coste_producto_porcentage,
(p.precio_venta - p.costo_receta) AS margen_contribucion,
(v.unidades_vendidas * p.costo_receta) AS total_coste_producto,
(v.unidades_vendidas * p.precio_venta) AS total_venta_producto,
(total_venta_producto - total_coste_producto) AS total_margen,
FROM platos AS p 
INNER JOIN ventas_summary AS v 
ON p.id = v.id_plato