COPY inventario FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\inventario.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY platos FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\platos.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY alergenos FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\alergenos.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY categorias_de_plato FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\categorias_de_plato.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY categorias_de_ingredientes FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\categorias_de_ingredientes.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY plato_alergenos FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\plato_alergenos.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY plato_ingredientes FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\plato_ingredientes.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY ingenieria_menu FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\ingenieria_menu.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');
COPY ventas_productos FROM 'C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\DB\Backup_20231012\ventas_productos.csv' (FORMAT 'csv', header 0, delimiter ',', quote '"');