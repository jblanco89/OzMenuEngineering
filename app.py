from Class.StockClass import StreamlitStockProcess
from Class.MealsClass import StreamlitMealsProcess
from Class.IngredientClass import IngredientClass
from Class.HomeClass import HomeClass
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
home_page = HomeClass()

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



def main():    
    # Create a menu with submenus
    menu = ['Home', 'Inventario', 'Platos', 'Escandallo', 'About']
    submenu_products = ['Mostrar', 'Agregar', 'Eliminar']
    
    st.sidebar.title('MENU DE NAVEGACIÓN',)
    st.sidebar.image('img/oz_logo.png', caption='Oz Gastro club', use_column_width='auto')
    selection_menu = st.sidebar.selectbox('Main Menu', menu)
   
    # Show selected page based on menu choice
    if selection_menu == 'Home':
        home_page.show_home()
        
    elif selection_menu == 'Inventario':    
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
            
            inventori.search_stock_engine()

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
            meals.search_meal_engine()
            # meals.create_grid_meals_table()
        elif submenu_choice == 'Agregar':
            meals.add_meals_form()

    elif selection_menu == 'Escandallo':
        selection_submenu = st.sidebar.selectbox('Selecciona una acción',
                                        submenu_products)
        submenu_choice = selection_submenu
        if submenu_choice == 'Mostrar':
            #ingredients.create_grid_ingredients_table()
            st.write('En construcción')
        elif submenu_choice == 'Agregar':
            #ingredients.add_ingredient_form()
            st.write('En construcción')       

    # elif st.sidebar.selectbox('Menu', menu) == 'About':
    #      st.subheader('More About')
    #      st.write(
    #         'This is a demonstration of a modern Streamlit page with tables, forms, and a menu. '
    #         'It was created by Javier Blanco.')
        

if __name__ == "__main__":
    main()



