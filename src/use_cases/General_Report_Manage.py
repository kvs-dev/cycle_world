from abc import ABC, abstractmethod
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
from matplotlib import cm
from use_cases.DTOs.Label import Label

class Show(ABC):
    @abstractmethod
    def render(self) -> None:
        pass

class Pagination(Show):
    def render(self,st:st,how_many_pages:int,middle:int, total_records:int, min_value:int, step:int, data:pd.DataFrame):

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


        with bottom_menu[1]:
            total_pages = max(1, int(total_records / st.session_state.batch_size))
            current_page = st.number_input(
                "Page", min_value=min_value, max_value=total_pages, step=step,
                value=st.session_state.current_page,
                key="page_number"
            )
            if current_page != st.session_state.current_page:
                st.session_state.current_page = current_page
                st.rerun()

        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** - Total records: **{total_records}**")


        pagination = st.container()

        pagination.dataframe(data=data, use_container_width=True, hide_index=True)

class Download_Excel(Show):
    def __init__(self, buffer: io.BytesIO, filename: str, label:str, dataframe: pd.DataFrame) -> None:
        self.buffer = Download_Excel.__create_excel_file(dataframe=dataframe, filename=filename, buffer=buffer)
        self.filename = filename
        self.label = label

    @staticmethod
    def __create_excel_file(dataframe:pd.DataFrame, filename: str, buffer:io.BytesIO) -> io.BytesIO:

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name=filename)
            writer.close()
        buffer.seek(0)
        return buffer

    def render(self, st:st) -> None:
        st.download_button(
            label=self.label,
            data=self.buffer,
            file_name=self.filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )



class Bar_chart(Show):
    def __init__(self, data: pd.DataFrame, plt: plt, np:np):
        self.data = data
        self.plt = plt
        self.np = np

    def render(self, subheader:str, cm:cm, title: str, st:st, label:Label  ):
        if 'SECTOR_NAME' in self.data.columns and 'BIKE_COLOR' in self.data.columns:
            st.subheader(subheader)

        counts = self.data.groupby(['SECTOR_NAME', 'BIKE_COLOR']).size().reset_index(name='COUNT')

        sector_map = {sector: i for i, sector in enumerate(sorted(counts['SECTOR_NAME'].unique()))}
        color_map = {color: i for i, color in enumerate(sorted(counts['BIKE_COLOR'].unique()))}

        counts['SECTOR_NUM'] = counts['SECTOR_NAME'].map(sector_map)
        counts['COLOR_NUM'] = counts['BIKE_COLOR'].map(color_map)

        fig = self.plt.figure(figsize=(20, 12))
        ax = fig.add_subplot(projection='3d')

        x = counts['SECTOR_NUM']
        y = counts['COLOR_NUM']
        z = self.np.zeros_like(counts['COUNT'])
        dx = dy = 0.5
        dz = counts['COUNT']

        num_barras = len(dz)
        colores = cm.get_cmap('tab20', num_barras)(range(num_barras))  

        ax.bar3d(x, y, z, dx, dy, dz, color=colores, alpha=0.8)


        ax.set_xlabel(label.x_label)
        ax.set_ylabel(label.y_label)
        ax.set_zlabel(label.z_label)

        xticks = list(sector_map.values())
        xlabels = list(sector_map.keys())
        skip = 2 if len(xlabels) > 15 else 1

        ax.set_xticks(xticks[::skip])
        ax.set_xticklabels(xlabels[::skip], rotation=60, ha='right', fontsize=7)

        ax.set_yticks(list(color_map.values()))
        ax.set_yticklabels(list(color_map.keys()), rotation=45, ha='right', fontsize=8)

        self.plt.title(title)
        self.plt.tight_layout()
        st.pyplot(fig)