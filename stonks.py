import streamlit as st
import plotly.express as px
import requests
from typing import Dict
import pandas as pd
from datetime import datetime

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

# Fetch stock mentions data
st.title('Stock Mentions Dashboard')

try:
    # Fetch stock mentions data
    data = api.get_mentions()
    
    # Create DataFrame from API results
    df = pd.DataFrame(data['results'])
    
    # Get current timestamp
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Display last updated time
    st.markdown(f"*Last Updated: {last_updated}*", unsafe_allow_html=True)
    
    # Create column layout for visualizations
    col1, col2 = st.columns(2)
    
    # Top mentions bar chart
    with col1:
        fig1 = px.bar(
            df.head(10),
            x='name',  # Changed from 'ticker' to 'name'
            y='mentions',
            text='ticker',  # Added ticker as text
            title='Top 10 Most Mentioned Stocks'
        )
        fig1.update_traces(textposition='outside')  # Show ticker on top of bars
        fig1.update_layout(
            xaxis_title="Stock Name",
            yaxis_title="Number of Mentions"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Mentions vs Upvotes scatter plot
    with col2:
        fig2 = px.scatter(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',  # Use only ticker for text
            hover_data={'name': True, 'ticker': True},  # Include full name in hover
            title='Mentions vs Upvotes (Top 20 Stocks)'
        )
        fig2.update_traces(textposition='top center')  # Position ticker text
        fig2.update_layout(
            xaxis_title="Number of Mentions",
            yaxis_title="Number of Upvotes"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 24h Change in Mentions bar chart
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = px.bar(
        df.head(10),
        x='name',  # Changed from 'ticker' to 'name'
        y='mention_change',
        text='ticker',  # Added ticker as text
        title='24h Change in Mentions (Top 10 Stocks)'
    )
    fig3.update_traces(textposition='outside')  # Show ticker on top of bars
    fig3.update_layout(
        xaxis_title="Stock Name",
        yaxis_title="Change in Mentions"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Top Upvotes bar chart
    fig4 = px.bar(
        df.head(10).sort_values('upvotes', ascending=False),
        x='name',  # Changed from 'ticker' to 'name'
        y='upvotes',
        text='ticker',  # Added ticker as text
        title='Top 10 Most Upvoted Stocks'
    )
    fig4.update_traces(textposition='outside')  # Show ticker on top of bars
    fig4.update_layout(
        xaxis_title="Stock Name",
        yaxis_title="Number of Upvotes"
    )
    st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching stock mentions: {str(e)}")
