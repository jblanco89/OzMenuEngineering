import pandas as pd
import duckdb as dk

sales_raw = pd.read_excel('./Uploads/VENTASARTICULOSFECHA.xls', sheet_name='Hoja1')

sales_df = sales_raw[['Codigo', 'Nombre']]

meals_unique = sales_df.drop_duplicates()
meals_unique = meals_unique.sort_values('Codigo')
meals_unique['Codigo'] = meals_unique['Codigo'].astype(int)




meals_unique.to_csv('./Uploads/unique_meal_list.csv', sep=',', index=False, header=True)



