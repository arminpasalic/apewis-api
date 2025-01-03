import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time

class ApeWisdomAPI:
    # The base URL for the API endpoints
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize the API client with rate limiting
        
        Args:
            rate_limit: Minimum time (in seconds) between API requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """
        Implements rate limiting by waiting if needed before making a new request
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        """
        Fetch stock mentions data from the API
        
        Args:
            filter_type: Type of stocks to filter (e.g., "all-stocks")
            page: Page number for pagination
            
        Returns:
            Dictionary containing the API response
        """
        self._rate_limit_wait()
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

# Configure the Streamlit page
st.set_page_config(layout="wide")

# Initialize session state for persistent data
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
    st.session_state.api = ApeWisdomAPI(rate_limit=1.0)
    st.session_state.data = None

st.title('Stock Mentions Dashboard')

# Calculate time elapsed and update data if needed
elapsed = datetime.now() - st.session_state.start_time
UPDATE_INTERVAL = 300  # 5 minutes in seconds

if elapsed.total_seconds() >= UPDATE_INTERVAL:
    st.session_state.data = st.session_state.api.get_mentions()
    st.session_state.start_time = datetime.now()

# Display countdown timer
time_left = UPDATE_INTERVAL - elapsed.total_seconds()
if time_left > 0:
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    st.markdown(f"### Next update in: {minutes:02d}:{seconds:02d}")
else:
    st.markdown("### Updating...")

# Display visualizations if data is available
if st.session_state.data:
    # Create DataFrame from API results
    df = pd.DataFrame(st.session_state.data['results'])
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    # Top mentions bar chart
    with col1:
        fig1 = px.bar(
            df.head(10),
            x='ticker',
            y='mentions',
            title='Top 10 Most Mentioned Stocks'
        )
        fig1.update_layout(
            xaxis_title="Stock Ticker",
            yaxis_title="Number of Mentions"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Mentions vs Upvotes scatter plot
    with col2:
        fig2 = px.scatter(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',
            title='Mentions vs Upvotes (Top 20 Stocks)'
        )
        fig2.update_layout(
            xaxis_title="Number of Mentions",
            yaxis_title="Number of Upvotes"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 24h Change in Mentions bar chart
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = px.bar(
        df.head(10),
        x='ticker',
        y='mention_change',
        title='24h Change in Mentions (Top 10 Stocks)'
    )
    fig3.update_layout(
        xaxis_title="Stock Ticker",
        yaxis_title="Change in Mentions"
    )
    st.plotly_chart(fig3, use_container_width=True)
