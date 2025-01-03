import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from ape_wisdom import ApeWisdomAPI
import pandas as pd
import threading
import time
from datetime import datetime

class DataCollector:
    def __init__(self, interval=300):
        self.interval = interval
        self.latest_data = None
        self.api = ApeWisdomAPI()
        self.lock = threading.Lock()
        self.last_update = None
        self.next_update = None
        
    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        while True:
            try:
                self.next_update = datetime.now().timestamp() + self.interval
                data = self.api.get_mentions("all-stocks", page=1)
                
                # Clear old data explicitly
                old_data = None
                with self.lock:
                    self.latest_data = data
                    self.last_update = datetime.now()
                    # Force garbage collection if needed
                    import gc
                    gc.collect()
                    
                print(f"Data updated at {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(60)
    
    def get_latest_data(self):
        with self.lock:
            return self.latest_data, self.last_update, self.next_update

collector = DataCollector()
collector.start()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Stock Mentions Dashboard', style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        html.H4('Data Updates:', style={'marginBottom': '10px'}),
        html.Div([
            html.Span('Last update: ', style={'fontWeight': 'bold'}),
            html.Span(id='last-update')
        ]),
        html.Div([
            html.Span('Next update in: ', style={'fontWeight': 'bold'}),
            html.Span(id='countdown')
        ]),
    ], style={'textAlign': 'center', 'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
    
    html.Div([
        dcc.Graph(id='mentions-chart'),
        dcc.Graph(id='scatter-plot'),
        dcc.Graph(id='change-chart'),
        dcc.Interval(
            id='interval-component',
            interval=1000,
            n_intervals=0
        )
    ])
])

@app.callback(
    [Output('mentions-chart', 'figure'),
     Output('scatter-plot', 'figure'),
     Output('change-chart', 'figure'),
     Output('last-update', 'children'),
     Output('countdown', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    data, last_update, next_update = collector.get_latest_data()
    
    if data is None:
        return dash.no_update, dash.no_update, dash.no_update, "Never", "Initializing..."
    
    now = datetime.now().timestamp()
    seconds_left = int(next_update - now)
    countdown_text = f"{seconds_left // 60}m {seconds_left % 60}s"
    last_update_text = last_update.strftime("%Y-%m-%d %H:%M:%S")
    
    df = pd.DataFrame(data['results'])
    
    mentions_fig = px.bar(
        df.head(10),
        x='ticker',
        y='mentions',
        title='Top 10 Most Mentioned Stocks',
        labels={'ticker': 'Stock', 'mentions': 'Number of Mentions'},
        color='mentions'
    )
    
    scatter_fig = px.scatter(
        df.head(20),
        x='mentions',
        y='upvotes',
        title='Mentions vs Upvotes (Top 20 Stocks)',
        labels={'mentions': 'Number of Mentions', 'upvotes': 'Number of Upvotes'},
        text='ticker',
        size='mentions',
        color='upvotes'
    )
    
    df['mention_change'] = df['mentions'].astype(float) - df['mentions_24h_ago'].astype(float)
    change_fig = go.Figure()
    change_fig.add_trace(go.Bar(
        x=df.head(10)['ticker'],
        y=df.head(10)['mention_change'],
        name='24h Change in Mentions'
    ))
    change_fig.update_layout(
        title='24h Change in Mentions (Top 10 Stocks)',
        xaxis_title='Stock',
        yaxis_title='Change in Mentions'
    )
    
    return mentions_fig, scatter_fig, change_fig, last_update_text, countdown_text

# Add this at the bottom of your main app.py file
server = app.server  # needed for deployment

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
