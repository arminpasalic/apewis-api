import streamlit as st
import plotly.express as px
import requests
from typing import Dict
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Define different color palettes for each visualization
MENTIONS_PALETTE = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9AB87A', '#F3B562', '#F06060', '#8789C0']
SCATTER_PALETTE = ['#FF9F1C', '#2EC4B6', '#E71D36', '#011627', '#FDFFFC', '#235789', '#C1292E', '#F1D302', '#020100', '#B8D4E3']
CHANGE_PALETTE = ['#4CB944', '#F4AC45', '#9B4DCA', '#22AED1', '#F98866', '#2AB7CA', '#FE4A49', '#00A878', '#FF6B6B', '#4ECDC4']
UPVOTES_PALETTE = ['#6C5B7B', '#C06C84', '#F67280', '#F8B195', '#355C7D', '#725A7A', '#A7226E', '#EC2049', '#F26B38', '#2F9599']

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, text: str = None, color_palette=None):
    """Create a styled bar chart with custom colors"""
    fig = px.bar(
        df,
        x=x,
        y=y,
        text=text,
        title=title,
        color_discrete_sequence=color_palette
    )
    
    # Update layout with professional styling and transparent background
    fig.update_layout(
        title={
            'font_size': 24,
            'font_family': "Arial, Helvetica, sans-serif",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family="Arial, Helvetica, sans-serif",
            size=12
        ),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(t=100, b=100, l=100, r=50)
    )
    
    # Update bar styling
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=12, family="Arial, Helvetica, sans-serif"),
        marker_line_width=1.5,
        opacity=0.85
    )
    
    # Update axes with transparent background
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.2)'
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.2)'
    )
    
    return fig

def create_scatter_plot(df: pd.DataFrame, x: str, y: str, text: str, title: str, color_palette=None):
    """Create a styled scatter plot with custom colors"""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        text=text,
        title=title,
        color_discrete_sequence=color_palette,
        hover_data={'name': True, 'ticker': True}
    )
    
    # Update layout with professional styling and transparent background
    fig.update_layout(
        title={
            'font_size': 24,
            'font_family': "Arial, Helvetica, sans-serif",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
            family="Arial, Helvetica, sans-serif",
            size=12
        ),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(t=100, b=100, l=100, r=50)
    )
    
    # Update marker styling
    fig.update_traces(
        marker=dict(
            size=12,
            line=dict(width=2),
            opacity=0.85
        ),
        textposition='top center',
        textfont=dict(size=12, family="Arial, Helvetica, sans-serif")
    )
    
    # Update axes with transparent background
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.2)'
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(128,128,128,0.2)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128,128,128,0.2)'
    )
    
    return fig

# Configure the Streamlit page with transparent background
st.set_page_config(layout="wide", page_title="Stock Mentions Dashboard")

# Custom CSS for better text styling and transparent background
st.markdown("""
    <style>
        .stApp {
            background: transparent;
        }
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
        div[data-testid="stVerticalBlock"] {
            background: transparent;
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
    
    # Top mentions bar chart with custom colors
    with col1:
        fig1 = create_bar_chart(
            df.head(10),
            x='name',
            y='mentions',
            text='ticker',
            title='Top 10 Most Mentioned Stocks',
            color_palette=MENTIONS_PALETTE
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Mentions vs Upvotes scatter plot with custom colors
    with col2:
        fig2 = create_scatter_plot(
            df.head(20),
            x='mentions',
            y='upvotes',
            text='ticker',
            title='Mentions vs Upvotes (Top 20 Stocks)',
            color_palette=SCATTER_PALETTE
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 24h Change in Mentions bar chart with custom colors
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    fig3 = create_bar_chart(
        df.head(10),
        x='name',
        y='mention_change',
        text='ticker',
        title='24h Change in Mentions (Top 10 Stocks)',
        color_palette=CHANGE_PALETTE
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Top Upvotes bar chart with custom colors
    fig4 = create_bar_chart(
        df.head(10).sort_values('upvotes', ascending=False),
        x='name',
        y='upvotes',
        text='ticker',
        title='Top 10 Most Upvoted Stocks',
        color_palette=UPVOTES_PALETTE
    )
    st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching stock mentions: {str(e)}")
