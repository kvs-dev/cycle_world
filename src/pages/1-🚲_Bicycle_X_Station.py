import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io

st.title("Report bicycle station data")
st.write('This report shows the data of bicycles by station.')

conn = st.connection("snowflake")
buffer = io.BytesIO()

keyword_search_general_report = st.text_input("Search", placeholder='search by sector...', value='Marylebone')

if keyword_search_general_report =='Marylebone':
    st.info('Delete the search term to see all information.')

def load_table():
    session = conn.session()
    if keyword_search_general_report:
        return session.sql(f"SELECT * FROM table(SEARCH_IN_STATIONXBICYCLE_REPORT('{keyword_search_general_report.title()}'))").to_pandas()
    return session.table('CYCLE_WORLD.ENHANCED.STATIONXBICYCLE').to_pandas()



@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df

session = conn.session()
df = load_table()

with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='General Report')
    writer.close()

buffer.seek(0)

stations = []
if keyword_search_general_report:
    stations_name = df['STATION_NAME'].unique()
    stations_dfs = []

    for station in stations_name:
        safe_station = station.title().replace("'", "''")
        sql_query = session.sql(f"SELECT * FROM table(SEARCH_IN_STATIONS('{safe_station}'))")
        result_df = sql_query.to_pandas()
        stations_dfs.append(result_df)

    if stations_dfs:
        stations = pd.concat(stations_dfs, ignore_index=True)
        stations['LATITUDE'] = stations['LATITUDE'].str.replace(',', '.').astype(float)
        stations['LONGITUDE'] = stations['LONGITUDE'].str.replace(',', '.').astype(float)
    else:
        stations = pd.DataFrame()


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

pagination = st.container()
how_many_pages = count_pages(df)
middle = who_is_middle(how_many_pages)

if not df.empty:
    st.download_button(
        label="Download to Excel file!!!",
        data=buffer,
        file_name="report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    bottom_menu = st.columns((4, 2, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox("Page Size", options=how_many_pages, index=middle)
    with bottom_menu[1]:

        total_pages = (
            int(len(df) / batch_size) if int(len(df) / batch_size) > 0 else 1
        )
        current_page = st.number_input(
            "Page", min_value=1, max_value=total_pages, step=1
        )
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}** ")


    pages = split_frame(df, batch_size)
    pagination.dataframe(data=pages[current_page - 1], use_container_width=True, hide_index=True)

    if keyword_search_general_report:
        st.map(data=stations, zoom=12, use_container_width=True)

    bike_color_counts = df['BIKE_COLOR'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))


    color_mapping = {
    'Red': 'red',
    'Yellow': 'gold',
    'Green': 'green',
    'Blue': 'blue',
    'Black': 'black'
    }

    pie_colors = [color_mapping[color] for color in bike_color_counts.index]

    total = sum(bike_color_counts.values)
    percentages = [(count/total)*100 for count in bike_color_counts.values]
    absolute_values = bike_color_counts.values

    def func(pct, allvals):
        absolute = int(np.round(pct/100.*np.sum(allvals)))
        return f"{pct:.1f}%\n({absolute})"

    wedges, texts, autotexts = ax.pie(
        bike_color_counts.values,
        colors=pie_colors,
        autopct=lambda pct: func(pct, bike_color_counts.values),
        textprops=dict(color="w", weight="bold")
    )

    ax.legend(
        wedges, 
        bike_color_counts.index,
        title="Bike Colors",
        loc="upper right",
        bbox_to_anchor=(1.1, 1)
    )


    st.write("## Journeys by bicycle color")
    st.pyplot(fig)





    st.write("## Journeys by timezone")

    timezone_counts = df.groupby('TIMEZONE')['BICYCLES_THAT_ARRIVED'].sum()

    fig, ax = plt.subplots(figsize=(10, 6))

    timezones = timezone_counts.index.tolist() 
    counts = timezone_counts.values 

    colors = {'Morning': 'tab:orange', 'Valley': 'tab:green', 'Afternoon': 'tab:blue'}
    bar_colors = [colors.get(tz, 'tab:gray') for tz in timezones]

    ax.bar(timezones, counts, color=bar_colors)

    ax.set_xlabel('Timezone')
    ax.set_ylabel('Number of bicycles')
    ax.set_title('Number of bicycles arriving by timezone')

    for i, v in enumerate(counts):
        ax.text(i, v + 0.1, str(v), ha='center')

    plt.tight_layout()

    st.pyplot(fig)
else:
    st.info('Data not found, please check the spelling of the search term.')








