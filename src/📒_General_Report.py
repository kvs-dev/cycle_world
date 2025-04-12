import streamlit as st
import pandas as pd
import io
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

conn = st.connection("snowflake")

st.title("Cycle World Database")
st.write('View to present an overview report of Cycle World')

keyword_search_general_report = st.text_input("Search", placeholder='search by station, sector and bike color...')

def load_table(page=1, batch_size=10):
    session = conn.session()
    offset = (page - 1) * batch_size

    if keyword_search_general_report:
        count_query = f"SELECT COUNT(*) as total FROM table(SEARCH_IN_GENERAL_REPORT('{keyword_search_general_report.title()}'))"
        total_count = session.sql(count_query).to_pandas().iloc[0]['TOTAL']

        data_query = f"""
            SELECT * FROM table(SEARCH_IN_GENERAL_REPORT('{keyword_search_general_report.title()}'))
            LIMIT {batch_size} OFFSET {offset}
        """
        data = session.sql(data_query).to_pandas()
        return data, total_count
    else:
        count_query = "SELECT COUNT(*) as total FROM CYCLE_WORLD.ENHANCED.GENERAL_REPORT"
        total_count = session.sql(count_query).to_pandas().iloc[0]['TOTAL']

        data_query = f"""
            SELECT * FROM CYCLE_WORLD.ENHANCED.GENERAL_REPORT
            LIMIT {batch_size} OFFSET {offset}
        """
        data = session.sql(data_query).to_pandas()
        return data, total_count

def count_pages(df):
    count = []
    df_length = len(df)
    for index in range(1, df_length + 1):
        if df_length % index == 0:
            count.append(index)
    return count

def who_is_middle(pages: int):
    return int(len(pages) / 2)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

_, full_count = load_table(page=1, batch_size=1)

if full_count == 0:
    st.info("Data not found, please check the spelling of the search term.")
    st.stop()


how_many_pages = count_pages(pd.DataFrame(index=range(full_count)))
middle = who_is_middle(how_many_pages)

if 'batch_size' not in st.session_state or st.session_state.batch_size not in how_many_pages:
    st.session_state.batch_size = how_many_pages[middle]

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1


bottom_menu = st.columns((4, 2, 1))

with bottom_menu[2]:
    new_batch_size = st.selectbox(
        "Page Size",
        options=how_many_pages,
        index=how_many_pages.index(st.session_state.batch_size),
        key="batch_size_select"
    )
    if new_batch_size != st.session_state.batch_size:
        st.session_state.batch_size = new_batch_size
        st.session_state.current_page = 1
        st.rerun()

df, total_records = load_table(page=st.session_state.current_page, batch_size=st.session_state.batch_size)

with bottom_menu[1]:
    total_pages = max(1, int(total_records / st.session_state.batch_size))
    current_page = st.number_input(
        "Page", min_value=1, max_value=total_pages, step=1,
        value=st.session_state.current_page,
        key="page_number"
    )
    if current_page != st.session_state.current_page:
        st.session_state.current_page = current_page
        st.rerun()

with bottom_menu[0]:
    st.markdown(f"Page **{current_page}** of **{total_pages}** - Total records: **{total_records}**")

if 'START_DATE' in df.columns:
    df['START_DATE'] = pd.to_datetime(df['START_DATE']).dt.strftime('%d-%m-%Y')
if 'END_DATE' in df.columns:
    df['END_DATE'] = pd.to_datetime(df['END_DATE']).dt.strftime('%d-%m-%Y')

pagination = st.container()
if not df.empty:
    pagination.dataframe(data=df, use_container_width=True, hide_index=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Current Page')
    buffer.seek(0)

    st.download_button(
        label="Download to Excel File!!!",
        data=buffer,
        file_name="general_report_page.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    if 'SECTOR_NAME' in df.columns and 'BIKE_COLOR' in df.columns:
        st.subheader("Sector and Color of Bicycle")

        counts = df.groupby(['SECTOR_NAME', 'BIKE_COLOR']).size().reset_index(name='COUNT')

        sector_map = {sector: i for i, sector in enumerate(sorted(counts['SECTOR_NAME'].unique()))}
        color_map = {color: i for i, color in enumerate(sorted(counts['BIKE_COLOR'].unique()))}

        counts['SECTOR_NUM'] = counts['SECTOR_NAME'].map(sector_map)
        counts['COLOR_NUM'] = counts['BIKE_COLOR'].map(color_map)

        fig = plt.figure(figsize=(20, 12))
        ax = fig.add_subplot(projection='3d')

        x = counts['SECTOR_NUM']
        y = counts['COLOR_NUM']
        z = np.zeros_like(counts['COUNT'])
        dx = dy = 0.5
        dz = counts['COUNT']

        num_barras = len(dz)
        colores = cm.get_cmap('tab20', num_barras)(range(num_barras))  

        ax.bar3d(x, y, z, dx, dy, dz, color=colores, alpha=0.8)


        ax.set_xlabel('Sector')
        ax.set_ylabel('Color')
        ax.set_zlabel('Amount')

        xticks = list(sector_map.values())
        xlabels = list(sector_map.keys())
        skip = 2 if len(xlabels) > 15 else 1

        ax.set_xticks(xticks[::skip])
        ax.set_xticklabels(xlabels[::skip], rotation=60, ha='right', fontsize=7)

        ax.set_yticks(list(color_map.values()))
        ax.set_yticklabels(list(color_map.keys()), rotation=45, ha='right', fontsize=8)

        plt.title('Number of bicycles by Sector and Color')
        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info('Data not found, please check the spelling of the search term.')
