from Class.ConnectionDB import ConnectionDB
from st_aggrid import GridOptionsBuilder 
from st_aggrid import AgGrid 
from st_aggrid import GridUpdateMode
from st_aggrid import ColumnsAutoSizeMode
from st_aggrid import AgGridTheme
import pandas as pd 
import streamlit as st
import time


con = ConnectionDB('DB/engineMenu.db')
cursor = con.cursor()

class IngredientClass:
    def __init__(self, con):
        self.con = con
    def ingredients_data(self):
        ingredients_data = pd.read_sql(
            '''
            SELECT
            id,
            nombre,
            unidad_real,
            precio_compra,
            unidad_compra,
            factor_merma
            FROM
            ingredientes
            ''', cursor)
        ingredients_data = ingredients_data.rename(
                                            columns=lambda x: x
                                            .upper()
                                            .replace('_', ' ')
                                            )
        return ingredients_data
        
    def create_grid_ingredients_table(self):
        st.subheader('Tabla de Ingredientes')
        ingredients_data_frame = self.ingredients_data()
        gob = GridOptionsBuilder.from_dataframe(ingredients_data_frame)

        # set the update mode to 'ValueChange' to update the table on input chang
        gob.configure_grid_options(domLayout='normal', 
                                enableSorting=True, 
                                enableFilter=True, 
                                enableColResize=True,
                                enableRangeSelection=True, 
                                rowSelection='single', 
                                editable=True, 
                                enableCellChangeFlash=True)

        gob.configure_default_column(cellStyle={'font-size': '12px'}, 
                                    suppressMenu=True, 
                                    wrapHeaderText=True, 
                                    autoHeaderHeight=True
                                   )
        
        
        # create the agGrid table
        ag_grid = AgGrid(data = ingredients_data_frame,
        gridOptions=gob.build(),
        height='500px',
        width='100%',
        fit_columns_on_grid_load = True, 
        updateMode=GridUpdateMode.VALUE_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        reload_data=True,
        allow_unsafe_jscode=True
        )

       # get the selected row from the table
        selected_row = ag_grid['selected_rows']
       
        if selected_row:
        # get the selected row from the table
            # get the values of the selected row
            row_values = list(selected_row[0].values())
            # st.write(row_values)
            ingredients_id = row_values[1]
            ingredients_name = row_values[2]
            ingredients_unit = row_values[3]
            ingredients_purchase_price = row_values[4]
            ingredients_purchase_unit = row_values[5]
            ingredients_merma = row_values[6]
            
            with st.form(key='update_form', clear_on_submit=True):
                st.write('Update Ingrediente')
                # updated_id = st.number_input('ID', value=meals_id)
                updated_name = st.text_input('NOMBRE', value = ingredients_name)
                updated_unit = st.text_input('UNIDAD', value= ingredients_unit)
                updated_purchase_price = st.number_input('PRECIO COMPRA (€)', value=float(ingredients_purchase_price), format='%f')
                updated_purchase_unit = st.text_input('UNIDAD COMPRA', value=ingredients_purchase_unit)
                updated_merma = st.number_input('FACTOR MERMA', value=ingredients_merma)
                update_button = st.form_submit_button(label='Update Ingrediente')

            if update_button:
                # execute a query to update the row in the table
                cursor.execute(f'''
                UPDATE ingredientes 
                SET
                nombre='{updated_name}',
                unidad_real ='{updated_unit}',
                precio_compra ='{updated_purchase_price}',
                unidad_compra ='{updated_purchase_unit}',
                factor_merma ='{updated_merma}'
                WHERE id = '{ingredients_id}'
                ''')

                cursor.commit()
             # display a success message
                st.success('Ingrediente Actualizado!')
                time.sleep(2)
                st.experimental_rerun()

    def add_ingredient_form(self):
        unit_options = ('gramos', 'mililitros', 'Litros', 'Kilogramos', 'Onzas')
        ingredients_data_frame = self.ingredients_data()
        st.subheader('Agregar nuevo ingrediente')
        with st.form(key='add_ingredient_form', clear_on_submit=True):
            st.write('Nuevo Ingrediente')
            add_id = ingredients_data_frame['ID'].iloc[-1] + 1 
            # add_id = st.number_input('ID', min_value=0 ,value=, format='%d')
            add_name = st.text_input('NOMBRE')
            add_unit = st.selectbox('UNIDAD', unit_options, index=0)
            add_purchase_price = st.number_input('PRECIO DE COMPRA (€)', format='%.2f')
            add_purchase_unit = st.selectbox('UNIDAD DE COMPRA', unit_options, index=0)
            add_merma = st.number_input('FACTOR MERMA', format='%.2f')
            add_button = st.form_submit_button(label='Nuevo Ingrediente')

            if add_button:
                # execute a query to update the row in the table
                cursor.execute(f'''
                INSERT INTO ingredientes 
                (id,
                nombre,
                unidad_real,
                precio_compra,
                unidad_compra,
                factor_merma
                ) VALUES (
                '{add_id}', 
                '{add_name}', 
                '{add_unit}',
                '{add_purchase_price}',
                '{add_purchase_unit}',
                '{add_merma}'
                );
                ''')
                cursor.commit()

                # display a success message
                st.success('Nuevio ingrediente agregado')
                time.sleep(2)
                st.experimental_rerun()


       


