import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output


# Load the migration data into a pandas DataFrame
df = pd.read_csv('updated_file1.csv')

# Create a list of unique years in the DataFrame
years = sorted(df['Year'].unique())

# Create a list of unique sources in the DataFrame
sources = sorted(df['Source'].unique())

# Create a list of unique destinations in the DataFrame
destinations = sorted(df['Target'].unique())

## Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1('Migration Flow Map'),
    html.Div([
        dcc.Dropdown(
            id = 'year-dropdown',
            options = [{'label': year, 'value': year} for year in df['Year'].unique()],
            value = df['Year'].min()
        ),
        dcc.Dropdown(
            id = 'source-dropdown',
            options = [{'label': source, 'value': source} for source in ['All'] + df['Source'].unique().tolist()],
            value = 'All'
        ),
        dcc.Dropdown(
            id = 'destination-dropdown',
            options = [{'label': destination, 'value': destination} for destination in df['Target'].unique()],
            value = df['Target'].unique()[0]
        )
    ], style = {'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(id = 'migration-flow-map')
])

# Define the callback function
@app.callback(
    Output('migration-flow-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('destination-dropdown', 'value')]
)
def update_figure(year, source, destination):
    if source == 'All': # if the user selects "All" as the source, display migration flows from all sources to the selected destination
        # Filter the DataFrame based on the selected year and destination
        filtered_df = df[(df['Year'] == year) & (df['Target'] == destination)]

        # Create a Plotly figure with a scattergeo trace for each unique source, and a trace for the migration flows between the origin and destination points
        fig = go.Figure()
        for src in filtered_df['Source'].unique():
            sub_df = filtered_df[filtered_df['Source'] == src]
            if not sub_df.empty:
                fig.add_trace(
                    go.Scattergeo(
                        lon = sub_df['lon_org'].tolist() + sub_df['lon_dest'].tolist(),
                        lat = sub_df['lat_org'].tolist() + sub_df['lat_dest'].tolist(),
                        mode = 'markers',
                        marker = dict(
                            # size = sub_df['Value'],
                            sizemode = 'diameter',
                            # sizemin = 5,
                            color = 'blue',
                            # symbol = 'circle'
                        ),
                        name = src
                    )
                )
                fig.add_trace(
                    go.Scattergeo(
                        lon = sub_df['lon_org'].tolist() + sub_df['lon_dest'].tolist(),
                        lat = sub_df['lat_org'].tolist() + sub_df['lat_dest'].tolist(),
                        mode = 'lines',
                        line = dict(width = 1,color = 'blue'),
                        name = src
                    )
                )

        # Update the layout of the figure to
            fig.update_layout(
                title = f'Migration flows to {destination} ({year})',
                geo = dict(
                    scope = 'world',
                    projection = go.layout.geo.Projection(type = 'natural earth'),
                    showland = True,
                    landcolor = 'rgb(217, 217, 217)',
                    subunitwidth = 1,
                    countrywidth = 1,
                    subunitcolor = 'rgb(255,255,255)',
                    countrycolor = 'rgb(255,255,255)'
                )
            )
    else: # if the user selects a specific source, display migration flows from that source to all destinations
        # Filter the DataFrame based on the selected year and source
        filtered_df = df[(df['Year'] == year) & (df['Source'] == source)]

        # Create a Plotly figure with a scattergeo trace for each unique destination, and a trace for the migration flows between the origin and destination points
        fig = go.Figure()
        for dest in filtered_df['Target'].unique():
            sub_df = filtered_df[filtered_df['Target'] == dest]
            if not sub_df.empty:
                fig.add_trace(
                    go.Scattergeo(
                        lon = sub_df['lon_org'].tolist() + sub_df['lon_dest'].tolist(),
                        lat = sub_df['lat_org'].tolist() + sub_df['lat_dest'].tolist(),
                        mode = 'markers',
                        marker = dict(
                            # size = sub_df['Value'],
                            sizemode = 'diameter',
                            sizemin = 5,
                            color = 'red',
                            symbol = 'circle'
                        ),
                        name = dest
                    )
                )
                fig.add_trace(
                    go.Scattergeo(
                        lon = sub_df['lon_org'].tolist() + sub_df['lon_dest'].tolist(),
                        lat = sub_df['lat_org'].tolist() + sub_df['lat_dest'].tolist(),
                        mode = 'lines',
                        line = dict(width = 1,color = 'blue'),
                        name = dest
                    )
                )

        # Update the layout of the figure
        fig.update_layout(
            title = f'Migration flows from {source} ({year})',
            geo = dict(
                scope = 'world',
                projection = go.layout.geo.Projection(type = 'natural earth'),
                showland = True,
                landcolor = 'rgb(217, 217, 217)',
                subunitwidth = 1,
                countrywidth = 1,
                subunitcolor = 'rgb(255,255,255)',
                countrycolor = 'rgb(255,255,255)'
            )
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug = True)
