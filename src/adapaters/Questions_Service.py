from abc import ABC, abstractmethod
import pandas as pd
import streamlit as st
from snowflake.connector import SnowflakeConnection

class Query(ABC):
    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Query object with a Snowflake connection.
        """
        self.conn = conn
        self.session = conn.session()
    
    @abstractmethod
    @st.cache_data(ttl=3600)
    def get(self) -> pd.DataFrame:
        """
        Abstract method to be implemented by subclasses to fetch data.
        """
        pass

class Stations_More_Crowded(Query):

    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Stations_More_Crowded object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()

    def get(self) -> pd.DataFrame:
        """
        Fetches the data for the most crowded stations.
        """
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
        return self.session.sql(query).to_pandas()
    
class Percentage_By_Journeys(Query):

    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Stations_More_Crowded object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()
    
    def get(self) -> pd.DataFrame:
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
        return self.session.sql(query).to_pandas()
    
class AVG_JOURNEY_DURATION(Query):

    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Stations_More_Crowded object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()
    
    def get(self) -> pd.DataFrame:
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
        return self.session.sql(query).to_pandas()
    
class Bike_Color(Query):
    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Stations_More_Crowded object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()
    def get(self) -> pd.DataFrame:
        query = """
        select bike_color,count(*) as total from CYCLE_WORLD.RAW.BIKES GROUP BY bike_color ORDER BY TOTAL DESC;
        """
        return self.session.sql(query).to_pandas()