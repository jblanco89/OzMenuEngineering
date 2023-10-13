
WITH RECURSIVE id_plato_series AS (
  SELECT 1 AS id_plato
  UNION ALL
  SELECT id_plato + 1
  FROM id_plato_series
  WHERE id_plato < 701
)

-- Insert the data into plato_alergenos
INSERT OR IGNORE INTO plato_alergenos (id_plato, id_alergeno, presencia)
SELECT id_plato_series.id_plato, alergenos.id_alergeno, 0 AS presencia
FROM id_plato_series
CROSS JOIN alergenos
WHERE alergenos.id_alergeno BETWEEN 1 AND 14;
