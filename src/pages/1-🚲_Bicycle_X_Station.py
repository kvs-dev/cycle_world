import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
from adapaters.Bicycle_X_Station_Service import BicycleXStation
from snowflake.connector import SnowflakeConnection
from use_cases.Bicycle_X_Station_Manage import Download_Excel, Pagination, Map, Pie_Chart, Bar_Chart
from use_cases.DTOs.Ax_Label import AX_LabelImplementation
from use_cases.DTOs.Legend import LegendImplementation

def create_excel_file(dataframe:pd.DataFrame, filename: str, buffer:io.BytesIO) -> io.BytesIO:

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name=filename)
        writer.close()
    buffer.seek(0)
    return buffer

def parse_stations(stations:pd.DataFrame, keyword_search_general_report:str, connection: SnowflakeConnection, pandas:pd) -> pd.DataFrame:
    if keyword_search_general_report:
        stations_name = stations['STATION_NAME'].unique()
        stations_dfs = []

        for station in stations_name:
            safe_station = station.title().replace("'", "''")
            sql_query = connection.session().sql(f"SELECT * FROM table(SEARCH_IN_STATIONS('{safe_station}'))")
            result_df = sql_query.to_pandas()
            stations_dfs.append(result_df)

        if stations_dfs:
            stations = pandas.concat(stations_dfs, ignore_index=True)
            stations['LATITUDE'] = stations['LATITUDE'].str.replace(',', '.').astype(float)
            stations['LONGITUDE'] = stations['LONGITUDE'].str.replace(',', '.').astype(float)
            return stations
        
        return pandas.DataFrame()
    
def count_pages(df):
    count = []
    df_length = len(df)
    for index in range(1, df_length + 1):
        if df_length % index == 0:
            count.append(index)
    return count

def who_is_middle(pages:int):
    pages_length = len(pages)

    if pages_length % 2 == 0:
        return int(pages_length / 2)
    
    return int(pages_length / 2)



conn = st.connection("snowflake")
buffer = io.BytesIO()

st.title("Report bicycle station data")
st.write('This report shows the data of bicycles by station.')

keyword_search_general_report = st.text_input("Search", placeholder='search by sector...', value='Marylebone')

if keyword_search_general_report =='Marylebone':
    st.info('Delete the search term to see all information.')


query = BicycleXStation(conn=conn)
df = query.get(keyword_search_general_report=keyword_search_general_report)

if not df.empty:

    pagination = st.container()
    how_many_pages = count_pages(df)
    middle = who_is_middle(how_many_pages)
    show_pagination = Pagination(dataframe=df, how_many_pages=how_many_pages, middle=middle, min_value=1, step=1)
    show_pagination.render(st=st, pagination=pagination)

    buffer = create_excel_file(dataframe=df, filename='Report by sector', buffer=buffer)
    show_excel_download_button = Download_Excel(buffer=buffer, filename='report_by_sector.xlsx', label="Download to Excel file!!!")
    show_excel_download_button.render(st=st)

    stations = parse_stations(stations=df, keyword_search_general_report=keyword_search_general_report, connection=conn, pandas=pd)
    show_map = Map(dataframe=stations, keyword_search_general_report=keyword_search_general_report, zoom=12)
    show_map.render(st=st)


    color_mapping = {
    'Red': 'red',
    'Yellow': 'gold',
    'Green': 'green',
    'Blue': 'blue',
    'Black': 'black'
    }

    legend = LegendImplementation(title='Bike Colors', loc='upper right')
    show_pie_chart = Pie_Chart(dataframe=df, plt=plt, np=np)
    show_pie_chart.render(color_mapping=color_mapping, legend=legend, title='Journeys by bicycle color', st=st)


    colors = {'Morning': 'tab:orange', 'Valley': 'tab:green', 'Afternoon': 'tab:blue'}

    show_bar_chart = Bar_Chart(dataframe=df, plt=plt)
    ax_label = AX_LabelImplementation(x_label='Timezone', y_label='Number of bicycles', title='Journeys by timezone')
    show_bar_chart.render(st=st, title='Journeys by timezone', colors=colors, ax_label=ax_label)


else:
    st.info('Data not found, please check the spelling of the search term.')








