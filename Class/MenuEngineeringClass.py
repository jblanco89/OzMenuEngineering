import pandas as pd 
import streamlit as st
import time
import datetime
from Class.ConnectionDB import ConnectionDB
from Class.StockClass import StreamlitStockProcess
from Class.SalesMealsClass import StreamlitSalesMealsClass

con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()

class MenuEngineeringClass:
    def __init__(self, con) -> None:
        self.con = con

    def date_slider(self):
        with st.form('Slider-date-form', clear_on_submit=False):
            today = datetime.datetime.now()
            PRE_SELECTED_DATES = (datetime.datetime.now() - datetime.timedelta(days=60), datetime.datetime.now() - datetime.timedelta(days=10))
            MIN_MAX_RANGE = (today - datetime.timedelta(days=180), today)
            if 'selected_min' not in st.session_state:
                st.session_state.PRE_SELECTED_DATES = PRE_SELECTED_DATES
                st.session_state.MIN_MAX_RANGE = MIN_MAX_RANGE
            st.session_state.selected_min, st.session_state.selected_max = st.slider(
                "Selecciona Fecha",
                value=st.session_state.PRE_SELECTED_DATES,
                step=datetime.timedelta(days=1),
                min_value=st.session_state.MIN_MAX_RANGE[0],
                max_value=st.session_state.MIN_MAX_RANGE[1],
                format="YYYY-MM-DD",    
                )
            btn = st.form_submit_button('Filtrar')
            if btn and (st.session_state.selected_min != MIN_MAX_RANGE[0] or st.session_state.selected_max != MIN_MAX_RANGE[1]):
                st.write('Rango de fechas elegido es de:', st.session_state.selected_min.date(), 'hasta', st.session_state.selected_max.date())
                return st.session_state.selected_min.date(), st.session_state.selected_max.date()
            

    def filter_table(self, start_date, end_date):
        return True
    
    def analysis_table(self):
        return True