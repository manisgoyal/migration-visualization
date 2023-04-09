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

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1('Migration Flow Map - SIN Project'),
    html.Div([
        html.H2('Select a Year'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year}
                     for year in df['Year'].unique()],
            value=df['Year'].min()
        ),
        html.H2('Select the Source'),
        dcc.Dropdown(
            id='source-dropdown',
            options=[{'label': source, 'value': source}
                     for source in ['All'] + df['Source'].unique().tolist()],
            value='All'
        ),
        html.H2('Select the Destination'),
        dcc.Dropdown(
            id='destination-dropdown',
            options=[{'label': destination, 'value': destination}
                     for destination in ['All'] + df['Target'].unique().tolist()],
            value='All'
        )
    ], style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(id='migration-flow-map')
])

# Define the callback function


@app.callback(
    Output('migration-flow-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('source-dropdown', 'value'),
     Input('destination-dropdown', 'value')]
)
def update_figure(year, source, destination):
    # Any one not Chosen
    if (year == None or source == None or destination == None):
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
        fig.update_layout(
            height=800,
            title_text='Select All the Values',
            geo_scope='world'
        )
        return fig

    if source == 'All' and destination == 'All':
        filtered_df = df[df['Year'] == year]
        fig = go.Figure()
        if filtered_df.empty:
            fig.update_layout(
                height=2000,
                title_text='Nothing Matches your Query',
                geo_scope='world'
            )
            fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
            return fig

        for source in filtered_df['Source'].unique():
            for destination in filtered_df['Target'].unique():
                sub_df = filtered_df[(filtered_df['Source'] == source) & (
                    filtered_df['Target'] == destination)]
                if not sub_df.empty:
                    fig.add_trace(go.Scattergeo(
                        locationmode='ISO-3',
                        lon=sub_df['lon_org'],
                        lat=sub_df['lat_org'],
                        mode='markers',
                        marker=dict(
                            sizemode='diameter',
                            sizemin=5,
                            color='red',
                            reversescale=True,
                            symbol='circle',
                        ),
                        hoverinfo='text',
                        text=sub_df['Source']
                    ))
                    fig.add_trace(go.Scattergeo(
                        locationmode='ISO-3',
                        lon=sub_df['lon_dest'],
                        lat=sub_df['lat_dest'],
                        mode='markers',
                        marker=dict(
                            sizemode='diameter',
                            sizemin=5,
                            color='blue',
                            reversescale=True,
                            symbol='square',
                        ),
                        hoverinfo='text',
                        text=sub_df['Target'].astype(str)
                    ))
                    fig.add_trace(
                        go.Scattergeo(
                            lon=sub_df['lon_org'].tolist(
                            ) + sub_df['lon_dest'].tolist(),
                            lat=sub_df['lat_org'].tolist(
                            ) + sub_df['lat_dest'].tolist(),
                            mode='lines',
                            line=dict(width=1, color='blue'),
                            hoverinfo='text',
                            text=[sub_df['Source'].get(sub_df['Source'].keys()[0]), sub_df['Target'].get(
                                sub_df['Target'].keys()[0])]
                        )
                    )

        fig.update_layout(
            height=800,
            geo=dict(
                scope='world',
                projection=go.layout.geo.Projection(type='natural earth'),
                showland=True,
                landcolor='rgb(217, 217, 217)',
                subunitwidth=1,
                countrywidth=1,
                subunitcolor='rgb(255,255,255)',
                countrycolor='rgb(255,255,255)'
            ),
            title_text='Migration Flows in {}'.format(year),
            geo_scope='world',
            showlegend=False
        )

        return fig

    if source == 'All':
        # if the user selects "All" as the source, display migration flows from all sources to the selected destination
        # Filter the DataFrame based on the selected year and destination
        filtered_df = df[(df['Year'] == year) & (df['Target'] == destination)]
        fig = go.Figure()
        if filtered_df.empty:
            fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
            fig.update_layout(
                height=800,
                title_text='Nothing Matches your Query',
                geo_scope='world'
            )
            return fig

        # Create a Plotly figure with a scattergeo trace for each unique source, and a trace for the migration flows between the origin and destination points
        for src in filtered_df['Source'].unique():
            sub_df = filtered_df[filtered_df['Source'] == src]
            if sub_df.empty:
                fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
                fig.update_layout(
                    height=800,
                    title_text='Nothing Matches your Query',
                    geo_scope='world'
                )
                return fig
            else:
                fig.add_trace(
                    go.Scattergeo(
                        lon=sub_df['lon_org'].tolist(
                        ) + sub_df['lon_dest'].tolist(),
                        lat=sub_df['lat_org'].tolist(
                        ) + sub_df['lat_dest'].tolist(),
                        mode='markers',
                        marker=dict(
                            sizemode='diameter',
                            sizemin=5,
                            color='red',
                            symbol='circle',
                        ),
                        name=src
                    )
                )

                fig.add_trace(go.Scattergeo(
                    locationmode='ISO-3',
                    lon=sub_df['lon_dest'],
                    lat=sub_df['lat_dest'],
                    mode='markers',
                    marker=dict(
                        sizemode='diameter',
                        sizemin=6,
                        color='blue',
                        reversescale=True,
                        symbol='square',
                    ),
                    hoverinfo='text',
                    text=sub_df['Target'].astype(str)
                ))
                sourceInfo = f"{sub_df['Source'].get(sub_df['Source'].keys()[0])} : {sub_df['Value'].get(sub_df['Value'].keys()[0])}"
                fig.add_trace(
                    go.Scattergeo(
                        lon=sub_df['lon_org'].tolist(
                        ) + sub_df['lon_dest'].tolist(),
                        lat=sub_df['lat_org'].tolist(
                        ) + sub_df['lat_dest'].tolist(),
                        mode='lines',
                        line=dict(width=1, color='blue'),
                        name=src,
                        hoverinfo='text',
                        text=[sourceInfo, sub_df['Target'].get(
                            sub_df['Target'].keys()[0])]
                    )
                )

        # Update the layout of the figure to
            fig.update_layout(
                title=f'Migration flows to {destination} ({year})',
                showlegend=False,
                geo=dict(
                    scope='world',
                    projection=go.layout.geo.Projection(type='natural earth'),
                    showland=True,
                    landcolor='rgb(217, 217, 217)',
                    subunitwidth=1,
                    countrywidth=1,
                    subunitcolor='rgb(255,255,255)',
                    countrycolor='rgb(255,255,255)'
                )
            )

        return fig

    if destination == 'All':  # if the user selects a specific source, display migration flows from that source to all destinations
        # Filter the DataFrame based on the selected year and source
        filtered_df = df[(df['Year'] == year) & (df['Source'] == source)]

        # Create a Plotly figure with a scattergeo trace for each unique destination, and a trace for the migration flows between the origin and destination points
        fig = go.Figure()
        if filtered_df.empty:
            fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
            fig.update_layout(
                height=800,
                title_text='Nothing Matches your Query',
                geo_scope='world'
            )
            return fig
        for dest in filtered_df['Target'].unique():
            sub_df = filtered_df[filtered_df['Target'] == dest]
            if sub_df.empty:
                fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
                fig.update_layout(
                    height=800,
                    title_text='Nothing Matches your Query',
                    geo_scope='world'
                )
                return fig
            else:
                fig.add_trace(
                    go.Scattergeo(
                        lon=sub_df['lon_org'].tolist(
                        ) + sub_df['lon_dest'].tolist(),
                        lat=sub_df['lat_org'].tolist(
                        ) + sub_df['lat_dest'].tolist(),
                        mode='markers',
                        marker=dict(
                            # size = sub_df['Value'],
                            sizemode='diameter',
                            sizemin=5,
                            color='red',
                            symbol='circle'
                        ),
                        name=dest
                    )
                )
                fig.add_trace(go.Scattergeo(
                    locationmode='ISO-3',
                    lon=sub_df['lon_dest'],
                    lat=sub_df['lat_dest'],
                    mode='markers',
                    marker=dict(
                        sizemode='diameter',
                        sizemin=6,
                        color='blue',
                        reversescale=True,
                        symbol='square',
                    ),
                    # hoverinfo='text',
                    text=sub_df['Target'].astype(str)
                ))
                destInfo = f"{sub_df['Target'].get(sub_df['Target'].keys()[0])} : {sub_df['Value'].get(sub_df['Value'].keys()[0])}"
                fig.add_trace(
                    go.Scattergeo(
                        lon=sub_df['lon_org'].tolist(
                        ) + sub_df['lon_dest'].tolist(),
                        lat=sub_df['lat_org'].tolist(
                        ) + sub_df['lat_dest'].tolist(),
                        mode='lines',
                        line=dict(width=1, color='blue'),
                        hoverinfo='text',
                        text=[sub_df['Source'].get(
                            sub_df['Source'].keys()[0]), destInfo]
                    )
                )

        # Update the layout of the figure
        fig.update_layout(
            title=f'Migration flows from {source} ({year})',
            showlegend=False,
            geo=dict(
                scope='world',
                projection=go.layout.geo.Projection(type='natural earth'),
                showland=True,
                landcolor='rgb(217, 217, 217)',
                subunitwidth=1,
                countrywidth=1,
                subunitcolor='rgb(255,255,255)',
                countrycolor='rgb(255,255,255)'
            )
        )
        return fig

    # else everything is selected
    else:
        fig = go.Figure()
        filtered_df = df[(df['Year'] == year) & (
            df['Target'] == destination) & (df['Source'] == source)]
        if filtered_df.empty:
            fig.add_trace(go.Scattergeo(locationmode='ISO-3'))
            fig.update_layout(
                height=2000,
                title_text='Nothing Matches your Query',
                geo_scope='world'
            )
        else:
            fig.add_trace(go.Scattergeo(
                locationmode='ISO-3',
                lon=filtered_df['lon_dest'],
                lat=filtered_df['lat_dest'],
                mode='markers',
                marker=dict(
                    sizemode='diameter',
                    sizemin=6,
                    color='blue',
                    reversescale=True,
                    symbol='square',
                ),
            ))
            destInfo = f"{filtered_df['Target'].get(filtered_df['Target'].keys()[0])} : {filtered_df['Value'].get(filtered_df['Value'].keys()[0])}"
            fig.add_trace(go.Scattergeo(
                locationmode='ISO-3',
                lon=filtered_df['lon_org'],
                lat=filtered_df['lat_org'],
                mode='markers',
                marker=dict(
                    sizemode='diameter',
                    sizemin=5,
                    color='red',
                    reversescale=True,
                    symbol='circle',
                ),
            ))
            fig.add_trace(
                go.Scattergeo(
                    lon=filtered_df['lon_org'].tolist(
                    ) + filtered_df['lon_dest'].tolist(),
                    lat=filtered_df['lat_org'].tolist(
                    ) + filtered_df['lat_dest'].tolist(),
                    mode='lines',
                    line=dict(width=1, color='blue'),
                    hoverinfo='text',
                    text=[filtered_df['Source'].get(
                        filtered_df['Source'].keys()[0]), destInfo]
                )
            )
            fig.update_layout(
                title=f'Migration flows from {source} to {destination} ({year})',
                showlegend=False,
                geo=dict(
                    scope='world',
                    projection=go.layout.geo.Projection(type='natural earth'),
                    showland=True,
                    landcolor='rgb(217, 217, 217)',
                    subunitwidth=1,
                    countrywidth=1,
                    subunitcolor='rgb(255,255,255)',
                    countrycolor='rgb(255,255,255)'
                )
            )
            return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
