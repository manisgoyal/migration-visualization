import dash
from dash import dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# Load the migration data into a pandas DataFrame
df = pd.read_csv('updated_file1.csv')

# Create a list of unique years in the DataFrame
years = sorted(df['Year'].unique())

# Create a list of unique sources in the DataFrame
sources = sorted(df['Source'].unique())

# Create a list of unique destinations in the DataFrame
destinations = sorted(df['Target'].unique())

# Create a Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1('Migration Flow Map'),
    html.Div([
        html.Label('Year:'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in years],
            value=years[0]
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Source:'),
        dcc.Dropdown(
            id='source-dropdown',
            options=[{'label': source, 'value': source} for source in sources],
            value=sources[0]
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Destination:'),
        dcc.Dropdown(
            id='destination-dropdown',
            options=[{'label': dest, 'value': dest} for dest in destinations],
            value=destinations[0]
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    dcc.Graph(id='migration-flow-map')
])

# Define the callback function that updates the map when the user selects a new year, source, or destination


@app.callback(
    dash.dependencies.Output('migration-flow-map', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value'),
     dash.dependencies.Input('source-dropdown', 'value'),
     dash.dependencies.Input('destination-dropdown', 'value')])
def update_map(year, source, destination):
    # Filter the DataFrame based on the selected year, source, and destination
    filtered_df = df[(df['Year'] == year) & (
        df['Source'] == source) & (df['Target'] == destination)]

    # Create a Plotly figure with a scattergeo trace for the origin and destination points
    fig = go.Figure(
        go.Scattergeo(
            lon=filtered_df['lon_org'].tolist(
            ) + filtered_df['lon_dest'].tolist(),
            lat=filtered_df['lat_org'].tolist(
            ) + filtered_df['lat_dest'].tolist(),
            mode='markers',
            marker=dict(
                size=10,
                color='red',
                symbol='circle'
            )
        )
    )

    # Add a trace for the migration flows between the origin and destination points
    fig.add_trace(
        go.Scattergeo(
            lon=filtered_df['lon_org'].tolist(
            ) + filtered_df['lon_dest'].tolist(),
            lat=filtered_df['lat_org'].tolist(
            ) + filtered_df['lat_dest'].tolist(),
            mode='lines',
            line=dict(
                width=1,
                color='blue'
            ),
            opacity=0.8
        )
    )

    fig.update_layout(
        geo=dict(
            projection_type='orthographic',
            showland=True,
            landcolor='rgb(250, 250, 250)',
            showcountries=True,
            countrycolor='rgb(10, 10, 10)',
            showocean=True,
            oceancolor='rgb(0, 0, 255)',
            showlakes=True,
            lakecolor='rgb(0, 0, 255)'
        ),
        title=dict(
            text=f'Migration Flow Map ({source} to {destination}, {year})',
            font=dict(size=24),
            x=0.5
        ),
        margin=dict(l=0, r=0, t=60, b=0)
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
