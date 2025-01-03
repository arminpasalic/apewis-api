import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time
import threading
from queue import Queue
import schedule

class ApeWisdomAPI:
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
        
    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        self._rate_limit_wait()
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

class DataFetcher:
    def __init__(self):
        self.data_queue = Queue()
        self.api = ApeWisdomAPI(rate_limit=1.0)
        self.last_update = None
        
    def fetch_data(self):
        """Fetch data in a separate thread"""
        data = self.api.get_mentions()
        self.data_queue.put(data)
        self.last_update = datetime.now()
        
    def get_last_update(self):
        return self.last_update

def initialize_session_state():
    """Initialize all session state variables"""
    if 'data_fetcher' not in st.session_state:
        st.session_state.data_fetcher = DataFetcher()
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None

def update_data():
    """Update data if 5 minutes have passed"""
    if (st.session_state.last_update is None or 
        (datetime.now() - st.session_state.last_update).total_seconds() >= 300):
        
        # Start data fetch in background
        fetch_thread = threading.Thread(
            target=st.session_state.data_fetcher.fetch_data
        )
        fetch_thread.start()
        fetch_thread.join(timeout=0.1)  # Short timeout to prevent blocking
        
        # Check if new data is available
        try:
            while not st.session_state.data_fetcher.data_queue.empty():
                st.session_state.current_data = st.session_state.data_fetcher.data_queue.get_nowait()
                st.session_state.last_update = datetime.now()
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")

def main():
    st.set_page_config(layout="wide")
    initialize_session_state()
    
    st.title('Stock Mentions Dashboard')
    
    # Update data if needed
    update_data()
    
    # Display countdown
    if st.session_state.last_update:
        elapsed = datetime.now() - st.session_state.last_update
        time_left = max(300 - elapsed.total_seconds(), 0)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        st.markdown(f"### Next update in: {minutes:02d}:{seconds:02d}")
        
        if st.session_state.current_data:
            df = pd.DataFrame(st.session_state.current_data['results'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(px.bar(
                    df.head(10),
                    x='ticker',
                    y='mentions',
                    title='Top 10 Most Mentioned Stocks'
                ), use_container_width=True)
            
            with col2:
                st.plotly_chart(px.scatter(
                    df.head(20),
                    x='mentions',
                    y='upvotes',
                    text='ticker',
                    title='Mentions vs Upvotes'
                ), use_container_width=True)
            
            df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
            st.plotly_chart(px.bar(
                df.head(10),
                x='ticker',
                y='mention_change',
                title='24h Change in Mentions'
            ), use_container_width=True)
    else:
        st.markdown("### Initializing data...")
        update_data()

if __name__ == "__main__":
    main()
