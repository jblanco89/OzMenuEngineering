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
        engine_df['rentabilidad'] = engine_df.apply(lambda row: "BAJO" if row['margen_contribucion'] < row['costo_receta'] else "ALTO", axis=1)  
        engine_df['popularidad'] = engine_df.apply(lambda row: "BAJO" if row['indice_popularidad'] <  pop_avg_index_value else "ALTO", axis=1)
        engine_df['clasificación'] = engine_df.apply(lambda row: 
                        "ESTRELLA" if row['rentabilidad'] == "ALTO" and row['popularidad'] == "ALTO" else
                        "ENIGMA" if row['rentabilidad'] == "ALTO" and row['popularidad'] == "BAJO" else
                        "PERRO" if row['rentabilidad'] == "BAJO" and row['popularidad'] == "BAJO" else
                        "VACA" if row['rentabilidad'] == "BAJO" and row['popularidad'] == "ALTO" else
                        "", axis=1)
        with cost_avg:
            st.metric('Coste Medio', value=round(cost_avg_value,2))
        with pop_avg_index:
            st.metric('Índice de Pop. Medio', value=round(pop_avg_index_value,2))
        with roi_avg:
            st.metric('Rentabilidad Media', value=round(roi_avg_value,2))

        st.dataframe(engine_df, hide_index=True,use_container_width=True)
        return engine_df

    def engine_explanation(self):
        with open('Markdowns/EngineExplanation.md', 'r') as EngineExplanation:
            EngineExplanation = EngineExplanation.read()
        
        st.markdown(EngineExplanation)
        

    def price_fixing(self):
        start_date = st.session_state.selected_min.date()
        end_date = st.session_state.selected_max.date()
        with open('sql/engine_table.sql', 'r') as sql_file:
            sql_query = sql_file.read()
        
        engine_df = pd.read_sql(sql_query, cursor, params=(start_date, end_date,))
        price_table = engine_df[['nombre_plato', 'unidades_vendidas', 'costo_receta', 'precio_venta', 'coste_producto_porcentage', 'total_venta_producto']]
        ex = st.expander('Metricas')
        with ex:
            disp, gamma, relacion = st.columns([1,1,1], gap='medium')
            with disp:
                st.subheader('Dispersión de Precios')
                max_price = price_table['precio_venta'].max()
                min_price = price_table['precio_venta'].min()
                diff_price = max_price - min_price
                disp_data = [{'Precio más alto': max_price,
                                'Precio más bajo': min_price,
                                'Diferencia': diff_price}
                                ]
                
                st.metric('Actual',value=diff_price)
                st.dataframe(disp_data, hide_index=True,use_container_width=True)
                st.markdown('Coeficiente ideal entre: *2,50 - 3,00*')
                # st.divider()
            with gamma:
                st.subheader('Amplitud de Gamma')
                ratio_intervalo = diff_price / 3
                low_gamma_cut = ratio_intervalo + min_price
                hi_gamma_cut =  max_price - ratio_intervalo
                low_actual_abs_value = engine_df[engine_df['precio_venta'] <= low_gamma_cut]['precio_venta'].count()
                hi_actual_abs_value = engine_df[engine_df['precio_venta'] > hi_gamma_cut]['precio_venta'].count()
                med_actual_abs_value = engine_df['nombre_plato'].count() - low_actual_abs_value - hi_actual_abs_value

                low_actual_relative_value = low_actual_abs_value * 100 / len(engine_df)
                low_ideal_relative_value = 25
                low_ideal_abs_value = round((len(engine_df) * low_ideal_relative_value) / 100,0)

                med_actual_relative_value = med_actual_abs_value * 100 / len(engine_df)
                med_ideal_relative_value = 50
                med_ideal_abs_value = round((len(engine_df) * med_ideal_relative_value) / 100,0)

                hi_actual_relative_value = hi_actual_abs_value * 100 / len(engine_df)
                hi_ideal_relative_value = 25
                hi_ideal_abs_value = round((len(engine_df) * hi_ideal_relative_value) / 100,0)

                low, med, hi = st.columns([1,1,1])
                with low:
                    st.metric('Banda Baja', low_actual_abs_value)
                with med:
                    st.metric('Banda Media', med_actual_abs_value)
                with hi:
                    st.metric('Banda Alta', hi_actual_abs_value)


                gamma_data = [
                    ['Baja', low_actual_relative_value, low_ideal_abs_value, low_ideal_relative_value],
                    ['Media', med_actual_relative_value, med_ideal_abs_value, med_ideal_relative_value],
                    ['Alta', hi_actual_relative_value, hi_ideal_abs_value, hi_ideal_relative_value]
                ]
                gama_data_addional = [{'Ratio intervalo': ratio_intervalo,
                                        'Corte gamma baja': low_gamma_cut,
                                        'Corte gamma alta': hi_gamma_cut}]
                gamma_df = pd.DataFrame(gamma_data, columns=['Banda', 'Actual %', 'Ideal abs', 'Ideal %'])
                st.dataframe(gamma_df, hide_index=True,use_container_width=True)
                st.dataframe(gama_data_addional, hide_index=True,use_container_width=True)
                # st.divider()
            with relacion:
                st.subheader('Relación Calidad - Precio')
                requested_price = (engine_df['precio_venta'].sum() / engine_df['total_venta_producto'].sum())
                offered_avg_price = (engine_df['precio_venta'].sum() / engine_df['nombre_plato'].count())
                ratio_rel_price = (requested_price / offered_avg_price)

                ideal_span_low = 0.90
                ideal_span_hi = 1.00

                action = "Recomendable SUBIR precios" if ratio_rel_price > ideal_span_hi else "Recomendable BAJAR precios" if ratio_rel_price < ideal_span_low else "Recomendable MANTENER precios"


                rq_price, offe_price, rat_price = st.columns([1,1,1])
                with rq_price:
                    st.metric('Precio Solicitado', round(requested_price,0))
                with offe_price:
                    st.metric('Precio ofertado', round(offered_avg_price,0))
                with rat_price:
                    st.metric('Relación de precios', round(ratio_rel_price,0))

                relacion_data = [
                    ['Relación ideal de precios', ideal_span_low, ideal_span_hi]
                    # ['Nuevo precio ofertado', ]
                ]
                relacion_data_df = pd.DataFrame(relacion_data, columns=['Indicador', 'Ideal min', 'Ideal max'])
                st.dataframe(relacion_data_df, hide_index=True,use_container_width=True)

                st.markdown('*Acción:*')
                st.markdown(f'**{action}**')
        # with table:
        st.subheader('Tabla de Datos')

        st.dataframe(price_table, hide_index=True,use_container_width=True)
        

        
        