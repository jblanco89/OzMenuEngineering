from Class.ConnectionDB import ConnectionDB
from Class.IngredientClass import IngredientClass
from st_aggrid import GridOptionsBuilder 
from st_aggrid import AgGrid 
from st_aggrid import GridUpdateMode
from st_aggrid import ColumnsAutoSizeMode
from st_aggrid import AgGridTheme
from bitstring import BitArray
from io import BytesIO
from PIL import Image
import pandas as pd 
import streamlit as st
import time
import datetime



con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()
ingredints = IngredientClass(con)


# Define the Streamlit Stock Process
class StreamlitMealsProcess:
    def __init__(self, con):
        self.con = con
    
    def meals_data(self):
        meals_data = pd.read_sql(
            '''
            SELECT
            id,
            categoria,
            nombre_plato,
            Fecha,
            porcion_grs,
            round(precio_venta,2) AS precio_venta,
            round(costo_receta,2) AS costo_receta,
            round((precio_venta - precio_venta*impuesto),2) AS precio_neto,
            round((precio_venta - precio_venta*impuesto - costo_receta),2) AS beneficio,
            plato_activo 
            FROM platos
            ''', 
            cursor)
        meals_data = meals_data.rename(
                                    columns=lambda x: x
                                    .upper()
                                    .replace('_', ' ')
                                    )
        
        return meals_data
    def ingredient_form(self):
        st.write('Agregar ingredientes')
        with st.container():
            name = st.selectbox('INGREDIENTE', ('Carne Picada', 'Salsa', 'Cebolla'))
            ingredient_portion = st.number_input('CANTIDAD', format='%.2f')
            ingredient_unit = st.text_input('UNIDAD')
            add_ingre_to_meals_button = st.form_submit_button('Agregar al plato', 
                                                              type='secondary' 
                                                              )
            if add_ingre_to_meals_button:
                # st.experimental_rerun()
                st.empty()
                time.sleep(3)
                self.ingredient_form()

    def get_expander_data(self, id):
        expander_data = pd.read_sql(
            f'''
            SELECT 
            zona,
            numero_porciones,
            tiempo_prep_mins,
            tiempo_coccion_mins,
            temp_serv_c,
            elaboracion,
            presentacion,
            equipo_elaboracion,
            foto_plato
            FROM PLATOS
            WHERE id = '{id}' 
        ''', cursor)

        return expander_data


    def create_grid_meals_table(self):
        st.subheader('Tabla de Platos Existentes')
        meals_data_frame = self.meals_data()
        gob = GridOptionsBuilder.from_dataframe(meals_data_frame)

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
        ag_grid = AgGrid(data = meals_data_frame,
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
        # check if a row is selected
        if selected_row:
        # get the selected row from the table
            # get the values of the selected row
            # row_values = 
            row_values = list(selected_row[0].values())
            # display the values in the input fields
            meals_id = row_values[1]
            meals_category = row_values[2]
            meals_name = row_values[3]
            meals_portion = round(row_values[5],2)
            meals_sale_price = round(row_values[6],2)
            meals_recipe_cost = round(row_values[7],2) 

            with st.form(key='update_form', clear_on_submit=True):
                st.subheader('Editar Plato')
                meals_tax=0.1
                updated_name = st.text_input('NOMBRE', value = meals_name)
                updated_category = st.text_input('CATEGORÍA', value= meals_category)
                updated_portion = st.number_input('PORCIONES (grs)', value=float(meals_portion), format='%f')
                updated_sale_price = st.number_input('PRECIO VENTA (€)', value=meals_sale_price, format='%f')
                updated_recipe_cost = st.number_input('COSTE RECETA (€)', value= float(meals_recipe_cost), format='%.2f')
                updated_tax = st.number_input('IMPUESTO', value=meals_tax, format='%.2f')
                updated_status = st.checkbox('¿Plato Activo?')

                if updated_status:
                    updated_status_val = '1'
                else:
                    updated_status_val = '0'

                # update_expander = st.form_submit_button('Expandir')
                # if update_expander:
                #     with st.container():
                meals_id = meals_id
                expander_data = self.get_expander_data(id=meals_id)
                meals_zone = expander_data['zona'].values[0]
                updated_zone = st.text_input('ZONA', value = meals_zone)
                updated_num_portions = st.number_input('Nº PORCIONES', value = float(expander_data['numero_porciones'].values[0]), format='%f')
                uptdated_prep_mins = st.number_input('TIEMPO PREPARACIÓN (mins)', value = expander_data['tiempo_prep_mins'].values[0])
                uptdated_cook_mins = st.number_input('TIEMPO COCCIÓN (mins)', value = expander_data['tiempo_coccion_mins'].values[0])
                uptdated_temp_serv = st.number_input('TEMPERATURA SERVICIO (ºC)', value = expander_data['tiempo_coccion_mins'].values[0])
                updated_elaboracion = st.text_area('ELABORACIÓN', 
                                                    value = expander_data['elaboracion'].values[0],
                                                    max_chars=1000, 
                                                    height=12, 
                                                    placeholder='Describe la elaboracón del plato (1000 caracteres)')
                updated_presentation = st.text_area('PRESENTACIÓN', 
                                                    value = expander_data['presentacion'].values[0],
                                                    max_chars=500, 
                                                    height=8, 
                                                    placeholder='Describe la presentación del plato (400 caracteres)')
                updated_tools = st.text_area('EQUIPO DE ELABORACIÓN', 
                                                    value = expander_data['equipo_elaboracion'].values[0],
                                                    max_chars=500, 
                                                    height=8, 
                                                    placeholder='Menciona el equipo necesario para elaboración (400 caracteres)')
                
                img_data = expander_data['foto_plato'].values[0]
                updated_img = st.image('img/Imagen1.jpg', 'referencia')

                        # if img_data:
                        #     img_data = BytesIO(img_data)
                        #     updated_img = st.image(Image.open(img_data),
                        #                         caption= f'{updated_name}')
                        # else:
                        #     updated_img = st.file_uploader('Imagen', type=['png', 'jpg', 'jepg'])
                        #     if updated_img:
                        #         img = Image.open(updated_img)
                        #         updated_img = st.image(img, caption=f'{updated_name}')
                # else:

                #     updated_zone = ''
                #     updated_num_portions = 0.0
                #     uptdated_prep_mins = 0.0
                #     uptdated_cook_mins = 0.0
                #     uptdated_temp_serv = 0.0
                #     updated_elaboracion = ''
                #     updated_presentation = ''
                #     updated_tools = ''
                #     # updated_img = st.image('img/Imagen1.jpg', 'referencia')


    
                update_button = st.form_submit_button(label='Update Plato', type='primary')
                
                if update_button:
                    meals_id = meals_id
                    # st.write(expander_data)
                    st.write(updated_zone)
                    updated_status_bin = BitArray(bin=updated_status_val).bin
                    # updated_img = updated_img.read()
                    # execute a query to update the row in the table
                    cursor.execute(f'''
                    UPDATE platos 
                    SET 
                    categoria='{updated_category}', 
                    nombre_plato='{updated_name}',
                    porcion_grs='{updated_portion}',
                    precio_venta='{updated_sale_price}', 
                    costo_receta='{updated_recipe_cost}',
                    impuesto ='{updated_tax}',
                    plato_activo = '{updated_status_bin}',
                    zona = '{updated_zone}',
                    numero_porciones = '{updated_num_portions}',
                    tiempo_prep_mins = '{uptdated_prep_mins}',
                    tiempo_coccion_mins = '{uptdated_cook_mins}',
                    temp_serv_c = '{uptdated_temp_serv}',
                    elaboracion = '{updated_elaboracion}',
                    presentacion = '{updated_presentation}',
                    equipo_elaboracion = '{updated_tools}'
                    WHERE id = '{meals_id}'
                    ''')
                    cursor.commit()

                    # display a success message
                    st.success('Plato Actualizado!')
                    time.sleep(2)
                    st.experimental_rerun()

# meals_data_frame['id'].iloc[-1] + 1
    def add_meals_form(self):
        meals_data_frame = self.meals_data()
        with st.form(key='add_meals_form', clear_on_submit=True):
        # with st.container():
            st.write('Nuevo Plato')
            add_id = st.number_input('ID', min_value=0 ,value=meals_data_frame['ID'].iloc[-1] + 1, format='%d')
            add_name = st.text_input('NOMBRE')
            add_category = st.text_input('CATEGORÍA')
            add_date = st.date_input('FECHA (YYYY/MM/DD)', value=datetime.date.today())
            add_portion = st.number_input('PORCION (grs)', format='%.2f')
            add_sale_price = st.number_input('PRECIO VENTA (€)', format='%.2f')
            add_recipe_cost = st.number_input('COSTE RECETA (€)', format='%.2f')
            add_tax = st.number_input('IMPUESTO (%)', min_value=4.0, max_value=21.0, value = 10.0, step=1.0, format='%.2f')
            add_img = st.file_uploader('Imagen', type=['png', 'jpg', 'jepg'])
            # add_ingredient_button = st.form_submit_button(label='Mostrar Ingredientes', 
                                            #   use_container_width=False)
            
            if add_img:
                img = Image.open(add_img)
                st.image(img, caption=f'{add_name}')


            add_status = st.checkbox('¿Plato Activo?')
            if add_status:
                add_status_val = '1'
            else:
                add_status_val = '0'

            add_button = st.form_submit_button(label='Nuevo Plato', type='primary')

            if add_button:
                add_tax = (add_tax / 100)
                add_status_bin = BitArray(bin=add_status_val).bin
                add_recipe_cost = float(add_recipe_cost)
                add_portion = float(add_portion)
                add_img = add_img.read()
                # execute a query to update the row in the table
                cursor.execute(f'''
                INSERT INTO platos 
                (id,
                categoria,
                nombre_plato,
                Fecha,
                porcion_grs,
                precio_venta,
                costo_receta,
                impuesto,
                foto_plato,
                plato_activo) VALUES (
                '{add_id}', 
                '{add_category}', 
                '{add_name}',
                '{add_date}',
                '{add_portion}',
                '{add_sale_price}', 
                '{add_recipe_cost}',
                '{add_tax}',
                '{add_img}',
                '{add_status_bin}'
                );
                ''', )
                cursor.commit()

                # display a success message
                st.success('Nuevio plato agregado')
                time.sleep(2)
                st.experimental_rerun()

