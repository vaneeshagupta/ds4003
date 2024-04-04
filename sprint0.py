# Import dependencies
from dash import Dash, html, dcc, Input, Output 
import pandas as pd
import plotly.express as px
import dash

#Cleaning and preparing data, making it tidy
import pandas as pd
df = pd.read_csv('bestsellers.csv')
#printing out the first couple rows to preview the data
df.head()
#checking for missing value
df.isnull().sum()

#Cleaning data set by making fiction and non-fiction variables
df['Fiction'] = df['Genre'].apply(lambda x: 1 if x == 'Fiction' else 0)
df['Non Fiction'] = df['Genre'].apply(lambda x: 1 if x == 'Non Fiction' else 0)
df.drop('Genre', axis=1, inplace=True)

#removing any duplicate entries for books (where there were bestsellers in multiple years), keeping only the initial year it was a bestseller
df.drop_duplicates(subset='Name', inplace=True)

df.to_csv('data.csv', index=False)
df2 = pd.read_csv('data.csv')
df = df2


# Load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1("Book Bestsellers from 2009-2019", style={'text-align': 'center'}),
    html.H2("Select the year(s) and genre(s) of the bestsellers and view the number of books in different price ranges as well as the correlation between user ratings and the number of ratings. Please note the year signifies the year that a book was first named a bestseller."),
    html.Label("Select Year Range:"),
    dcc.RangeSlider(
        id='year-slider',
        min=df2['Year'].min(),
        max=df2['Year'].max(),
        value=[df2['Year'].min(), df2['Year'].max()],
        marks={str(year): str(year) for year in range(df2['Year'].min(), df2['Year'].max() + 1)}
    ),
    html.Div([
        html.Div([
            html.Label("Filter by Book Type:"),
            dcc.RadioItems(
                id='book-type',
                options=[
                    {'label': 'Fiction', 'value': 1},
                    {'label': 'Non-Fiction', 'value': 0},
                    {'label': 'All', 'value': 'all'}
                ],
                value='all',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id='bar-chart', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='scatter-plot', style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ])
])

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('scatter-plot', 'figure')],
    [Input('year-slider', 'value'),
     Input('book-type', 'value')]
)
def update_charts(year_range, book_type):
    filtered_df = df2[(df2['Year'] >= year_range[0]) & (df2['Year'] <= year_range[1])]
    if book_type != 'all':
        filtered_df = filtered_df[filtered_df['Fiction'] == int(book_type)]

    price_ranges = ['0-10', '11-20', '21-30', '31-40', '41-50', '51+']
    book_counts = []

    for price_range in price_ranges:
        if price_range == '51+':
            count = filtered_df[(filtered_df['Price'] >= 51)].shape[0]
        else:
            price_range_values = price_range.split('-')
            count = filtered_df[(filtered_df['Price'] >= int(price_range_values[0])) &
                                (filtered_df['Price'] <= int(price_range_values[1]))].shape[0]
        book_counts.append(count)

    bar_fig = {
        'data': [{
            'x': price_ranges,
            'y': book_counts,
            'type': 'bar'
        }],
        'layout': {
            'xaxis': {'title': 'Price Range'},
            'yaxis': {'title': 'Number of Books'},
            'title': 'Number of Books in Different Price Ranges'
        }
    }

    scatter_fig = {
        'data': [{
            'x': filtered_df['Reviews'],
            'y': filtered_df['User Rating'],
            'text': filtered_df['Name'],
            'mode': 'markers',
            'marker': {
                'size': 10,
                'opacity': 0.8
            }
        }],
        'layout': {
            'xaxis': {'title': 'Number of Reviews'},
            'yaxis': {'title': 'User Rating'},
            'title': 'Book Ratings vs Number of Reviews'
        }
    }

    return bar_fig, scatter_fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)