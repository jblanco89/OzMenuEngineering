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
cursor.execute(query=queries.create_allergen_meal_table)
cursor.execute(query=queries.create_meal_ingredient_table)
cursor.execute(query=queries.create_menu_engine_table)
cursor.execute(query=queries.create_sales_table)
cursor.execute(query=queries.insert_meals_data)
cursor.execute(query=queries.insert_inventory_data)
cursor.execute(query=queries.correct_inventario_data)
cursor.execute(query=queries.insert_ingredient_meal_data)
cursor.execute(query=queries.insert_menu_engine_value)

cursor.execute(query=queries.create_meal_category_table)
cursor.execute(query=queries.create_ingredient_category_table)
cursor.execute(query=queries.insert_meal_category_data)
cursor.execute(query=queries.insert_ingredient_category_data)
cursor.execute(query=queries.insert_allergen_data)
cursor.execute(query=queries.insert_meal_allergen_data)


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
        table_in, adding_in, categories = st.tabs(['TABLA', 'AGREGAR', 'CATEGORIAS'])
        with table_in:
            inventori.search_stock_engine()
        with adding_in:
            inventori.add_product_form()
        with categories:
            inventori.add_product_categories()
            

    elif selection_menu == 'Platos':
        cards, table, adding, categories = st.tabs(['CARDS', 'TABLA', 'AGREGAR', 'CATEGORIAS'])
        with table:
            meals.search_meal_engine_table()
        with cards:
            meals.search_meal_engine_cards()
        with adding:
            meals.add_meals_form()
        with categories:
            meals.add_meals_categories()

    elif selection_menu == 'Análisis':
        st.subheader("Ingeniería de Menú")
        menu_engine.date_slider()
        engine_tab1, engine_tab2, engine_tab3, engine_tab4 = st.tabs(['DASHBOARD', 
                                                                      'INGENIERÍA', 
                                                                      'FIJACIÓN DE PRECIOS', 
                                                                      'EXPLICACIÓN'])
        with engine_tab1:
            menu_engine.engine_dashboard()
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



