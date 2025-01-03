import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict
import pandas as pd
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

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

class AsyncDataFetcher:
    def __init__(self, interval: int = 300):
        self.interval = interval
        self.last_data = None
        self.last_update = None
        self.is_running = False
        self.api = ApeWisdomAPI(rate_limit=1.0)
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    async def start_fetching(self):
        """Start the async data fetching loop"""
        self.is_running = True
        while self.is_running:
            # Use ThreadPoolExecutor for the blocking API call
            loop = asyncio.get_event_loop()
            self.last_data = await loop.run_in_executor(
                self.executor, 
                self.api.get_mentions
            )
            self.last_update = datetime.now()
            await asyncio.sleep(self.interval)
    
    def stop_fetching(self):
        """Stop the async data fetching loop"""
        self.is_running = False
        
    def get_time_until_next_update(self) -> timedelta:
        """Calculate time until next update"""
        if not self.last_update:
            return timedelta(seconds=0)
        next_update = self.last_update + timedelta(seconds=self.interval)
        return next_update - datetime.now()

def init_async_fetcher():
    """Initialize the async data fetcher in session state"""
    if 'fetcher' not in st.session_state:
        st.session_state.fetcher = AsyncDataFetcher()
        
    if 'fetch_thread' not in st.session_state:
        async def run_fetcher():
            await st.session_state.fetcher.start_fetching()
            
        loop = asyncio.new_event_loop()
        thread = threading.Thread(
            target=lambda: loop.run_until_complete(run_fetcher()),
            daemon=True
        )
        thread.start()
        st.session_state.fetch_thread = thread

def main():
    st.set_page_config(layout="wide")
    st.title('Stock Mentions Dashboard')
    
    # Initialize async fetcher
    init_async_fetcher()
    
    # Display countdown
    fetcher = st.session_state.fetcher
    time_until_update = fetcher.get_time_until_next_update()
    
    if time_until_update.total_seconds() > 0:
        minutes = int(time_until_update.total_seconds() // 60)
        seconds = int(time_until_update.total_seconds() % 60)
        st.markdown(f"### Next update in: {minutes:02d}:{seconds:02d}")
    else:
        st.markdown("### Updating...")
    
    # Display data
    if fetcher.last_data:
        df = pd.DataFrame(fetcher.last_data['results'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                px.bar(
                    df.head(10),
                    x='ticker',
                    y='mentions',
                    title='Top 10 Most Mentioned Stocks'
                ),
                use_container_width=True
            )
            
        with col2:
            st.plotly_chart(
                px.scatter(
                    df.head(20),
                    x='mentions',
                    y='upvotes',
                    text='ticker',
                    title='Mentions vs Upvotes'
                ),
                use_container_width=True
            )
        
        df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
        st.plotly_chart(
            px.bar(
                df.head(10),
                x='ticker',
                y='mention_change',
                title='24h Change in Mentions'
            ),
            use_container_width=True
        )

if __name__ == "__main__":
    main()
