from Class.StockClass import StreamlitStockProcess
from Class.MealsClass import StreamlitMealsProcess
from Class.IngredientClass import IngredientClass
from Class.HomeClass import HomeClass
from Class.ConnectionDB import ConnectionDB
from Class.SalesMealsClass import StreamlitSalesMealsClass
from Class.MenuEngineeringClass import MenuEngineeringClass
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
menu_engine = MenuEngineeringClass(con=con)

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
cursor.execute(query=queries.create_allergen_table)
cursor.execute(query=queries.create_meal_ingredient_table)
cursor.execute(query=queries.create_menu_engine_table)
cursor.execute(query=queries.create_sales_table)
# cursor.execute(query=queries.insert_meals_data)
cursor.execute(query=queries.insert_inventory_data)
cursor.execute(query=queries.correct_inventario_data)
# cursor.execute(query=queries.insert_ingredient_meal_data)
cursor.execute(query=queries.insert_menu_engine_value)


def main():    
    # Create a menu with submenus
    menu = ['Platos', 'Análisis', 'Inventario','Ventas', 'About', 'Home']
    # submenu_products = ['Mostrar', 'Agregar', 'Eliminar']
    
    st.sidebar.title('MENU DE NAVEGACIÓN',)
    st.sidebar.image('img/oz_logo.png', caption='Oz Gastro club', use_column_width='auto')
    selection_menu = st.sidebar.selectbox('Main Menu', menu)
   
    # Show selected page based on menu choice
    if selection_menu == 'Home':
        home_page.show_home()
        
    elif selection_menu == 'Inventario':
        table_in, adding_in = st.tabs(['TABLA', 'AGREGAR'])
        with table_in:
            inventori.search_stock_engine()
        with adding_in:
            st.subheader('Add a new product')
            product_name = st.text_input('Product Name')
            product_description = st.text_area('Product Description')
            product_price = st.number_input('Product Price', step=0.01, format='%0.2f')
            if st.button('Submit'):
                st.success('Product added successfully!')
            

    elif selection_menu == 'Platos':
        cards, table, adding = st.tabs(['CARDS', 'TABLA', 'AGREGAR'])
        with table:
            meals.search_meal_engine_table()
        with cards:
            meals.search_meal_engine_cards()
        with adding:
            meals.add_meals_form()

    elif selection_menu == 'Análisis':
        st.subheader("Ingeniería de Menú")
        menu_engine.date_slider()
        engine_tab1, engine_tab2, engine_tab3, engine_tab4 = st.tabs(['DASHBOARD', 
                                                                      'INGENIERÍA', 
                                                                      'FIJACIÓN DE PRECIOS', 
                                                                      'EXPLICACIÓN'])
        with engine_tab1:
            st.write('construcción')
        with engine_tab2:
            menu_engine.engine_table()
        with engine_tab3:
            menu_engine.price_fixing()
        with engine_tab4:
            menu_engine.engine_explanation()
    
            


    elif selection_menu == 'Ventas':
         sales.display_data()      


if __name__ == "__main__":
    main()



