-- Assuming the CSV file is imported into a temporary table called 'csv_data'
WITH csv_data AS (
    SELECT Codigo_Plato, Codigo_Ingrediente, Porciones
    FROM read_csv_auto('C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\Uploads\insert_meal_ingredients_data.csv', delim=';', header=True, ignore_errors=1)
)

INSERT OR IGNORE INTO plato_ingredientes
(id_plato,
id_inventario,
porcion_ing_grs)
SELECT Codigo_Plato, Codigo_Ingrediente, Porciones
FROM csv_data;

-- -- Update the plato_ingredientes table based on the CSV data
-- UPDATE plato_ingredientes 
-- SET 
--     id_inventario = (SELECT Codigo_Ingrediente FROM csv_data WHERE plato_ingredientes.id_plato = csv_data.Codigo_Plato),
--     porcion_ing_grs = (SELECT Porciones FROM csv_data WHERE plato_ingredientes.id_plato = csv_data.Codigo_Plato)
-- WHERE plato_ingredientes.id_plato IN (SELECT DISTINCT Codigo_Plato FROM csv_data);

