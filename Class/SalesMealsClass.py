from Class.ConnectionDB import ConnectionDB
from st_aggrid import GridOptionsBuilder 
from st_aggrid import AgGrid 
from st_aggrid import GridUpdateMode
from st_aggrid import ColumnsAutoSizeMode
from st_aggrid import AgGridTheme
from pandas_profiling import ProfileReport
import pandas as pd 
import streamlit as st
import time

con = ConnectionDB('DB/engineMenu_v43.db')
cursor = con.cursor()

class StreamlitSalesMealsClass:
    def __init__(self, con):
        self.con = con

    def sales_data(self):
        sales_data = pd.read_sql(
            '''
            SELECT * 
            FROM ventas_productos 
            ''', cursor)
        
        sales_data = sales_data.rename(
                                    columns=lambda x: x
                                    .upper()
                                    .replace('_', ' ')
                                    )
        return sales_data
    

    def display_data(self):
            # Create a file uploader
        st.subheader("Meal Sales")
        uploaded_file = st.file_uploader("Upload Sales File", type=["xlsx", "xls"])
        if uploaded_file is not None:
            file_path = f"Uploads/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            sales_data_xls = pd.read_excel(file_path, sheet_name='Hoja1')
            sales_data_xls = sales_data_xls.rename(columns={"Codigo": "id"})
            df = pd.read_sql("SELECT id FROM platos", cursor)
            sales_df = pd.merge(sales_data_xls, df, on='id')
            cursor.execute("INSERT INTO ventas_productos SELECT * FROM sales_df;")
            st.success("Sales uploaded successfully!")
        sales_data = self.sales_data()
        st.dataframe(sales_data, use_container_width=True, hide_index=True)
    
