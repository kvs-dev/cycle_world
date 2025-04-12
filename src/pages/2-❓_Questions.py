import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

conn = st.connection("snowflake")

@st.cache_data(ttl=3600)
def get_stattions_more_crowded():

    session = conn.session()
    query = """
    WITH station_traffic AS (
        SELECT START_STATION_ID AS station_id, COUNT(*) AS start_count
        FROM CYCLE_WORLD.RAW.JOURNEYS
        GROUP BY START_STATION_ID
        
        UNION ALL
        
        SELECT END_STATION_ID AS station_id, COUNT(*) AS end_count
        FROM CYCLE_WORLD.RAW.JOURNEYS
        GROUP BY END_STATION_ID
    ),
    total_station_traffic AS (
        SELECT 
            station_id, 
            SUM(start_count) AS total_traffic
        FROM station_traffic
        GROUP BY station_id
    )

    SELECT 
        s.STATION_NAME,
        t.total_traffic AS journeys_total
    FROM total_station_traffic t
    JOIN CYCLE_WORLD.RAW.STATIONS s ON t.station_id = s.STATION_ID
    ORDER BY journeys_total DESC
    LIMIT 10
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=3600)
def get_percentage_by_journeys():
    session = conn.session()
    query = """
    WITH daily_weather AS (
    SELECT 
        DATE(datetime) as date,
        MAX(CASE WHEN weather IN ('Light snow or light rain', 'Heavy rain or snow, hail or thunderstorm') THEN 1 ELSE 0 END) as was_raining
    FROM weather
    GROUP BY DATE(datetime)
    )

    SELECT 
        (SELECT COUNT(*) 
        FROM journeys js
        JOIN daily_weather dw ON DATE(js.start_date) = dw.date
        WHERE dw.was_raining = 1
        ) * 100.0 / 
    (SELECT COUNT(*) FROM journeys) AS percentage_travel_rainy_days
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=3600)
def get_avg_journey_duration():
    session = conn.session()
    query = """
    WITH daily_weather AS (
    SELECT 
        DATE(datetime) as date,
        MAX(CASE WHEN weather = 'Clear to partly cloudy' THEN 1 ELSE 0 END) as clear
    FROM CYCLE_WORLD.RAW.WEATHER
    GROUP BY DATE(datetime)
    )
    SELECT 
    AVG(journey_duration) AS avg_minutes
    FROM CYCLE_WORLD.RAW.JOURNEYS js
    JOIN daily_weather dw
    ON DATE(js.start_date) = dw.date
    WHERE dw.clear = 1
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=3600)
def get_bike_color():
    session = conn.session()
    query = """
    select bike_color,count(*) as total from CYCLE_WORLD.RAW.BIKES GROUP BY bike_color ORDER BY TOTAL DESC;
    """
    return session.sql(query).to_pandas()

df = get_stattions_more_crowded()


st.title("🚴‍♂️ Top 10 Most Crowded Stations")

stations = df["STATION_NAME"].values
y_pos = np.arange(len(stations))
journeys = df["JOURNEYS_TOTAL"].values

# Crear la figura
fig, ax = plt.subplots(figsize=(8, len(stations) * 0.4))  # Ajustar altura

colors = plt.cm.viridis(np.linspace(0, 1, len(df)))
ax.barh(y_pos, journeys, align='center', color=colors)

ax.set_yticks(y_pos)
ax.set_yticklabels(stations)
ax.invert_yaxis()  # Estaciones desde la más usada arriba
ax.set_xlabel('Total Journeys')
ax.set_title('Journeys by station')

# Mostrar en Streamlit
st.pyplot(fig, use_container_width=True)


percentage_by_journeys = get_percentage_by_journeys()
avg_journey_duration = get_avg_journey_duration()
bike_color = get_bike_color()

with st.container():
    # Primera fila
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
            delta=float(bike_color['TOTAL'][0])
        )

    with col4:
        st.metric(
            label="🚲 Less Common Bike Color",
            value=bike_color['BIKE_COLOR'][len(bike_color)-1],
            delta=float(bike_color['TOTAL'][len(bike_color)-1])
        )

