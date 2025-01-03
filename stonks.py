import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time

class ApeWisdomAPI:
    """Handles API interactions with ApeWisdom"""
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
    def _rate_limit_wait(self):
        """Implements rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
        
    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        """Fetches mention data from the API"""
        self._rate_limit_wait()
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

def initialize_session_state():
    """Sets up initial session state variables"""
    if 'api' not in st.session_state:
        st.session_state.api = ApeWisdomAPI(rate_limit=1.0)
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'update_counter' not in st.session_state:
        st.session_state.update_counter = 0

def should_update() -> bool:
    """Determines if it's time for a data update"""
    if st.session_state.last_update is None:
        return True
    elapsed = datetime.now() - st.session_state.last_update
    return elapsed.total_seconds() >= 300  # 5 minutes

def update_data():
    """Fetches new data if needed"""
    try:
        if should_update():
            data = st.session_state.api.get_mentions()
            st.session_state.current_data = data
            st.session_state.last_update = datetime.now()
            st.session_state.update_counter += 1
            # Force a rerun only when new data is fetched
            time.sleep(1)  # Small delay to ensure smooth transition
            st.rerun()
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")

def create_visualizations(df: pd.DataFrame):
    """Creates and displays all dashboard visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            df.head(10),
            x='ticker',
            y='mentions',
            title='Top 10 Most Mentioned Stocks'
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',
            title='Mentions vs Upvotes'
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = px.bar(
        df.head(10),
        x='ticker',
        y='mention_change',
        title='24h Change in Mentions'
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

def display_timer():
    """Shows countdown timer until next update"""
    if st.session_state.last_update:
        elapsed = datetime.now() - st.session_state.last_update
        time_left = max(300 - elapsed.total_seconds(), 0)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        
        # Create a more visually appealing timer display
        st.markdown(
            f"""
            <div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;'>
                <h3 style='margin: 0; color: #0e1117; text-align: center;'>
                    Next update in: {minutes:02d}:{seconds:02d}
                </h3>
                <p style='margin: 5px 0 0 0; text-align: center; font-size: 0.8em; color: #666;'>
                    Updates completed: {st.session_state.update_counter}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    """Main application function"""
    st.set_page_config(layout="wide")
    initialize_session_state()
    
    st.title('Stock Mentions Dashboard')
    
    # Update data check
    update_data()
    
    # Display timer
    display_timer()
    
    # Display visualizations if data is available
    if st.session_state.current_data:
        df = pd.DataFrame(st.session_state.current_data['results'])
        create_visualizations(df)
    else:
        st.info("Initializing dashboard... Please wait.")

if __name__ == "__main__":
    main()
