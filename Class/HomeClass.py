from Class.MealsClass import StreamlitMealsProcess
from Class.ConnectionDB import ConnectionDB
import pandas as pd 
import streamlit as st

con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()
meals = StreamlitMealsProcess(con=cursor)

class HomeClass:
    def __init__(self) -> None:
        pass
    def show_home(self):

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


        space_1, main_btn1, main_btn2, main_btn3 = st.columns((1,2,2,2))
        with space_1:
            st.container()
        with main_btn1:
            st.button('Menu Platos', type='primary')
        with main_btn2:
            st.button('Menu Inventario', type='primary')
        with main_btn3:
            st.button('Menu Escandallo', type='primary')
