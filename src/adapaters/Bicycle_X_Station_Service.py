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


class BicycleXStation(Query):
    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()

    def get(self, keyword_search_general_report: str) -> pd.DataFrame:
        """
        Fetches data from the bicycle_x_station table.
        """
        if keyword_search_general_report:
            return self.session.sql(f"SELECT * FROM table(SEARCH_IN_STATIONXBICYCLE_REPORT('{keyword_search_general_report.title()}'))").to_pandas()
        return self.session.table('CYCLE_WORLD.ENHANCED.STATIONXBICYCLE').to_pandas()
