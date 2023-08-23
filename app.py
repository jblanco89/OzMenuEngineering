from Class.StockClass import StreamlitStockProcess
from Class.MealsClass import StreamlitMealsProcess
from Class.IngredientClass import IngredientClass
from Class.HomeClass import HomeClass
from Class.ConnectionDB import ConnectionDB
from Class.SalesMealsClass import StreamlitSalesMealsClass
import streamlit as st
import pandas as pd
import queries



# Create a new database
con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()

#Instantiating Classes
inventori = StreamlitStockProcess(con)
meals = StreamlitMealsProcess(con)
# ingredients = IngredientClass(con)
home_page = HomeClass()
sales = StreamlitSalesMealsClass(con)

css_styles = '''
<style>
    body{
        font-family:"karla",
        "Helvetica Neue",
        sans-serif;
        font-size: 13px;
        }
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
cursor.execute(query=queries.create_meals_table)
cursor.execute(query=queries.create_meal_ingredient_table)
cursor.execute(query=queries.create_menu_engine_table)
cursor.execute(query=queries.create_sales_table)
cursor.execute(query=queries.insert_meals_data)
cursor.execute(query=queries.insert_inventory_data)
cursor.execute(query=queries.correct_inventario_data)
cursor.execute(query=queries.insert_ingredient_meal_data)
# cursor.execute(query=queries.insert_sales_data)
cursor.execute(query=queries.insert_menu_engine_value)




def main():    
    # Create a menu with submenus
    menu = ['Home', 'Inventario', 'Platos', 'Analisis', 'Ventas', 'About']
    # submenu_products = ['Mostrar', 'Agregar', 'Eliminar']
    
    st.sidebar.title('MENU DE NAVEGACIÓN',)
    st.sidebar.image('img/oz_logo.png', caption='Oz Gastro club', use_column_width='auto')
    selection_menu = st.sidebar.selectbox('Main Menu', menu)
   
    # Show selected page based on menu choice
    if selection_menu == 'Home':
        home_page.show_home()
        
    elif selection_menu == 'Inventario':
        if st.button('Agregar Ingrediente', type='primary', key='main_btn2'):
            # elif submenu_choice == 'Agregar':
            st.subheader('Add a new product')
            product_name = st.text_input('Product Name')
            product_description = st.text_area('Product Description')
            product_price = st.number_input('Product Price', step=0.01, format='%0.2f')
            if st.button('Submit'):
            # Add product to database or save data to file
                st.success('Product added successfully!')
        else:
            inventori.search_stock_engine()

    elif selection_menu == 'Platos':
        cards, table = st.tabs(['Tarjetas', 'Tabla'])
        with table:
            if st.button('Agregar Plato', type='primary'):
                meals.add_meals_form(cursor=cursor)
            else:
                meals.search_meal_engine_table()
        with cards:
            meals.search_meal_engine_cards()
        

    elif selection_menu == 'Analisis':
            st.write('En construcción')


    elif selection_menu == 'Ventas':
         sales.display_data()      


if __name__ == "__main__":
    main()



