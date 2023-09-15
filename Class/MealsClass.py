import base64
import pandas as pd 
import streamlit as st
import time
import datetime
import queries
from Class.ConnectionDB import ConnectionDB
from Class.StockClass import StreamlitStockProcess
from st_aggrid import GridOptionsBuilder 
from st_aggrid import AgGrid 
from st_aggrid import GridUpdateMode
from st_aggrid import ColumnsAutoSizeMode
from st_aggrid import AgGridTheme
import streamlit.components.v1 as components
from bitstring import BitArray
from pandas_profiling import ProfileReport
from io import BytesIO

con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()

class StreamlitMealsProcess:
    def __init__(self, con):
        self.con = con

    def get_image(self, img_data):
        image_bytes = base64.b64decode(img_data)
        actual_image = BytesIO(image_bytes)
        return actual_image
    
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
    
    def get_expander_allergen(self):
        expander_allergen_data = ['Gluten 🚫', 
                                  'Crustáceos 🦞',
                                  'Huevo 🥚',
                                  'Pescado 🐟',
                                  'Cacahuetes 🥜',
                                  'Lacteos 🥛',
                                  'Apio 🥬',
                                  'Mostaza 🌿',
                                  'Sulfitos 🧪',
                                  'Sésamo 🍞',
                                  'Moluscos 🐚',
                                  'Soja 🥟',
                                  'Frtos secos 🌰',
                                  'Altramuz 🌱']
        expander_allergen_data = [item.upper() for item in expander_allergen_data]
    
        return expander_allergen_data
    
    def upload_meal_file(self):
        file_upload = st.expander('Subida de archivo')
        st.subheader('Añadir platos')
        st.markdown("*Añadir lista platos desde archivo Excel*")
        st.markdown('El archivo debe contener como mínimo dos columnas:`ID del plato` y `Nombre del plato`')
        with file_upload:
            st.file_uploader('Subir lista de platos', type=["xlsx", "xls"])

    def add_meals_form(self):
        checkbox_states = {}
        st.subheader('Formulario para añadir plato')
        meals_data_frame = self.meals_data()
        id_value = meals_data_frame['ID'].iloc[-1] + 1
        with st.form(key='add_meals_form', clear_on_submit=False):
            st.subheader('Nuevo Plato')
            st.markdown(f'**ID Plato:** {id_value}')
            add_id = id_value
            # add_id = st.number_input('ID', min_value=0, value=id_value,format='%d')
            add_name = st.text_input('NOMBRE', value="")
            # add_category = st.text_input('CATEGORÍA', value="")
            add_category = st.selectbox('CATEGORÍA',('CENA','BREAKFAST','LUNCH', 'VINOS'))
            add_date = st.date_input('FECHA (YYYY/MM/DD)', value=datetime.date.today())
            add_portion = st.number_input('PORCION (grs)', format='%.2f', value=0.0)
            add_sale_price = st.number_input('PRECIO VENTA (€)', format='%.2f', value=0.0)
            # add_tax = st.number_input('IMPUESTO (%)', min_value=4.0, max_value=21.0, value = 10.0, step=1.0, format='%.2f')
            st.markdown(f'**IMPUESTO:** 10%')
            add_tax = 10
            add_img = st.file_uploader('Imagen', type=['jpg', 'jepg'])
    
            add_status = st.checkbox('¿Plato Activo?')
            if add_status:
                add_status_val = '1'
            else:
                add_status_val = '0'

            if 'data' not in st.session_state:
                data = pd.DataFrame({'ID_PLATO':[],
                                     'ID_INGREDIENTE':[],
                                     'INGREDIENTE':[],
                                     'PORCION (gr)':[],
                                     'PRECIO': [],
                                    #  'FACTOR MERMA': [],
                                     'COSTE': []})
                st.session_state.data = data

            data = st.session_state.data

            def add_ingredient():
                nombre = st.session_state.input_name
                porcion = st.session_state.input_portion

                temp_table = f"SELECT id, precio_compra FROM inventario WHERE nombre = '{nombre}'"
                temp_df = pd.read_sql(temp_table, cursor)
                id_ingrediente = temp_df['id'].values[0]
                precio = temp_df['precio_compra'].values[0]
                coste = (porcion / 1000 ) * precio
                row = pd.DataFrame({'ID_PLATO':[add_id],
                        'ID_INGREDIENTE':[id_ingrediente],
                        'INGREDIENTE':[nombre],
                        'PORCION (gr)':[porcion],
                        'PRECIO':[precio],
                        # 'FACTOR MERMA': [factor_merma],
                        'COSTE':[coste]})
                st.session_state.data = pd.concat([st.session_state.data, row])  

            ex = st.expander('Agregar Ingredientes')
            df_ex_2 = st.data_editor(data, 
                                disabled=("ID_PLATO", "ID_INGREDIENTE", "INGREDIENTE", "PORCION (gr)", "PRECIO", "COSTE"), 
                                hide_index=True,
                                use_container_width=True,
                                num_rows='dynamic')
            if ex:
                df_ex_2
                # ex.dataframe(data, hide_index=True)
                ingredient_query = 'SELECT DISTINCT nombre FROM inventario'
                ingredient_values = pd.read_sql(ingredient_query, cursor)
                ing1, ing2 = ex.columns([1,1])
                with ing1:
                    st.selectbox('INGREDIENTE', ingredient_values, key='input_name')
                with ing2:
                    st.number_input('PORCION (gr)', format='%f', key='input_portion')
                ex.form_submit_button('Agregar', type='primary', on_click=add_ingredient)

            st.subheader('Alérgenos')
            with st.expander('Alérgenos'):
                data_allergen = self.get_expander_allergen()
                allergen_df = pd.DataFrame({
                                "Alérgeno": data_allergen,
                                "Presencia": [False for _ in range(len(data_allergen))],
                            }
                                )
                new_allergen_df = st.data_editor(allergen_df, column_config={
                                                    "Presencia": st.column_config.CheckboxColumn(
                                                        "¿Hay Alérgeno?",
                                                        help="Selecciona el **Alérgeno**",
                                                        default=False,
                                                        width="small",
                                                    )
                                                },
                                                disabled=["Alérgeno"],
                                                hide_index=True,
                                                use_container_width=True) 
            add_additional_exp = st.expander('Información adicional')
            with add_additional_exp:
                add_zona = st.selectbox('ZONA', ('TERRAZA', 'SALA', 'BARRA'))
                add_portions_number = st.number_input('Nº PORCIONES')
                expander_data = self.get_expander_data(id=add_id)
                add_prep_mins = st.number_input('TIEMPO PREPARACIÓN (mins)', value=expander_data['tiempo_prep_mins'].values[0] if expander_data['tiempo_prep_mins'].values else 0.0, min_value=0.0, key='add_time_prep')
                add_cook_mins = st.number_input('TIEMPO COCCIÓN (mins)', value=expander_data['tiempo_coccion_mins'].values[0] if expander_data['tiempo_coccion_mins'].values else 0.0, min_value=0.0, key='add_time_coock')
                add_temp_serv = st.number_input('TEMPERATURA SERVICIO (ºC)',
                                                    value=expander_data['temp_serv_c'].values[0] if expander_data['temp_serv_c'].values else 0.0, min_value=0.0, key='add_temp_serv')
                add_elaboracion = st.text_area('ELABORACIÓN',
                                                value=expander_data['elaboracion'].values[0] if expander_data['elaboracion'].values else '',
                                                max_chars=1000,
                                                height=12,
                                                placeholder='Describe la elaboracón del plato (1000 caracteres)')
                add_presentation = st.text_area('PRESENTACIÓN',
                                                    value=expander_data['presentacion'].values[0] if expander_data['presentacion'].values else '',
                                                    max_chars=500,
                                                    height=8,
                                                    placeholder='Describe la presentación del plato (400 caracteres)')
                add_tools = st.text_area('EQUIPO DE ELABORACIÓN',
                                            value=expander_data['equipo_elaboracion'].values[0] if expander_data['equipo_elaboracion'].values else '',
                                            max_chars=500,
                                            height=8,
                                            placeholder='Menciona el equipo necesario para elaboración (400 caracteres)') 

            # main_btn1, main_btn2 = st.columns((1,1))
            # with main_btn1:
            add_button = st.form_submit_button(label='Nuevo Plato', type='primary')
            if add_button:
                add_tax = (add_tax / 100)
                add_status_bin = BitArray(bin=add_status_val).bin
                add_portion = float(add_portion)
                add_ingredients_data = pd.DataFrame(data)
                add_recipe_cost = add_ingredients_data['COSTE'].sum()
                add_meals_ingredients_tuple = [tuple(row) for row in add_ingredients_data[['ID_PLATO', 'ID_INGREDIENTE', 'PORCION (gr)']].values]
                if add_img is not None:
                    add_img_contents = add_img.read()
                    st.image(add_img_contents, caption=f'{add_name}')
                    add_img = base64.b64encode(add_img_contents).decode('utf-8')
                else:
                    img = open('img/oz_logo.jpg', 'rb')
                    image_data = img.read()
                    add_img = base64.b64encode(image_data).decode('utf-8')
                # execute a query to update the row in the table
                cursor.execute(f'''
                INSERT INTO platos 
                (id,
                zona,
                categoria,
                nombre_plato,
                Fecha,
                porcion_grs,
                numero_porciones,
                tiempo_prep_mins,
                tiempo_coccion_mins,
                temp_serv_c,               
                precio_venta,
                costo_receta,
                impuesto,
                elaboracion,
                presentacion,
                equipo_elaboracion,               
                foto_plato,
                plato_activo) VALUES (
                '{add_id}',
                '{add_zona}', 
                '{add_category}', 
                '{add_name}',
                '{add_date}',
                '{add_portion}',
                '{add_portions_number}',
                '{add_prep_mins}',
                '{add_cook_mins}',
                '{add_temp_serv}',
                '{add_sale_price}', 
                '{add_recipe_cost}',
                '{add_tax}',
                '{add_elaboracion}',
                '{add_presentation}',
                '{add_tools}',
                '{add_img}',
                '{add_status_bin}'
                );
                ''')
                cursor.executemany(f'''
                INSERT INTO plato_ingredientes
                (id_plato,
                id_inventario,
                porcion_ing_grs) 
                VALUES (?,?,?); 
                ''', add_meals_ingredients_tuple)

                all_allergens = new_allergen_df[['Alérgeno', 'Presencia']].values.tolist()
                allergen_to_insert = [(add_id, allergen, presence) for allergen, presence in all_allergens]
                cursor.executemany('''INSERT INTO alergenos 
                                    (id_plato, 
                                    alergeno, 
                                    presencia) 
                                    VALUES (?, ?, ?);''', allergen_to_insert)
                cursor.commit()
                st.success('Nuevo plato agregado')
                time.sleep(2)
                st.session_state.data = pd.DataFrame({'ID_PLATO':[],
                                    'ID_INGREDIENTE':[],
                                    'INGREDIENTE':[],
                                    'PORCION (gr)':[],
                                    'PRECIO': [],
                                #  'FACTOR MERMA': [],
                                    'COSTE': []})
                st.experimental_rerun()
            # with main_btn2:
            #     exit_buttom = st.form_submit_button('Cancelar', type='secondary')
            #     if exit_buttom:
            #         self.search_meal_engine_table()

    def update_meal_form(self, meals_id, 
                         meals_category,
                         meals_date, 
                         meals_name, 
                         meals_portion, 
                         meals_sale_price, 
                         meals_recipe_cost,
                        expander_data,
                     cursor):
        with st.form(key='update_form', clear_on_submit=True):
            st.subheader('Editar Plato')
            meals_tax = 0.1
            updated_name = st.text_input('NOMBRE', value=meals_name)
            updated_category = st.selectbox('CATEGORÍA',options= (meals_category,) + ('CENA','BREAKFAST','LUNCH', 'VINOS') if meals_category else ('CENA','BREAKFAST','LUNCH', 'VINOS'))
            # updated_category = st.text_input('CATEGORÍA', value=meals_category)
            meals_date = datetime.datetime.strptime(meals_date, '%Y-%m-%dT%H:%M:%S.%f') if meals_date else datetime.date.today()
            updated_date = st.date_input('FECHA (YYYY/MM/DD)', value=meals_date, format='YYYY/MM/DD')
            updated_portion = st.number_input('PORCION (grs)', value=float(meals_portion), format='%f')
            updated_sale_price = st.number_input('PRECIO VENTA (€)', value=meals_sale_price, format='%f')
            updated_recipe_cost = st.number_input('COSTE RECETA (€)', value=float(meals_recipe_cost), format='%.2f')
            updated_tax = 0.10
            st.markdown(f'**IMPUESTO: {updated_tax*100}%**')
            # updated_tax = st.number_input('IMPUESTO', value=meals_tax, format='%.2f')
            updated_status = st.checkbox('¿Plato Activo?', value=True)
            if updated_status:
                updated_status_val = '1'
            else:
                updated_status_val = '0'

            cross_query = queries.cross_platos_ingredientes
            plato_ing_data = pd.read_sql(cross_query, cursor, params=(meals_id,))
            plato_ing_data_df = plato_ing_data[['id','nombre', 'porcion_ing_grs', 'precio_compra']]
            plato_ing_data_df = plato_ing_data_df.rename(columns={'id':'ID_INGREDIENTE','nombre':'INGREDIENTE', 'precio_compra':'PRECIO €', 'porcion_ing_grs':'PORCION (grs)'})
            plato_ing_data_df['COSTE'] = (plato_ing_data_df['PORCION (grs)'] / 1000) * plato_ing_data_df['PRECIO €']
            plato_ing_data_df['ID_PLATO'] = meals_id


            meals_id = meals_id
            meals_zone = expander_data['zona'].values[0]
            updated_zone = st.selectbox('ZONA',options=(meals_zone,) + ('TERRAZA', 'SALA', 'BARRA') if meals_zone else ('TERRAZA', 'SALA', 'BARRA'))
            updated_num_portions = st.number_input('Nº PORCIONES', value=float(expander_data['numero_porciones'].values[0]),
                                                format='%f')
            
            def calculate_data_from_ingredient_name_list(ingredient_df, id_plato):
                ingredient_list = ingredient_df['INGREDIENTE'].values.tolist()
                ingredient_names = ', '.join([f"'{name}'" for name in ingredient_list])
                query = f'SELECT id, precio_compra FROM inventario WHERE nombre IN ({ingredient_names});'
                results = pd.read_sql(query, cursor)
                results = results.rename(columns={'id':'ID_INGREDIENTE','precio_compra':'PRECIO €'})
                ingredient_df['PORCION (grs)'] = pd.to_numeric(ingredient_df['PORCION (grs)'], errors='coerce')
                results['COSTE'] = (ingredient_df['PORCION (grs)'] / 1000) * results['PRECIO €']
                results['ID_PLATO'] = id_plato
                results['PORCION (grs)'] = ingredient_df['PORCION (grs)']
                results['INGREDIENTE'] = ingredient_df['INGREDIENTE']

                return results

            st.subheader('Ingredientes del Plato')
            ingredient_query = 'SELECT DISTINCT nombre FROM inventario'
            ingredient_values = pd.read_sql(ingredient_query, cursor)
            updated_ingredients = st.data_editor(plato_ing_data_df,
                                                column_config={
                                                    "INGREDIENTE": st.column_config.SelectboxColumn(
                                                        "INGREDIENTE",
                                                        help="Selecciona Ingrediente",
                                                        width="large",
                                                        options=ingredient_values.values.tolist(),
                                                        required = True,     
                                                    )
                                                }, 
                                                hide_index=True, 
                                                use_container_width=True,
                                                disabled=('PRECIO €', 'ID_INGREDIENTE', 'COSTE', 'ID_PLATO'),
                                                num_rows='dynamic'
                                                )
        
            
            st.subheader('Alérgenos')
            # ex_alrg = st.expander('Alérgenos')
            data_allergen = pd.read_sql(f'SELECT id_plato, alergeno, presencia FROM alergenos WHERE id_plato = {meals_id}', cursor)
            data_allergen_df = pd.DataFrame(data_allergen)
            if data_allergen_df.empty:
                data_allergen = self.get_expander_allergen()
                new_data_allergen_df = pd.DataFrame({
                                'ID Plato': meals_id,
                                "Alérgeno": data_allergen,
                                # "Presencia": data_allergen_df['presencia']
                                "Presencia": [False for _ in range(len(data_allergen))],
                            }
                                )
            else:
                new_data_allergen_df = data_allergen_df

            new_data_allergen_df.rename(columns={'id_plato':'ID Plato','alergeno': 'Alérgeno', 'presencia': 'Presencia'}, inplace=True)
                
            updated_data_allergen = st.data_editor(new_data_allergen_df, column_config={
                                                        "Presencia": st.column_config.CheckboxColumn(
                                                            "¿Hay Alérgeno?",
                                                            help="Selecciona el **Alérgeno**",
                                                            default=False,
                                                            width="small",
                                                        )
                                                    },
                                                    disabled=["Alérgeno"],
                                                    hide_index=True,
                                                    use_container_width=True)
            
            uptdated_prep_mins = st.number_input('TIEMPO PREPARACIÓN (mins)', value=expander_data['tiempo_prep_mins'].values[0])
            uptdated_cook_mins = st.number_input('TIEMPO COCCIÓN (mins)', value=expander_data['tiempo_coccion_mins'].values[0])
            uptdated_temp_serv = st.number_input('TEMPERATURA SERVICIO (ºC)',
                                                value=expander_data['tiempo_coccion_mins'].values[0])
            updated_elaboracion = st.text_area('ELABORACIÓN',
                                            value=expander_data['elaboracion'].values[0],
                                            max_chars=1000,
                                            height=12,
                                            placeholder='Describe la elaboracón del plato (1000 caracteres)')
            updated_presentation = st.text_area('PRESENTACIÓN',
                                                value=expander_data['presentacion'].values[0],
                                                max_chars=500,
                                                height=8,
                                                placeholder='Describe la presentación del plato (400 caracteres)')
            updated_tools = st.text_area('EQUIPO DE ELABORACIÓN',
                                        value=expander_data['equipo_elaboracion'].values[0],
                                        max_chars=500,
                                        height=8,
                                        placeholder='Menciona el equipo necesario para elaboración (400 caracteres)')

            
            
            img_data = expander_data['foto_plato'].values[0]
            image_bytes = base64.b64decode(img_data)
            actual_image = self.get_image(img_data=img_data)
            st.image(actual_image, updated_name)
            updated_img = st.file_uploader('Imagen', type=['jpg', 'jpeg'])

            # upt_btn1, upt_btn2 = st.columns([5, 1], gap="small")
            # with upt_btn1:
            update_button = st.form_submit_button(label='Actualizar Plato', type='primary')
            if update_button:
                meals_id = meals_id
                ingredient_df = updated_ingredients
                df = calculate_data_from_ingredient_name_list(ingredient_df, id_plato=meals_id)
                updated_ingredients_new = df
                updated_status_bin = BitArray(bin=updated_status_val).bin
                updated_ingredients_data = updated_ingredients_new
                updated_recipe_cost = updated_ingredients_data['COSTE'].sum()
                updated_meals_ingredients_tuple = [tuple(row) for row in updated_ingredients_data[['ID_INGREDIENTE', 'PORCION (grs)', 'ID_PLATO']].values]
                updated_all_allergen_list = updated_data_allergen[['Alérgeno','Presencia']].values.tolist()
                updated_all_allergen_to_insert = [(allergen, presence) for allergen, presence in updated_all_allergen_list]
                if updated_img is not None:
                    updated_img_contents = updated_img.read()
                    st.image(updated_img_contents, caption=f'{updated_name}')
                    updated_img = base64.b64encode(updated_img_contents).decode('utf-8')
                else:
                    # updated_img = actual_image
                    updated_img = base64.b64encode(image_bytes).decode('utf-8')
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
                equipo_elaboracion = '{updated_tools}',
                foto_plato = '{updated_img}'
                WHERE id = '{meals_id}'
                ''')

                for inventory_id, portion, meal_id in updated_meals_ingredients_tuple:
                    meal_id = int(meal_id)
                    inventory_id = int(inventory_id)
                    cursor.execute('''
                    SELECT COUNT(*) FROM plato_ingredientes
                    WHERE id_plato = ? AND id_inventario = ?
                ''', (meal_id, inventory_id))
                
                    count = cursor.fetchone()[0]
                
                    if count == 0:
                        # No record exists, so perform an INSERT
                        cursor.execute('''
                            INSERT INTO plato_ingredientes (id_plato, id_inventario, porcion_ing_grs)
                            VALUES (?, ?, ?)
                        ''', (meal_id, inventory_id, portion))
                    else:
                        cursor.execute('''
                            UPDATE plato_ingredientes
                            SET
                            porcion_ing_grs = ?
                            WHERE id_plato = ? AND id_inventario = ?
                        ''', (portion, meal_id, inventory_id))            
                
                cursor.commit()

                # # display a success message
                st.success('¡Plato Actualizado!', icon="✅")
                time.sleep(2)
                st.experimental_rerun()
            # with upt_btn2:
            #     del_upt_buttom = st.form_submit_button('Borrar', type='secondary')
            #     if del_upt_buttom:
            #         st.write('En construcción. Plato no ha sido eliminado')


    def create_grid_meals_table(self, meals_data_frame):
        st.subheader('Tabla de Platos Existentes')
        if st.button('Ver Reporte de platos'):
            with st.spinner(f'Generando reporte de platos... por favor espere'):
                df = pd.read_sql(f'SELECT * FROM platos', cursor)
                profile = ProfileReport(df, title='Profiling Report', explorative=True, dark_mode=True)
                pr_html = profile.to_html()
                st.components.v1.html(pr_html, width=800, scrolling=True)
        gob = GridOptionsBuilder.from_dataframe(meals_data_frame)
        gob.configure_grid_options(domLayout='normal', 
                                enableSorting=True, 
                                enableFilter=True, 
                                enableColResize=True,
                                enableRangeSelection=True, 
                                rowSelection='single', 
                                editable=True, 
                                enableCellChangeFlash=True)

        gob.configure_default_column(cellStyle={'font-size': '13px'}, 
                                    suppressMenu=True, 
                                    wrapHeaderText=True, 
                                    autoHeaderHeight=True
                                   )
        
        
        ag_grid = AgGrid(data = meals_data_frame,
        gridOptions=gob.build(),
        height='600px',
        width='100%',
        fit_columns_on_grid_load = True, 
        updateMode=GridUpdateMode.VALUE_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        reload_data=True,
        allow_unsafe_jscode=True
        )
        selected_row = ag_grid['selected_rows']
        # check if a row is selected
        if selected_row:
            row_values = list(selected_row[0].values())
            # display the values in the input fields
            meals_id = row_values[1]
            meals_category = row_values[2]
            meals_name = row_values[3]
            meals_date = row_values[4]
            meals_portion = round(row_values[5],2)
            meals_sale_price = round(row_values[6],2)
            meals_recipe_cost = round(row_values[7],2)
            expander_data = self.get_expander_data(id=meals_id)

            self.update_meal_form(meals_id, 
                         meals_category,
                         meals_date,
                         meals_name, 
                         meals_portion, 
                         meals_sale_price, 
                         meals_recipe_cost,
                         expander_data=expander_data,
                         cursor=cursor)            
    
    def search_meal_engine_table(self):
        search_term = st.text_input('Buscar')
        df_table = self.meals_data()
        m1 = df_table["NOMBRE PLATO"].str.lower().str.contains(search_term.lower())
        m2 = df_table["CATEGORIA"].str.lower().str.contains(search_term.lower())
        df_search = df_table[m1 | m2]
        if search_term:
            self.create_grid_meals_table(meals_data_frame=df_search)
        else:
            self.create_grid_meals_table(meals_data_frame=df_table)


    def search_meal_engine_cards(self):
        allergen_icons = {
                'Gluten': '🚫',
                'Crustáceos': '🦞',
                'Huevo': '🥚',
                'Pescado': '🐟',
                'Cacahuetes': '🥜',
                'Lacteos': '🥛',
                'Apio': '🥬',
                'Mostaza': '🌿',
                'Sulfitos': '🧪',
                'Sésamo': '🍞',
                'Moluscos': '🐚',
                'Soja': '🥟',
                'Frutos secos': '🌰',
                'Altramuz': '🌱'
            }
        allergen_names = self.get_expander_allergen()
        search_term = st.text_input('Buscar Plato', value='', placeholder='Buscar por nombre | categoría | ID')
        num_rows = st.selectbox('Layout Platos', options=(1,2,3,4), index=1)
        df_table = self.meals_data()
        df_table = df_table[df_table['PLATO ACTIVO'] == '1']
        fotos_platos = pd.read_sql('SELECT id, foto_plato FROM platos', cursor)

        if search_term:
            m1 = df_table["NOMBRE PLATO"].str.lower().str.contains(search_term.lower())
            m2 = df_table["CATEGORIA"].str.lower().str.contains(search_term.lower())
            m3 = df_table['ID'].astype(str).str.contains(search_term)
            df_search = df_table[m1 | m2 | m3]
        else:
            df_search = df_table  # Display all "platos" when no search term
        
        N_cards_per_row = num_rows

        for n_row, row in df_search.reset_index().iterrows():
            i = n_row % N_cards_per_row
            if i == 0:
                st.write("---")
                cols = st.columns(N_cards_per_row, gap="large")
            with cols[n_row % N_cards_per_row]:
                meal_info ={
                    "ID": row['ID'],
                    "NAME":row['NOMBRE PLATO'],
                    "CATEGORY":row['CATEGORIA']

                }
                st.caption(f"{row['NOMBRE PLATO'].strip()} - {row['CATEGORIA'].strip()} - {row['FECHA'].strftime('%Y-%m-%d')}")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**ID:** {row['ID']}")
                    st.markdown(f"**Precio Venta:** {row['PRECIO VENTA']}")
                    st.markdown(f"*Costo Receta:* {row['COSTO RECETA']}")
                    allergens = pd.read_sql(f"SELECT alergeno FROM alergenos WHERE presencia = 'true' AND id_plato = {row['ID']}", cursor)
                    allergens = allergens.values.tolist()
                    st.markdown(f"*{allergens}*")  
                    btn = st.button('Ver Plato', key=f'{row["ID"]}', type='secondary')
                if btn:
                    with open('Markdowns/MealsDisplay.md', 'r', encoding='utf-8') as markdown_file:
                        markdown_template = markdown_file.read()
                    markdown_content = markdown_template.format_map(meal_info)
                    st.markdown(markdown_content, unsafe_allow_html=True)  
                with col2:
                    selected_foto_plato = fotos_platos.loc[fotos_platos['id'] == row['ID'], 'foto_plato'].values[0]
                    st.image(self.get_image(selected_foto_plato), caption=row['NOMBRE PLATO'], use_column_width=True)




            



