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

class General_Report(Query):
    def __init__(self, conn: SnowflakeConnection):
        """
        Initializes the Stations_More_Crowded object with a Snowflake connection.
        """
        super().__init__(conn)
        self.session = conn.session()

    def get(self, page:int, batch_size:int, keyword_search_general_report:str) -> pd.DataFrame:
        """
        Fetches the general report data from Snowflake.
        """
        offset = (page - 1) * batch_size

        if keyword_search_general_report:
            count_query = f"SELECT COUNT(*) as total FROM table(SEARCH_IN_GENERAL_REPORT('{keyword_search_general_report.title()}'))"
            total_count = self.session.sql(count_query).to_pandas().iloc[0]['TOTAL']

            data_query = f"""
                SELECT * FROM table(SEARCH_IN_GENERAL_REPORT('{keyword_search_general_report.title()}'))
                LIMIT {batch_size} OFFSET {offset}
            """
            data = self.session.sql(data_query).to_pandas()
            return data, total_count
        else:
            count_query = "SELECT COUNT(*) as total FROM CYCLE_WORLD.ENHANCED.GENERAL_REPORT"
            total_count = self.session.sql(count_query).to_pandas().iloc[0]['TOTAL']

            data_query = f"""
                SELECT * FROM CYCLE_WORLD.ENHANCED.GENERAL_REPORT
                LIMIT {batch_size} OFFSET {offset}
            """
            data = self.session.sql(data_query).to_pandas()
            return data, total_count