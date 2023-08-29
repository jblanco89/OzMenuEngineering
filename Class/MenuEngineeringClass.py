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
                # st.write('Rango de fechas elegido es de:', st.session_state.selected_min.date(), 'hasta', st.session_state.selected_max.date())
                return st.session_state.selected_min.date(), st.session_state.selected_max.date()
            

    def filter_dates(self, start_date, end_date):
        return start_date, end_date
    
    def calculate_percentage(self, value, total_sum):
        try:
            return (value / total_sum) * 100
        except ZeroDivisionError:
            return ''
         
    def engine_table(self):
        start_date = st.session_state.selected_min.date()
        end_date = st.session_state.selected_max.date()
        #metrics stimation
        with open('sql/engine_table.sql', 'r') as sql_file:
            sql_query = sql_file.read()

        engine_df = pd.read_sql(sql_query, cursor, params=(start_date, end_date,))
        cost_avg_value = (engine_df['total_coste_producto'].sum() / engine_df['total_venta_producto'].sum()) * 100
        sold_units_total = engine_df['unidades_vendidas'].sum()
        engine_df['indice_popularidad'] = engine_df.apply(lambda row: self.calculate_percentage(row['unidades_vendidas'], sold_units_total) if row['nombre_plato'] != '' else '', axis=1)
        pop_avg_index_value = 70 / engine_df['indice_popularidad'].count()
        roi_avg_value = (engine_df['precio_venta'].sum() / engine_df['costo_receta'].sum()) * 100
        cost_avg, pop_avg_index, roi_avg = st.columns([2,2,2])
        with cost_avg:
            st.metric('Coste Medio', value=round(cost_avg_value,2))
        with pop_avg_index:
            st.metric('Índice de Pop. Medio', value=round(pop_avg_index_value,2))
        with roi_avg:
            st.metric('Rentabilidad Media', value=round(roi_avg_value,2))

        st.dataframe(engine_df, hide_index=True,use_container_width=True)

    def engine_explanation(self):
        with open('Markdowns/EngineExplanation.md', 'r') as EngineExplanation:
            EngineExplanation = EngineExplanation.read()
        
        st.markdown(EngineExplanation)
        

    def price_fixing(self):
        
        return True
        

        
        