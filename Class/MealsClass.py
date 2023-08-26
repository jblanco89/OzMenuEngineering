import base64
import pandas as pd 
import streamlit as st
import time
import datetime
import queries
from Utilities.modal import modal
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
    
    def get_expander_allergen(self, id):
        expander_allergen_data = pd.read_sql(f'''
            SELECT 
            gluten_alg,
            crustaceo_alg,
            huevo_alg,
            pescado_alg,
            cacahuetes_alg,
            lacteos_alg,
            apio_alg,
            mostaza_alg,
            sulfitos_alg,
            sesamo_alg,
            moluscos_alg,
            soja_alg,
            frutos_secos_alg,
            altramuz_alg,
            FROM PLATOS
            WHERE id = '{id}' 
        ''', cursor)
    
        return expander_allergen_data

    def add_meals_form(self):
        meals_data_frame = self.meals_data()
        with st.form(key='add_meals_form', clear_on_submit=False):
            st.write('Nuevo Plato')
            add_id = st.number_input('ID', min_value=0 ,value=meals_data_frame['ID'].iloc[-1] + 1, format='%d')
            add_name = st.text_input('NOMBRE', value="")
            add_category = st.text_input('CATEGORÍA', value="")
            add_date = st.date_input('FECHA (YYYY/MM/DD)', value=datetime.date.today())
            add_portion = st.number_input('PORCION (grs)', format='%.2f', value=0.0)
            add_sale_price = st.number_input('PRECIO VENTA (€)', format='%.2f', value=0.0)
            add_tax = st.number_input('IMPUESTO (%)', min_value=4.0, max_value=21.0, value = 10.0, step=1.0, format='%.2f')
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
            if ex:
                ex.dataframe(data, hide_index=True)
                ingredient_query = 'SELECT DISTINCT nombre FROM inventario'
                ingredient_values = pd.read_sql(ingredient_query, cursor)
                ing1, ing2 = ex.columns([1,1])
                with ing1:
                    st.selectbox('INGREDIENTE', ingredient_values, key='input_name')
                with ing2:
                    st.number_input('PORCION (gr)', format='%f', key='input_portion')
                ex.form_submit_button('Agregar', type='primary', on_click=add_ingredient)
            
            st.subheader('Alérgenos')
            ex_alrg = st.expander('Alérgenos')
            data_allergen = self.get_expander_allergen(add_id)
            column_names_allergen = data_allergen.columns.tolist()
            column_names_allergen = [item.replace("_alg", "").upper() for item in column_names_allergen]
            num_columns_allergen = 3
            groups = [column_names_allergen[i:i + num_columns_allergen] for i in range(0, len(column_names_allergen), num_columns_allergen)]
            if ex_alrg:
                checkbox_states = {col: False for col in column_names_allergen}
                for group in groups:
                    cols = st.columns(num_columns_allergen)
                    for i, col in enumerate(group):
                        checkbox_states[col] = cols[i].checkbox(col, key=col)

            
            main_btn1, main_btn2 = st.columns((1,1))
            with main_btn1:
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
                    ''')
                    cursor.executemany(f'''
                    INSERT INTO plato_ingredientes
                    (id_plato,
                    id_inventario,
                    porcion_ing_grs) 
                    VALUES (?,?,?); 
                    ''', add_meals_ingredients_tuple)
                    
                    cursor.commit()
                    # display a success message
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
            with main_btn2:
                exit_buttom = st.form_submit_button('Cancelar', type='secondary')
                if exit_buttom:
                    self.search_meal_engine_table()

    def update_meal_form(self, meals_id, 
                         meals_category, 
                         meals_name, 
                         meals_portion, 
                         meals_sale_price, 
                         meals_recipe_cost,
                        expander_data,
                        expander_allergen, 
                     cursor):
        with st.form(key='update_form', clear_on_submit=True):
            st.subheader('Editar Plato')
            meals_tax = 0.1
            updated_name = st.text_input('NOMBRE', value=meals_name)
            updated_category = st.text_input('CATEGORÍA', value=meals_category)
            updated_portion = st.number_input('PORCIONES (grs)', value=float(meals_portion), format='%f')
            updated_sale_price = st.number_input('PRECIO VENTA (€)', value=meals_sale_price, format='%f')
            updated_recipe_cost = st.number_input('COSTE RECETA (€)', value=float(meals_recipe_cost), format='%.2f')
            updated_tax = st.number_input('IMPUESTO', value=meals_tax, format='%.2f')
            updated_status = st.checkbox('¿Plato Activo?', value=True)
            if updated_status:
                updated_status_val = '1'
            else:
                updated_status_val = '0'

            meals_id = meals_id
            meals_zone = expander_data['zona'].values[0]
            updated_zone = st.text_input('ZONA', value=meals_zone)
            updated_num_portions = st.number_input('Nº PORCIONES', value=float(expander_data['numero_porciones'].values[0]),
                                                format='%f')
            st.subheader('Ingredientes del Plato')
            cross_query = queries.cross_platos_ingredientes
            plato_ing_data = pd.read_sql(cross_query, cursor, params=(meals_id,))
            plato_ing_data_df = plato_ing_data[['nombre', 'precio_compra', 'porcion_ing_grs']]
            updated_ingredients = st.dataframe(plato_ing_data_df, hide_index=True, width=600)

            st.subheader('Alérgenos')
            ex_alrg = st.expander('Alérgenos')
            data_allergen = expander_allergen
            column_names_allergen = data_allergen.columns.tolist()
            column_names_allergen = [item.replace("_alg", "").upper() for item in column_names_allergen]
            num_columns_allergen = 3
            groups = [column_names_allergen[i:i + num_columns_allergen] for i in range(0, len(column_names_allergen), num_columns_allergen)]
            if ex_alrg:
                checkbox_states = {col: False for col in column_names_allergen}
                for group in groups:
                    cols = st.columns(num_columns_allergen)
                    for i, col in enumerate(group):
                        checkbox_states[col] = cols[i].checkbox(col, key=col)

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

            upt_btn1, upt_btn2 = st.columns([5, 1], gap="small")
            with upt_btn1:
                update_button = st.form_submit_button(label='Actualizar Plato', type='primary')
                if update_button:
                    meals_id = meals_id
                    updated_status_bin = BitArray(bin=updated_status_val).bin
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
                    cursor.commit()

                    # display a success message
                    st.success('¡Plato Actualizado!', icon="✅")
                    time.sleep(2)
                    st.experimental_rerun()
            with upt_btn2:
                del_upt_buttom = st.form_submit_button('Borrar', type='secondary')
                if del_upt_buttom:
                    st.write('En construcción. Plato no ha sido eliminado')


    def create_grid_meals_table(self, meals_data_frame):
        st.subheader('Tabla de Platos Existentes')
        if st.button('Ver Reporte de platos'):
            with st.spinner(f'Generando reporte de platos... por favor espere'):
                df = pd.read_sql(f'SELECT * FROM platos', cursor)
                profile = ProfileReport(df, title='Profiling Report', explorative=True, dark_mode=True)
                pr_html = profile.to_html()
                st.components.v1.html(pr_html, width=800, height=800, scrolling=True)
        gob = GridOptionsBuilder.from_dataframe(meals_data_frame)
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
        selected_row = ag_grid['selected_rows']
        # check if a row is selected
        if selected_row:
            row_values = list(selected_row[0].values())
            # display the values in the input fields
            meals_id = row_values[1]
            meals_category = row_values[2]
            meals_name = row_values[3]
            meals_portion = round(row_values[5],2)
            meals_sale_price = round(row_values[6],2)
            meals_recipe_cost = round(row_values[7],2)
            expander_data = self.get_expander_data(id=meals_id)
            expander_allergen = self.get_expander_allergen(id=meals_id)

            self.update_meal_form(meals_id, 
                         meals_category, 
                         meals_name, 
                         meals_portion, 
                         meals_sale_price, 
                         meals_recipe_cost,
                         expander_data=expander_data,
                         expander_allergen=expander_allergen, 
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
        search_term = st.text_input('Buscar Plato', value='', placeholder='buscar plato')
        df_table = self.meals_data()
        fotos_platos = pd.read_sql('SELECT id, foto_plato FROM platos', cursor)

        if search_term:
            m1 = df_table["NOMBRE PLATO"].str.lower().str.contains(search_term.lower())
            m2 = df_table["CATEGORIA"].str.lower().str.contains(search_term.lower())
            m3 = df_table['ID'].astype(str).str.contains(search_term)
            df_search = df_table[m1 | m2 | m3]
        else:
            df_search = df_table  # Display all "platos" when no search term
        
        N_cards_per_row = 3

        for n_row, row in df_search.reset_index().iterrows():
            i = n_row % N_cards_per_row
            if i == 0:
                st.write("---")
                cols = st.columns(N_cards_per_row, gap="large")
            with cols[n_row % N_cards_per_row]:
                st.caption(f"{row['NOMBRE PLATO'].strip()} - {row['CATEGORIA'].strip()} - {row['FECHA'].strftime('%Y-%m-%d')}")
                col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Precio Venta:** {row['PRECIO VENTA']}")
                st.markdown(f"*Costo Receta:* {row['COSTO RECETA']}")
                btn = st.button('Ver Plato', key=f'{row["ID"]}', type='secondary')
                # JavaScript code to open a new tab with Markdown content
                if btn:
                    with open('Markdowns/MealsDisplay.html', 'r', encoding='utf-8') as markdown_file:
                        markdown_content = markdown_file.read()
                        st.markdown(markdown_content)
                              
                
            with col2:
                st.markdown(f"**ID:** {row['ID']}")
                selected_foto_plato = fotos_platos.loc[fotos_platos['id'] == row['ID'], 'foto_plato'].values[0]
                st.image(self.get_image(selected_foto_plato), caption=row['NOMBRE PLATO'], use_column_width=True)




            



