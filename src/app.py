import streamlit as st
import pandas as pd
import io

conn = st.connection("snowflake")
buffer = io.BytesIO()

st.title("Cycle World Database")
st.write('View to present an overview report of Cycle World')
keyword_search_general_report = st.text_input("Search", placeholder='search by station, sector and bike color...')
print(buffer.seek(0),'soy buffer')






def load_table():
    session = conn.session()
    if keyword_search_general_report:
        return session.sql(f"SELECT * FROM table(SEARCH_IN_GENERAL_REPORT('{keyword_search_general_report.title()}'))").to_pandas()
    return session.table('CYCLE_WORLD.ENHANCED.GENERAL_REPORT').to_pandas()

@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df


df = load_table()

with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='General Report')
    writer.close()

buffer.seek(0)

if 'START_DATE' in df.columns:
    df['START_DATE'] = pd.to_datetime(df['START_DATE']).dt.strftime('%d-%m-%Y')
if 'END_DATE' in df.columns:
    df['END_DATE'] = pd.to_datetime(df['END_DATE']).dt.strftime('%d-%m-%Y')


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
        label="Download Excel",
        data=buffer,
        file_name="general_report.xlsx",
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
else:
    st.info('Data not found, please check the spelling of the search term.')

