import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time
import asyncio
import aiohttp
from asyncio import create_task

class AsyncApeWisdomAPI:
    """Asynchronous version of the ApeWisdom API client"""
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = None
    
    async def _init_session(self):
        """Initialize aiohttp session if not already created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _rate_limit_wait(self):
        """Asynchronous rate limiting implementation"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    async def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        """Asynchronously fetch mentions data from the API"""
        await self._init_session()
        await self._rate_limit_wait()
        
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

class AsyncDataManager:
    """Manages asynchronous data updates and timing"""
    def __init__(self, update_interval: int = 300):
        self.update_interval = update_interval
        self.api = AsyncApeWisdomAPI(rate_limit=1.0)
        self.last_update = None
        self.current_data = None
        self.is_running = False
        self.update_task = None
    
    async def _update_data(self):
        """Internal method to fetch new data"""
        try:
            data = await self.api.get_mentions()
            self.current_data = data
            self.last_update = datetime.now()
            st.session_state.current_data = data
            st.session_state.last_update = self.last_update
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")
    
    async def start_update_loop(self):
        """Main update loop that runs continuously"""
        self.is_running = True
        while self.is_running:
            await self._update_data()
            # Wait for the next update interval
            await asyncio.sleep(self.update_interval)
    
    def stop(self):
        """Stop the update loop"""
        self.is_running = False
        if self.update_task:
            self.update_task.cancel()

def initialize_session_state():
    """Initialize all necessary session state variables"""
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = AsyncDataManager()
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'update_task' not in st.session_state:
        st.session_state.update_task = None

def create_visualizations(df: pd.DataFrame):
    """Create and display dashboard visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            df.head(10),
            x='ticker',
            y='mentions',
            title='Top 10 Most Mentioned Stocks'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',
            title='Mentions vs Upvotes'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = px.bar(
        df.head(10),
        x='ticker',
        y='mention_change',
        title='24h Change in Mentions'
    )
    st.plotly_chart(fig3, use_container_width=True)

def display_timer():
    """Display countdown timer until next update"""
    if st.session_state.last_update:
        elapsed = datetime.now() - st.session_state.last_update
        time_left = max(300 - elapsed.total_seconds(), 0)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        
        st.markdown(
            f"""
            <div style='padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 20px;'>
                <h3 style='margin: 0; color: #0e1117; text-align: center;'>
                    Next update in: {minutes:02d}:{seconds:02d}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

async def main():
    """Main application function with async support"""
    st.set_page_config(layout="wide")
    initialize_session_state()
    
    st.title('Stock Mentions Dashboard')
    
    # Start the update loop if not already running
    if st.session_state.update_task is None:
        st.session_state.update_task = create_task(
            st.session_state.data_manager.start_update_loop()
        )
    
    # Display timer
    display_timer()
    
    # Display visualizations if data is available
    if st.session_state.current_data:
        df = pd.DataFrame(st.session_state.current_data['results'])
        create_visualizations(df)
    else:
        st.info("Initializing dashboard... Please wait.")

if __name__ == "__main__":
    asyncio.run(main())
