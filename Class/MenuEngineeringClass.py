import pandas as pd 
import streamlit as st
import plotly.express as px
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
         
    def engine_table(self, data_only:bool = False):
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
        if data_only == False:
            with cost_avg:
                st.metric('Coste Medio', value=round(cost_avg_value,2))
            with pop_avg_index:
                st.metric('Índice de Pop. Medio', value=round(pop_avg_index_value,2))
            with roi_avg:
                st.metric('Rentabilidad Media', value=round(roi_avg_value,2))

            table_epx = st.expander('Tabla Ingenería de Menú')
            with table_epx:
                st.dataframe(engine_df, hide_index=True,use_container_width=True)

            plot_exp = st.expander('Gráfico Matríz BCG')
            with plot_exp:
                st.subheader('MATRIZ BCG')
                data_engine_plot = engine_df[['nombre_plato','unidades_vendidas','margen_contribucion','clasificación']]
                colors = {'PERRO': 'red', 'VACA': 'blue', 'ESTRELLA': 'green', 'ENIGMA': 'yellow'}
                fig = px.scatter(data_engine_plot, 
                                x='unidades_vendidas', 
                                y='margen_contribucion', 
                                color='clasificación',
                                title='Ingeniería del Menú - Matriz BCG', 
                                text='nombre_plato', 
                                color_discrete_map=colors,
                                labels={'unidades_vendidas': 'UNIDADES VENDIDAS', 'margen_contribucion': 'MARGEN DE CONTRIBUCIÓN'}
                                )
                
                fig.update_traces(textposition='top center',
                    marker=dict(size=12, opacity=0.7),
                    textfont=dict(size=12))
                # Customize point labels and colors
                # fig.update_traces(textposition='top center',
                #                 marker=dict(size=12, opacity=0.7, line=dict(width=2, color='DarkSlateGrey')),
                #                 textfont=dict(size=12),
                #                 selector=dict(mode='markers+text'))

                # # Update axis titles, font, and style
                # fig.update_xaxes(title_font=dict(size=14, family='Arial', color='black'),
                #                 showline=True, linewidth=2, linecolor='black')
                # fig.update_yaxes(title_font=dict(size=14, family='Arial', color='black'),
                #                 showline=True, linewidth=2, linecolor='black')

                # # Update title font and style
                # fig.update_layout(title_font=dict(size=18, family='Arial', color='black'),
                #                 title_x=0.5, title_y=0.98,
                #                 plot_bgcolor='white', paper_bgcolor='white',
                #                 legend=dict(title='', font=dict(size=14, family='Arial')))

                # Show the plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)

        return engine_df

    def engine_explanation(self):
        with open('Markdowns/EngineExplanation.md', 'r') as EngineExplanation:
            EngineExplanation = EngineExplanation.read()
        
        st.markdown(EngineExplanation)
        

    def price_fixing(self, data_only:bool = False):
        start_date = st.session_state.selected_min.date()
        end_date = st.session_state.selected_max.date()
        with open('sql/engine_table.sql', 'r') as sql_file:
            sql_query = sql_file.read()
        
        engine_df = pd.read_sql(sql_query, cursor, params=(start_date, end_date,))
        price_table = engine_df[['nombre_plato', 'unidades_vendidas', 'costo_receta', 'precio_venta', 'coste_producto_porcentage', 'total_venta_producto']]
        max_price = price_table['precio_venta'].max()
        min_price = price_table['precio_venta'].min()
        diff_price = max_price - min_price
        if min_price != 0:
            disp_metric = max_price / min_price
        else:
            disp_metric = 1
        # disp_metric = max_price / min_price
        disp_data = [{'Precio más alto': max_price,
                        'Precio más bajo': min_price,
                        'Diferencia': diff_price}
                        ]
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
        gamma_data = [
                    ['Baja', low_actual_relative_value, low_ideal_abs_value, low_ideal_relative_value],
                    ['Media', med_actual_relative_value, med_ideal_abs_value, med_ideal_relative_value],
                    ['Alta', hi_actual_relative_value, hi_ideal_abs_value, hi_ideal_relative_value]
                ]
        gama_data_addional = [{'Ratio intervalo': ratio_intervalo,
                                'Corte gamma baja': low_gamma_cut,
                                'Corte gamma alta': hi_gamma_cut}]
        gamma_df = pd.DataFrame(gamma_data, columns=['Banda', 'Actual %', 'Ideal abs', 'Ideal %'])

        requested_price = (engine_df['precio_venta'].sum() / engine_df['total_venta_producto'].sum())
        offered_avg_price = (engine_df['precio_venta'].sum() / engine_df['nombre_plato'].count())
        ratio_rel_price = (requested_price / offered_avg_price)

        ideal_span_low = 0.90
        ideal_span_hi = 1.00

        action = "Recomendable SUBIR precios" if ratio_rel_price > ideal_span_hi else "Recomendable BAJAR precios" if ratio_rel_price < ideal_span_low else "Recomendable MANTENER precios"

        relacion_data = [
                    ['Relación ideal de precios', ideal_span_low, ideal_span_hi]
                    # ['Nuevo precio ofertado', ]
                ]
        relacion_data_df = pd.DataFrame(relacion_data, columns=['Indicador', 'Ideal min', 'Ideal max'])

        if data_only == False:

            ex = st.expander('Metricas')
            with ex:
                disp, gamma, relacion = st.columns([1,1,1], gap='medium')
                with disp:
                    st.subheader('Dispersión de Precios') 
                    st.metric('Actual',value=disp_metric)
                    st.dataframe(disp_data, hide_index=True,use_container_width=True)
                    st.markdown('Coeficiente ideal entre: *2,50 - 3,00*')
                    # st.divider()
                with gamma:
                    st.subheader('Amplitud de Gamma')
                    low, med, hi = st.columns([1,1,1])
                    with low:
                        st.metric('Banda Baja', low_actual_abs_value)
                    with med:
                        st.metric('Banda Media', med_actual_abs_value)
                    with hi:
                        st.metric('Banda Alta', hi_actual_abs_value)
                    st.dataframe(gamma_df, hide_index=True,use_container_width=True)
                    st.dataframe(gama_data_addional, hide_index=True,use_container_width=True)
                    # st.divider()
                with relacion:
                    st.subheader('Relación Calidad - Precio')
                    rq_price, offe_price, rat_price = st.columns([1,1,1])
                    with rq_price:
                        st.metric('Precio Solicitado', round(requested_price,0))
                    with offe_price:
                        st.metric('Precio ofertado', round(offered_avg_price,0))
                    with rat_price:
                        st.metric('Relación de precios', round(ratio_rel_price,0))

                    st.dataframe(relacion_data_df, hide_index=True,use_container_width=True)

                    st.markdown('*Acción:*')
                    st.markdown(f'**{action}**')
            # with table:
            st.subheader('Tabla de Datos')

            st.dataframe(price_table, hide_index=True,use_container_width=True)

        metric_list = [max_price, 
                       min_price, 
                       diff_price,
                       disp_metric, 
                       low_actual_abs_value,
                       med_actual_abs_value,
                       hi_actual_abs_value,
                       low_ideal_abs_value,
                       med_ideal_abs_value,
                       hi_ideal_abs_value,
                       ratio_rel_price,
                       requested_price,
                       offered_avg_price]

        return metric_list
    
    def engine_dashboard(self):
        engine_df = self.engine_table(data_only=True)
        price_metrics = self.price_fixing(data_only=True)
        disp_coefficient = price_metrics[3]
        min_disp_coeff = price_metrics[1]
        max_disp_coeff = price_metrics[0]
        diff_disp_coeff = price_metrics[2]

        total_products =len(engine_df['nombre_plato'].unique())
        avg_perc_cost = engine_df['coste_producto_porcentage'].mean()
        avg_benefit = engine_df['margen_contribucion'].mean()
        classification_data = engine_df['clasificación']
        metric_1, metric_2, metric_3 = st.columns([1,1,1])
        with metric_1:
            st.metric('Número de productos',total_products)
        with metric_2:
            st.metric('% Coste medio',round(avg_perc_cost,2))
        with metric_3:
            st.metric('Beneficio medio',round(avg_benefit,2))

        colors = {'PERRO': 'red', 'VACA': 'blue', 'ESTRELLA': 'green', 'ENIGMA': 'yellow'}
        count_values = classification_data.value_counts().reset_index()
        count_values.columns = ['Clasificación', 'Total']
        plot_1, plot_2 = st.columns([1,1])
        with plot_1:
            bar_char = px.bar(count_values, 
                              x='Clasificación', 
                              y = 'Total', 
                              color="Clasificación", 
                              color_discrete_map=colors, 
                              title="Clasificación de Platos Oz", 
                              labels={'Total': 'Total'})
            bar_char.update_layout(showlegend=True, 
                                   bargap=0.3,
                                   bargroupgap=0.3)
            st.plotly_chart(bar_char, use_container_width=True)
        with plot_2:
            pie_char = px.pie(classification_data, 
                              names='clasificación', 
                              title="Clasificación porcentual de Platos Oz", 
                              hole=.6,
                              color_discrete_sequence=['yellow', 'green', 'blue', 'red'])
            pie_char.update_traces(hoverinfo="percent+name")
            pie_char.update_layout(showlegend=True, annotations=[dict(text='TIPO DE PLATO', x=0.50, y=0.5, font_size=22, showarrow=False)])
            st.plotly_chart(pie_char, use_container_width=True)
        
        # st.dataframe(price_metrics)

        disp_exp = st.expander('Dispersión de Precios')
        with disp_exp:
            disp_metric, plot_metric = st.columns([1,1])
            with disp_metric:
                st.subheader('Dispersión de Precios')
                st.metric('Coeficiente:',disp_coefficient)
            with plot_metric:
                data = {'Categoría': ['Precio más bajo', 'Precio más alto', 'Diferencia'],
                        'Cuenta': [min_disp_coeff, max_disp_coeff, diff_disp_coeff]}
                df_bar = pd.DataFrame(data)

                bar_char_disp = px.bar(df_bar, 
                                       x='Cuenta', 
                                       y='Categoría', 
                                       title='Dispersión de Precios',
                                       orientation='h',
                                       color='Categoría',
                                       color_discrete_map={'Precio más bajo':'green', 'Precio más alto':'red', 'Diferencia':'blue'})
                bar_char_disp.update_layout(showlegend=True, 
                                   bargap=0.4,
                                   bargroupgap=0.4)
                st.plotly_chart(bar_char_disp, use_container_width=True)



        # st.dataframe(engine_df)

        

        
        