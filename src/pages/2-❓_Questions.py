import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from adapaters.Questions_Service import AVG_JOURNEY_DURATION,Stations_More_Crowded, Percentage_By_Journeys, Bike_Color, Stations_No_Bicycles
from use_cases.Question_Manage import Crowded_Stations, Cards

conn = st.connection("snowflake")

query = Stations_More_Crowded(conn=conn)
stations_df = query.get()

show_crowded_stations = Crowded_Stations()
show_crowded_stations.render(stations_df, np, plt, st)

query = Percentage_By_Journeys(conn=conn)
percentage_by_journeys = query.get()

query = AVG_JOURNEY_DURATION(conn=conn)
avg_journey_duration = query.get()

query = Bike_Color(conn=conn)
bike_color = query.get()

query = Stations_No_Bicycles(conn=conn)
stations_without_bicycles = query.get()

show_metrics = Cards()
show_metrics.render(percentage_by_journeys, avg_journey_duration, bike_color, stations_without_bicycles= stations_without_bicycles, st=st)




