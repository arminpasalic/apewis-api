import streamlit as st
import plotly.express as px
import requests
from typing import Dict
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Define a professional color palette
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Define consistent chart styling
CHART_STYLE = {
    'font_family': "Arial, Helvetica, sans-serif",
    'title_font_size': 24,
    'axis_title_font_size': 14,
    'tick_font_size': 12,
    'legend_font_size': 12
}

class ApeWisdomAPI:
    BASE_URL = "https://apewisdom.io/api/v1.0"
    
    def get_mentions(self, filter_type: str = "all-stocks", page: int = 1) -> Dict:
        url = f"{self.BASE_URL}/filter/{filter_type}/page/{page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, text: str = None):
    """Create a styled bar chart"""
    fig = px.bar(
        df,
        x=x,
        y=y,
        text=text,
        title=title,
        color_discrete_sequence=COLOR_PALETTE
    )
    
    # Update layout with professional styling
    fig.update_layout(
        title={
            'font_size': CHART_STYLE['title_font_size'],
            'font_family': CHART_STYLE['font_family'],
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family=CHART_STYLE['font_family'],
            size=CHART_STYLE['tick_font_size']
        ),
        xaxis_title_font=dict(size=CHART_STYLE['axis_title_font_size']),
        yaxis_title_font=dict(size=CHART_STYLE['axis_title_font_size']),
        plot_bgcolor='white',
        height=500,  # Fixed height for better proportions
        margin=dict(t=100, b=100, l=100, r=50)  # Adequate margins for labels
    )
    
    # Update bar styling
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=12, family=CHART_STYLE['font_family']),
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

def create_scatter_plot(df: pd.DataFrame, x: str, y: str, text: str, title: str):
    """Create a styled scatter plot"""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        text=text,
        title=title,
        color_discrete_sequence=COLOR_PALETTE,
        hover_data={'name': True, 'ticker': True}
    )
    
    # Update layout with professional styling
    fig.update_layout(
        title={
            'font_size': CHART_STYLE['title_font_size'],
            'font_family': CHART_STYLE['font_family'],
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family=CHART_STYLE['font_family'],
            size=CHART_STYLE['tick_font_size']
        ),
        xaxis_title_font=dict(size=CHART_STYLE['axis_title_font_size']),
        yaxis_title_font=dict(size=CHART_STYLE['axis_title_font_size']),
        plot_bgcolor='white',
        height=500,
        margin=dict(t=100, b=100, l=100, r=50)
    )
    
    # Update marker styling
    fig.update_traces(
        marker=dict(
            size=12,
            line=dict(width=2, color='DarkSlateGrey'),
            opacity=0.7
        ),
        textposition='top center',
        textfont=dict(size=12, family=CHART_STYLE['font_family'])
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

# Configure the Streamlit page
st.set_page_config(layout="wide", page_title="Stock Mentions Dashboard")

# Custom CSS for better text styling
st.markdown("""
    <style>
        .title {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        .subtitle {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 16px;
            color: #666;
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize API client
api = ApeWisdomAPI()

# Title with custom styling
st.markdown('<p class="title">Stock Mentions Dashboard</p>', unsafe_allow_html=True)

# Filter selection
filter_options = [
    "all", "all-stocks", "all-crypto", "4chan", "CryptoCurrency", 
    "CryptoCurrencies", "Bitcoin", "SatoshiStreetBets", "CryptoMoonShots",
    "CryptoMarkets", "stocks", "wallstreetbets", "options", 
    "WallStreetbetsELITE", "Wallstreetbetsnew", "SPACs", "investing", 
    "Daytrading"
]
selected_filter = st.sidebar.selectbox("Select a filter", filter_options, index=1)

try:
    # Fetch stock mentions data
    data = api.get_mentions(filter_type=selected_filter)
    df = pd.DataFrame(data['results'])
    
    # Display last updated time
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<p class="subtitle">Last Updated: {last_updated}</p>', unsafe_allow_html=True)
    
    # Create column layout
    col1, col2 = st.columns(2)
    
    # Top mentions bar chart
    with col1:
        fig1 = create_bar_chart(
            df.head(10),
            x='name',
            y='mentions',
            text='ticker',
            title='Top 10 Most Mentioned Stocks'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Mentions vs Upvotes scatter plot
    with col2:
        fig2 = create_scatter_plot(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',
            title='Mentions vs Upvotes (Top 20 Stocks)'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 24h Change in Mentions bar chart
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = create_bar_chart(
        df.head(10),
        x='name',
        y='mention_change',
        text='ticker',
        title='24h Change in Mentions (Top 10 Stocks)'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Top Upvotes bar chart
    fig4 = create_bar_chart(
        df.head(10).sort_values('upvotes', ascending=False),
        x='name',
        y='upvotes',
        text='ticker',
        title='Top 10 Most Upvoted Stocks'
    )
    st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching stock mentions: {str(e)}")
