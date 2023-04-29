from Class.ConnectionDB import ConnectionDB
from st_aggrid import GridOptionsBuilder 
from st_aggrid import AgGrid 
from st_aggrid import GridUpdateMode
from st_aggrid import ColumnsAutoSizeMode
from st_aggrid import AgGridTheme
import pandas as pd 
import streamlit as st
import time


con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()


# Define the Streamlit Stock Process
class StreamlitStockProcess:
    def __init__(self, con):
        self.con = con

    def stock_data(self):
        # Load the product data
        stock_data = pd.read_sql(
        '''
        SELECT *
        FROM inventario
        ''', cursor)

        stock_data = stock_data.rename(
                                    columns=lambda x: x
                                    .upper()
                                    .replace('_', ' ')
                                    )
        stock_data['EXISTENCIAS'] = stock_data['EXISTENCIAS'].fillna(0.0)
        
        return stock_data
    def create_grid_stock_table(self, stock_data_frame):
        st.subheader('Tabla de Inventario')
        # stock_data_frame = self.stock_data()
        gob = GridOptionsBuilder.from_dataframe(stock_data_frame)

        # set the update mode to 'ValueChange' to update the table on input chang
        gob.configure_grid_options(domLayout='normal', 
                                enableSorting=True, 
                                enableFilter=True, 
                                enableColResize=True,
                                enableRangeSelection=True, 
                                rowSelection='single', 
                                editable=True, 
                                enableCellChangeFlash=True)

        gob.configure_default_column(cellStyle={'font-size': '12px'}, 
                                    suppressMenu=True, 
                                    wrapHeaderText=True, 
                                    autoHeaderHeight=True
                                   )
        
        # create the agGrid table
        ag_grid = AgGrid(data = stock_data_frame,
        gridOptions=gob.build(),
        height='500px',
        fit_columns_on_grid_load = True, 
        updateMode=GridUpdateMode.VALUE_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        reload_data=True,
        allow_unsafe_jscode=True
        )

        # get the selected row from the table
        selected_row = ag_grid['selected_rows']
        # check if a row is selected
        if selected_row:
        # get the selected row from the table
            # get the values of the selected row
            row_values = selected_row[0]
            # display the values in the input fields
            stock_id = row_values['ID']
            stock_name = row_values['NOMBRE']
            stock_family = row_values['FAMILIA']
            stock_provider = row_values['PROVEEDOR']
            stock_price = row_values['PRECIO COMPRA']
            stock_weight = row_values['PESO BRUTO']
            stock_merma = row_values['MERMA']
            stock_amount = row_values['EXISTENCIAS']


            with st.form(key='update_form', clear_on_submit=True):
                st.write('Update Inventario')
                # updated_id = st.number_input('ID', value=stock_id)
                updated_name = st.text_input('NOMBRE', value = stock_name)
                updated_family = st.text_input('FAMILIA', value= stock_family)
                updated_provider = st.text_input('PROVEEDOR', value= stock_provider)
                updated_price = st.number_input('PRECIO DE COMPRA', value= float(stock_price), format='%f')
                updated_weight = st.number_input('PESO BRUTO', value= float(stock_weight), format='%f')
                updated_merma = st.number_input('MERMA', value= stock_merma)
                updated_amount = st.number_input('EXISTENCIAS', value=float(stock_amount), format='%f')
                update_button = st.form_submit_button(label='Update producto')

            if update_button:
                # execute a query to update the row in the table
                cursor.execute(f'''
                UPDATE inventario 
                SET 
                nombre='{updated_name}', 
                familia='{updated_family}', 
                proveedor='{updated_provider}',
                precio_compra='{updated_price}',
                peso_bruto='{updated_weight}',
                merma='{updated_merma}', 
                existencias='{updated_amount}'
                WHERE id={stock_id}
                ''')

                # display a success message
                st.success('producto Actualizado!')
                time.sleep(2)
                st.experimental_rerun()

    def search_stock_engine(self):
        search_term = st.text_input('Buscar Artículo')
        df_table = self.stock_data()
        m1 = df_table["NOMBRE"].str.lower().str.contains(search_term.lower())
        m2 = df_table["FAMILIA"].str.lower().str.contains(search_term.lower())
        m3 = df_table['PROVEEDOR'].str.lower().str.contains(search_term.lower())
        df_search = df_table[m1 | m2 | m3]
        if search_term:
            # st.write(df_search)
            self.create_grid_stock_table(stock_data_frame=df_search)
        else:
            self.create_grid_stock_table(stock_data_frame=df_table)
