from Class.StockClass import StreamlitStockProcess
from Class.MealsClass import StreamlitMealsProcess
from Class.IngredientClass import IngredientClass
from Class.ConnectionDB import ConnectionDB
from pandas_profiling import ProfileReport
import streamlit as st
import pandas as pd
import queries



# Create a new database
con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()


#Instantiating Classes
inventori = StreamlitStockProcess(con)
meals = StreamlitMealsProcess(con)
ingredients = IngredientClass(con)

css_styles = '''
<style>
    body{
        font-family:"karla",
        "Helvetica Neue",
        sans-serif;
        font-size: 13px;
        }
    button{
    display: inline-block;
    }

</style>
'''

# Set page width and add custom CSS stylesheet
st.set_page_config(page_title='Oz Menu System', 
                   layout='wide',page_icon="🧊", menu_items={
'Get Help': 'https://www.extremelycoolapp.com/help',
'Report a bug': "https://www.extremelycoolapp.com/bug",
'About': "# This is a header. This is an *extremely* cool app!"
})
st.markdown(css_styles,
            unsafe_allow_html=True)



# DATE data type in duckDB --> ISO 8601 format (YYYY-MM-DD).
cursor.execute(query=queries.create_inventory_table)
cursor.execute(query=queries.create_ingredients_table)
cursor.execute(query=queries.create_meals_table)
cursor.execute(query=queries.create_meal_ingredient_table)
cursor.execute(query=queries.insert_meals_data)
cursor.execute(query=queries.insert_ingredients_data)
cursor.execute(query=queries.insert_inventory_data)


def home():    
    # Create a menu with submenus
    menu = ['Home', 'Inventario', 'Platos', 'Ingredientes', 'About']
    submenu_products = ['Mostrar', 'Agregar', 'Eliminar']

    # Set page title and subtitle
    st.title('OZ :orange[Menu] Engineering',)
    st.write(
    '''
    This Menu System is a comprehensive tool developed in Python and Streamlit 
    that facilitates the process of designing and managing restaurant menus. 
    It integrates an Inventory System, Meal characteristics, 
    Ingredient components, 
    and Allergens, allowing for a robust engineering of the menu offerings. 
    With its user-friendly interface and intuitive controls, 
    this system streamlines the menu design process while providing essential insights 
    into ingredient usage, costs, and nutritional information
    '''
    )

    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:
        st.image('img/comidas.webp', caption='Comidas', use_column_width='auto')
    with col2:
        st.image('img/cocteles.webp', caption='Cócteles', use_column_width='auto')
    with col3:
         st.image('img/postres.webp', caption='Postres', use_column_width='auto')
    with col4:
        st.image('img/vinos.webp', caption='Vinos', use_column_width='auto')


    st.sidebar.title('MENU DE NAVEGACIÓN',)
    st.sidebar.image('img/oz_logo.png', caption='Oz Gastro club', use_column_width='auto')
    selection_menu = st.sidebar.selectbox('Main Menu', menu)
   
    # Show selected page based on menu choice
    # if selection_menu == 'Home':
        
    if selection_menu == 'Inventario':    
        selection_submenu = st.sidebar.selectbox('Selecciona una acción',
                                           submenu_products)
        submenu_choice = selection_submenu

        if submenu_choice == 'Mostrar':
            if st.button('Ver Reporte de Inventario'):
                with st.spinner(f'Generando reporte de inventario... por favor espere'):
                    df = pd.read_sql(f'SELECT * FROM inventario', cursor)
                    profile = ProfileReport(df, title='Profiling Report', explorative=True, dark_mode=True)
                    pr_html = profile.to_html()
                    st.components.v1.html(pr_html, width=800, height=800, scrolling=True)

            inventori.create_grid_stock_table()

        elif submenu_choice == 'Agregar':
            # Example form for adding a new product
            st.subheader('Add a new product')
            product_name = st.text_input('Product Name')
            product_description = st.text_area('Product Description')
            product_price = st.number_input('Product Price', step=0.01, format='%0.2f')
            if st.button('Submit'):
            # Add product to database or save data to file
                st.success('Product added successfully!')

    elif selection_menu == 'Platos':
        selection_submenu = st.sidebar.selectbox('Selecciona una acción',
                                        submenu_products)
        submenu_choice = selection_submenu
        if submenu_choice == 'Mostrar':
            if st.button('Ver Reporte de platos'):
                with st.spinner(f'Generando reporte de platos... por favor espere'):
                    df = pd.read_sql(f'SELECT * FROM platos', cursor)
                    profile = ProfileReport(df, title='Profiling Report', explorative=True, dark_mode=True)
                    pr_html = profile.to_html()
                    st.components.v1.html(pr_html, width=800, height=800, scrolling=True)
            meals.create_grid_meals_table()
        elif submenu_choice == 'Agregar':
            meals.add_meals_form()

    elif selection_menu == 'Ingredientes':
        selection_submenu = st.sidebar.selectbox('Selecciona una acción',
                                        submenu_products)
        submenu_choice = selection_submenu
        if submenu_choice == 'Mostrar':
            ingredients.create_grid_ingredients_table()
        elif submenu_choice == 'Agregar':
            ingredients.add_ingredient_form()        

    # elif st.sidebar.selectbox('Menu', menu) == 'About':
    #      st.subheader('More About')
    #      st.write(
    #         'This is a demonstration of a modern Streamlit page with tables, forms, and a menu. '
    #         'It was created by Javier Blanco.')
        

if __name__ == "__main__":
    home()


