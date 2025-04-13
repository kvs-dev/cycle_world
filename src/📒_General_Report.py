import streamlit as st
import pandas as pd
import io
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from adapaters.General_Report_Service import General_Report
from use_cases.General_Report_Manage import Pagination, Download_Excel, Bar_chart
from use_cases.DTOs.Label import Label_Implementation

def parse_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if 'START_DATE' in df.columns:
        df['START_DATE'] = pd.to_datetime(df['START_DATE']).dt.strftime('%d-%m-%Y')
    if 'END_DATE' in df.columns:
        df['END_DATE'] = pd.to_datetime(df['END_DATE']).dt.strftime('%d-%m-%Y')
    return df

def create_excel_file(dataframe:pd.DataFrame, filename: str, buffer:io.BytesIO) -> io.BytesIO:

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name=filename)
        writer.close()
    buffer.seek(0)
    return buffer

def count_pages(df):
    count = []
    df_length = len(df)
    for index in range(1, df_length + 1):
        if df_length % index == 0:
            count.append(index)
    return count

def who_is_middle(pages: int):
    return int(len(pages) / 2)

conn = st.connection("snowflake")

st.title("Cycle World Database")
st.write('View to present an overview report of Cycle World')

keyword_search_general_report = st.text_input("Search", placeholder='search by station, sector and bike color...')

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

query = General_Report(conn=conn)
_, full_count = query.get(page=1, batch_size=1, keyword_search_general_report=keyword_search_general_report)

if full_count == 0:
    st.info("Data not found, please check the spelling of the search term.")
    st.stop()

how_many_pages = count_pages(pd.DataFrame(index=range(full_count)))
middle = who_is_middle(how_many_pages)

df, total_records = query.get(page=st.session_state.current_page, batch_size=st.session_state.batch_size, keyword_search_general_report=keyword_search_general_report)

df = parse_dataframe(df)

if not df.empty:

    show_pagination = Pagination()
    show_pagination.render(st, how_many_pages, middle, total_records, 1, 1, df)

    show_excel_download_button = Download_Excel(buffer=io.BytesIO(), filename="general_report_page.xlsx", label="Download to Excel File!!!", dataframe=df)
    show_excel_download_button.render(st)

    label = Label_Implementation(x_label="Sector", y_label="Color", z_label="Amount")
    show_bar_chart = Bar_chart(data=df, plt=plt, np=np)
    show_bar_chart.render(subheader="Sector and Color of Bicycle", cm=cm, title="Number of bicycles by Sector and Color", st=st, label=label)

else:
    st.info('Data not found, please check the spelling of the search term.')
