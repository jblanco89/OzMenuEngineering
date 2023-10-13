WITH RECURSIVE IdPlatoRecursive(id_plato) AS (
    SELECT 1 -- Starting id_plato
    UNION
    SELECT id_plato + 1 FROM IdPlatoRecursive WHERE id_plato < 701 -- Increment id_plato until 701
)
INSERT OR IGNORE INTO plato_ingredientes (id_plato, id_inventario, porcion_ing_grs)
SELECT id_plato, 999999, 0 FROM IdPlatoRecursive;
