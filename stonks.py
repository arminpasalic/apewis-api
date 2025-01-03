import streamlit as st
import plotly.express as px
import requests
from typing import Dict
import pandas as pd
import time

class ApeWisdomAPI:
    # The base URL for the API endpoints
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        """
        Fetch stock mentions data from the API
        
        Args:
            filter_type: Type of stocks to filter (e.g., "all-stocks")
            page: Page number for pagination
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

# Configure the Streamlit page
st.set_page_config(layout="wide")

# Initialize API client
api = ApeWisdomAPI()

# Title
st.title('Stock Mentions Dashboard')

# Timer fragment
with st.fragment(key="timer_fragment"):
    # Initialize start time if not already in session state
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    
    # Calculate elapsed time
    elapsed_time = time.time() - st.session_state.start_time
    
    # Reset start time and fetch new data if 5 minutes have passed
    if elapsed_time >= 300:  # 300 seconds = 5 minutes
        st.session_state.start_time = time.time()
        st.session_state.data = None  # Force data refetch
    
    # Display remaining time until next refresh
    remaining_time = max(0, 300 - elapsed_time)
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    
    # Display timer
    st.markdown(f"### Next update in: {minutes:02d}:{seconds:02d}")
    
    # Sleep for 1 second and rerun the fragment
    time.sleep(1)
    st.rerun(scope="fragment")

# Main content
try:
    # Fetch stock mentions data if not already fetched or expired
    if 'data' not in st.session_state or st.session_state.data is None:
        st.session_state.data = api.get_mentions()
    
    # Create DataFrame from API results
    df = pd.DataFrame(st.session_state.data['results'])
    
    # Create two-column layout for first two visualizations
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

except Exception as e:
    st.error(f"Error fetching stock mentions: {str(e)}")
