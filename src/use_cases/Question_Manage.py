from abc import ABC, abstractmethod
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Show(ABC):
    @abstractmethod
    def render(self) -> None:
        pass

class Crowded_Stations(Show):
    def render(self, stations_df: pd.DataFrame, numpy:np, plt:plt, streamlit:st) -> None:
        """
        Renders the most crowded stations in a horizontal bar chart.
        """
        streamlit.title("🚴‍♂️ Top 10 Most Crowded Stations")

        stations = stations_df["STATION_NAME"].values
        y_pos = numpy.arange(len(stations))
        journeys = stations_df["JOURNEYS_TOTAL"].values

        fig, ax = plt.subplots(figsize=(8, len(stations) * 0.4)) 

        colors = plt.cm.viridis(numpy.linspace(0, 1, len(stations_df)))
        ax.barh(y_pos, journeys, align='center', color=colors)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(stations)
        ax.invert_yaxis() 
        ax.set_xlabel('Total Journeys')
        ax.set_title('Journeys by station')

        streamlit.pyplot(fig, use_container_width=True)

class Cards(Show):
    def render(self, percentage_by_journeys: pd.DataFrame, avg_journey_duration: pd.DataFrame, bike_color:pd.DataFrame, stations_without_bicycles:pd.DataFrame, st:st ) -> None:
        """
        Renders the cards for the metrics.
        """
        with st.container():
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.metric(
                    label="☔ Percentage of Journeys on Rainy Days",
                    value=f"{percentage_by_journeys['PERCENTAGE_TRAVEL_RAINY_DAYS'][0]:.2f}%"
                )

            with col2:
                st.metric(
                    label="☀️ Average Journey Duration on Clear Days",
                    value=f"{avg_journey_duration['AVG_MINUTES'][0]:.2f} minutes"
                )

            col3, col4 = st.columns([1, 1])

            with col3:
                st.metric(
                    label="🚲 Most Common Bike Color",
                    value=bike_color['BIKE_COLOR'][0],
                )

            with col4:
                st.metric(
                    label="🚲 Less Common Bike Color",
                    value=bike_color['BIKE_COLOR'][len(bike_color)-1],
                )

            col4, col5 = st.columns([1, 1])
            with col4:
                st.metric(
                    label="🏬 Ever a day with no bikes available at a station?",
                    value=f"{stations_without_bicycles['HAVE_DAY_NO_BICYCLES'][0]}"
                )