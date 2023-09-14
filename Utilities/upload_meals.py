import pandas as pd

sales_raw = pd.read_excel('./Uploads/VENTASARTICULOSFECHA.xls', sheet_name='Hoja1')

sales_df = sales_raw[['Codigo', 'Nombre']]

meals_unique = sales_df.drop_duplicates()
meals_unique = meals_unique.sort_values('Codigo')

print(meals_unique)

meals_unique.to_csv('./Uploads/unique_meal_list.csv', sep=',', index=False, header=True)

# cursor.executemany(f'''
#     INSERT INTO platos
#         (id,
#         nombre_plato
#         )VALUES({meals_unique['Codigo']}, {meals_unique['Nombre']});
# ''')

