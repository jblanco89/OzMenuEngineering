INSERT OR IGNORE INTO platos SELECT Codigo, NULL, NULL, Nombre, NULL, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '', '', '', NULL, '0' FROM read_csv_auto("C:\Users\javie\Documents\Jami\Jami-Project\Escandallo\MenuEngine\Uploads\meal_list_unique_completed.csv", delim=";", header=True, ignore_errors=1); 