from abc import ABC, abstractmethod
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
from use_cases.DTOs.Legend import Legend
from use_cases.DTOs.Ax_Label import AX_Label

class Show(ABC):
    @abstractmethod
    def render(self) -> None:
        pass

class Download_Excel(Show):
    def __init__(self, buffer: io.BytesIO, filename: str, label:str) -> None:
        self.buffer = buffer
        self.filename = filename
        self.label = label

    def render(self, st:st) -> None:
        st.download_button(
            label=self.label,
            data=self.buffer,
            file_name=self.filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

class Pagination(Show):
    def __init__(self, how_many_pages:int, middle:int, dataframe: pd.DataFrame, min_value: int,step:int) -> None:
        self.how_many_pages = how_many_pages
        self.middle = middle
        self.df = dataframe
        self.min_value = min_value
        self.step = step

    @staticmethod
    def __split_frame(input_df: pd.DataFrame, rows) -> pd.DataFrame:
        df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
        return df

    def render(self, st:st, pagination:DeltaGenerator) -> None:
        bottom_menu = st.columns((4, 2, 1))
        with bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=self.how_many_pages, index=self.middle)
        with bottom_menu[1]:

            total_pages = (
                int(len(self.df) / batch_size) if int(len(self.df) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page", min_value=self.min_value, max_value=total_pages, step=self.step
            )
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")


        pages = self.__split_frame(self.df, batch_size)
        pagination.dataframe(data=pages[current_page - 1], use_container_width=True, hide_index=True)  


class Map(Show):
    def __init__(self, keyword_search_general_report: str, dataframe:pd.DataFrame, zoom:int) -> None:
        self.keyword_search_general_report = keyword_search_general_report
        self.stations = dataframe
        self.zoom = zoom

    def render(self, st:st) -> None:
        if self.keyword_search_general_report:
            st.map(data=self.stations, zoom=self.zoom, use_container_width=True)

class Pie_Chart(Show):
    def __init__(self, dataframe: pd.DataFrame, plt: plt, np: np) -> None:
        self.dataframe = dataframe
        self.plt = plt
        self.np = np

    def render(self, color_mapping: object, legend:Legend, title:str, st:st) -> None:
        bike_color_counts = self.dataframe['BIKE_COLOR'].value_counts()

        fig, ax = self.plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))

        pie_colors = [color_mapping[color] for color in bike_color_counts.index]

        total = sum(bike_color_counts.values)
        percentages = [(count/total)*100 for count in bike_color_counts.values]
        absolute_values = bike_color_counts.values

        def func(pct, allvals):
            absolute = int(self.np.round(pct/100.*np.sum(allvals)))
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
            title=legend.title,
            loc=legend.loc,
            bbox_to_anchor=(1.1, 1)
        )


        st.write(f"## {title}")
        st.pyplot(fig)
      
class Bar_Chart(Show):
    def __init__(self, dataframe: pd.DataFrame, plt:plt):
        self.df = dataframe
        self.plt = plt
    
    def render(self, st:st, title:str, colors: object, ax_label:AX_Label):
        st.write(f"## {title}")

        timezone_counts = self.df.groupby('TIMEZONE')['BICYCLES_THAT_ARRIVED'].sum()

        fig, ax = self.plt.subplots(figsize=(10, 6))

        timezones = timezone_counts.index.tolist() 
        counts = timezone_counts.values 

        bar_colors = [colors.get(tz, 'tab:gray') for tz in timezones]

        ax.bar(timezones, counts, color=bar_colors)

        ax.set_xlabel(ax_label.x_label)
        ax.set_ylabel(ax_label.y_label)
        ax.set_title(ax_label.title)

        for i, v in enumerate(counts):
            ax.text(i, v + 0.1, str(v), ha='center')

        self.plt.tight_layout()

        st.pyplot(fig)