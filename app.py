import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    html.Div([
        html.H1(children='BonApp Metrics'),

        html.H2(children='Leutner'),

        dcc.Graph(
            id='food-ratings-graph',
            figure={
                'data': [
                    {'x': ['Blackened Tofu', 'Made to Order Stir Fry', 'Margherita Pizza', 'Tomato Vegetable Soup', 'White Bean Stew', 'Made to Order Pasta Station'], 'y': [2.5, 4.5, 3, 2.8, 3.8, 5], 'type': 'bar', 'name': 'Average Rating'},
                    {'x': ['Blackened Tofu', 'Made to Order Stir Fry', 'Margherita Pizza', 'Tomato Vegetable Soup', 'White Bean Stew', 'Made to Order Pasta Station'], 'y': [3, 4.5, 5, 1, 4.2, 2.8, 1.3], 'type': 'bar', 'name': 'Rating Today'},
                ],
                'layout': {
                    'title': 'Food Ratings',
                    'xaxis' : dict(
                        title='Foods',
                        titlefont=dict(
                        family='Helvetica, monospace',
                        size=15,
                        color='#7f7f7f'
                    )),
                    'yaxis' : dict(
                        title='Ratings',
                        titlefont=dict(
                        family='Helvetica, monospace',
                        size=15,
                        color='#7f7f7f'
                    ))
                }
            }
        ),

        dcc.Graph(
            id='amenities-graph',
            figure={
                'data': [
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [3, 2.8, 2.5, 3], 'type': 'line', 'name': 'Milk'},
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [3, 2.8, 2.5, 2], 'type': 'line', 'name': 'Plates'},
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [2, 2.8, 1.5, 0.3], 'type': 'line', 'name': 'Cups'},
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [3, 2, 1.5, 0.5], 'type': 'line', 'name': 'Forks'},
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [3, 2.5, 2.2, 3], 'type': 'line', 'name': 'Knives'},
                    {'x': ["12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"], 'y': [2, 2.5, 2.5, 2.3], 'type': 'line', 'name': 'Spoons'},
                ],
                'layout': {
                    'title': 'Amenity Availability',
                    'xaxis' : dict(
                        title='Time',
                        titlefont=dict(
                        family='Helvetica, monospace',
                        size=15,
                        color='#7f7f7f'
                    )),
                    'yaxis' : dict(
                        title='Availability',
                        titlefont=dict(
                        family='Helvetica, monospace',
                        size=15,
                        color='#7f7f7f'
                    ))
                }
            }
        )

    ])
)

if __name__ == '__main__':
    app.run_server(debug=True)
