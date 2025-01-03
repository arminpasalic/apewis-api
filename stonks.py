import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time

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

st.set_page_config(layout="wide")

# Initialize session state
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
    st.session_state.api = ApeWisdomAPI(rate_limit=1.0)
    st.session_state.data = None

st.title('Stock Mentions Dashboard')

# Calculate time elapsed and update data if needed
elapsed = datetime.now() - st.session_state.start_time
if elapsed.total_seconds() >= 300:  # 5 minutes
    st.session_state.data = st.session_state.api.get_mentions()
    st.session_state.start_time = datetime.now()

# Display countdown
time_left = 300 - elapsed.total_seconds()
if time_left > 0:
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    st.markdown(f"### Next update in: {minutes:02d}:{seconds:02d}")
else:
    st.markdown("### Updating...")

# Display data
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data['results'])
    
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
