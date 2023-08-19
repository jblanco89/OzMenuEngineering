# **************************** BEGIN ********************************** #
if 'data' not in st.session_state:
                data = pd.DataFrame({'ID_PLATO':[],
                                     'ID_INGREDIENTE':[],
                                     'INGREDIENTE':[],
                                     'PORCION (gr)':[],
                                     'PRECIO': [],
                                     'FACTOR MERMA': [],
                                     'COSTE': []})
                st.session_state.data = data

data = st.session_state.data

def add_ingredient():

    nombre = st.session_state.input_name
    porcion = st.session_state.input_portion

    temp_table = f"SELECT id, precio_compra, factor_merma FROM inventario WHERE nombre = '{nombre}'"
    temp_df = pd.read_sql(temp_table, cursor)
    id_ingrediente = temp_df['id'].values[0]
    precio = temp_df['precio_compra'].values[0]
    factor_merma = temp_df['factor_merma'].values[0]
    # coste = (porcion * precio) / factor_merma
    coste = porcion * precio
    row = pd.DataFrame({'ID_PLATO':[add_id],
            'ID_INGREDIENTE':[id_ingrediente],
            'INGREDIENTE':[nombre],
            'PORCION (gr)':[porcion],
            'PRECIO':[precio],
            'FACTOR MERMA': [factor_merma],
            'COSTE':[coste]})
    st.session_state.data = pd.concat([st.session_state.data, row])  

ex = st.expander('Agregar Ingredientes')
if ex:
    ex.dataframe(data)
    ingredient_query = 'SELECT DISTINCT nombre FROM inventario'
    ingredient_values = pd.read_sql(ingredient_query, cursor)
    ing1, ing2 = ex.columns([1,1])
    with ing1:
        st.selectbox('INGREDIENTE', ingredient_values, key='input_name')
    with ing2:
        st.number_input('PORCION (gr)', format='%f', key='input_portion')
    ex.form_submit_button('agregar', type='primary', on_click=add_ingredient)
        # ex.write(data)
# *************************** END ************************************* #


# ************************** BEGIN ************************************* #


