from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.graph_objects as go
import colorlover as cl

load_figure_template("spacelab")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}
                      ])
# ----------------------------------------------DATA PREPARATION---------------------------------------------------

# source: https://www.kaggle.com/datasets/census/international-data?select=age_specific_fertility_rates.csv

# open dataset
df = pd.read_csv('/Filepath/age_specific_fertility_rates.csv', sep=',', header=0,
                 usecols=lambda x: x != '')

# unpivot DataFrame from wide format to long format
df = pd.melt(df, id_vars=['country_code', 'country_name', 'year'], value_vars=['fertility_rate_15_19',
                                                                               'fertility_rate_20_24',
                                                                               'fertility_rate_25_29',
                                                                               'fertility_rate_30_34',
                                                                               'fertility_rate_35_39',
                                                                               'fertility_rate_40_44',
                                                                               'fertility_rate_45_49'],
             var_name='age', value_name='rate')

# delete unnecessary data
df = df.drop(df[df.year > 2023].index)
df = df.drop(df[df.year < 1970].index)
df = df.drop(df[df.age == 'fertility_rate_45_49'].index)
df = df.replace('fertility_rate_15_19', '15-19')
df = df.replace('fertility_rate_20_24', '20-24')
df = df.replace('fertility_rate_25_29', '25-29')
df = df.replace('fertility_rate_30_34', '30-34')
df = df.replace('fertility_rate_35_39', '35-39')
df = df.replace('fertility_rate_40_44', '40-44')

df["rate"] = df["rate"].astype(float)

# ----------------------------------------------LAYOUT DEFINITION---------------------------------------------------

server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    # Header Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Br(),
                    html.H1('Fertility Rate Analysis'),
                    html.P("The Fertility Rate represents the number of births in a population per 1,000 women "
                           "of reproductive age in a given year. Over the past 50 years, fertility rates have "
                           "experienced a steady global decline. This trend can be attributed to several factors,"
                           " including the postponement of family formation and childbearing, as well as a decrease "
                           "in the desired size of families. This dashboard visualizes the change in fertility rates "
                           "for different age groups since 1970."),
                    html.P("Source: The U.S. Census Bureau")
                ], style={"background-color": "#EAEAEA"}),
            ], style={"border": "none"})
        ])], className='p-1 hidden'),
    dbc.Row([
        dbc.Col([
            # Section with Year Slider and Age Buttons
            dbc.Card([
                dbc.CardBody([
                    html.Br(),
                    html.Div("Drag the slider to change the year:", className='instructions'),
                    dcc.Slider(
                        min=df['year'].min(),
                        max=df['year'].max(),
                        step=None,
                        marks={year: str(year) for year in range(1955, 2051, 5)},
                        value=df['year'].max(),
                        id='year_slider',
                        tooltip={"placement": "bottom", "always_visible": True, },
                        className="year_selection--slider",
                    ),
                    html.Br(),
                    html.Div("Select an age group:", className='instructions'),
                    html.Div(
                        [
                            dbc.RadioItems(
                                id="age_buttons",
                                className="btn-group",
                                inputClassName="btn-check",
                                labelClassName="btn btn-outline-primary",
                                labelCheckedClassName="active",
                                options=sorted(
                                    [{"label": "age " + str(i), "value": str(i)} for i in df["age"].unique()],
                                    key=lambda x: x['label']),
                                value='15-19',
                            ),
                            html.Div(id="output"),
                        ], className="radio-group", )
                ])
            ], ),
            # Section with World Map
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Br(),
                            html.H2("The Fertility Rate across the World"),
                            html.H3("The highest fertility rate across all years is achieved by women between 25-29"
                                    " years."),
                            html.Hr(),
                            html.P("This heatmap illustrates the fertility rate for each country in the world. "
                                   "Dark blue countries have relatively low fertility rates, while red shaded countries"
                                   " have the highest fertility rates among women of the selected age. Please note that"
                                   " for white shaded countries no data is available for the selected year."),
                            html.Br(),
                            html.P("Click on a country to find out more about its fertility rates below.",
                                   style={'font-style': 'italic'}),
                            dbc.Col(dcc.Graph(id='world_map', figure={})),
                            html.Br(),
                            (html.P(id='info_country', children=[], )),
                        ])
                    ])
                ])
            ], className='mt-4'),
            # Section with text boxes
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Col(
                                [dbc.Col(html.P(id='container_1_value', children=[], className='container',
                                                style={'font-size': '40px', 'font-weight': 'bold'})),
                                 dbc.Col(html.P(id='container_1_text', children=[], className='container')),
                                 ]),
                        ], )
                    ])
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Col(
                                [dbc.Col(html.P(id='container_2_value', children=[], className='container',
                                                style={'font-size': '40px', 'font-weight': 'bold'})),
                                 dbc.Col(html.P(id='container_2_text', children=[], className='container')),
                                 ]),
                        ])
                    ], )
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Col(
                                [
                                    dbc.Col(html.P(id='container_3_value', children=[], className='container',
                                                   style={'font-size': '40px', 'font-weight': 'bold'})),
                                    dbc.Col(
                                        html.P(id='container_3_text', children=[], className='container')),
                                ]),
                        ])
                    ], )
                ]),

            ], className='mt-4'),
        ], xs=8),
        # Section with TOP 10 and LOW 10 charts
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("The 10 countries with the highest fertility rates"),
                    html.H3("Countries with comparatively high fertility rates are mostly located in Africa."),
                    dbc.Col(dcc.Graph(id='top10_barchart', figure={}), className='barchart'),
                    html.Br(),
                    html.Hr(),
                    html.Br(),
                    html.H2("The 10 countries with the lowest fertility rates"),
                    html.H3("Countries with comparatively low fertility rates are mostly located in Europe and "
                            "South East Asia."),
                    dbc.Col(dcc.Graph(id='low10_barchart', figure={}, className='barchart')),
                ], )
            ])
        ], xs=4),
    ], align='start', className='p-3 hidden'),
    # Section with second Header
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    (html.H1(id='headline_2', children=[], )),
                    html.P("The following charts provide a deep dive into fertility rates for the selected country."),
                ], style={"background-color": "#EAEAEA"}),
            ], style={"border": "none"})
        ])], className='p-1 hidden'),
    # Section with Development of Fertility Rates for each Country
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Col(html.H2(id='headline_rates_development', children=[])),
                    html.H3("In European countries such as France and Germany, a clear upward age shift can be observed"
                            " among expectant mothers."),
                    html.Hr(),
                    html.P("The charts below show the evolution of the fertility rate for each age group, as well as "
                           "the percentage evolution of the rate from the first year of record to 2023."),
                    html.Br(),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_19', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_19', figure={}), lg=2)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_24', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_24', figure={}), lg=2)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_29', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_29', figure={}), lg=2)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_34', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_34', figure={}), lg=2)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_39', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_39', figure={}), lg=2)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='bar_chart_44', figure={}), lg=10),
                        dbc.Col(dcc.Graph(id='indicator_44', figure={}), lg=2)
                    ]),
                    html.Br()
                ]),
            ]),
        ], xs=6),
        # Section with Country Comparison
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("Country Comparison"),
                    html.H3("Countries' fertility rates converge over time across all age groups."),
                    html.Hr(),
                    html.P("In this chart, individual countries can be compared with each other in terms of the "
                           "development of their fertility rates over the years."),
                    dbc.Row([
                        dbc.Col([
                            html.Div("Select the countries:", className='instructions'),
                            dcc.Dropdown(id='dropdown_countries',
                                         options=sorted(
                                             [{"label": str(i), "value": str(i)} for i in
                                              df["country_name"].unique()], key=lambda x: x['label']),
                                         multi=True,
                                         style={'height': '70px', 'width': '120%'},
                                         className="dropdown"
                                         )]),
                        dbc.Col([
                            html.Div("Select an age group:", className='instructions'),
                            dcc.Dropdown(id='dropdown_age_1',
                                         options=sorted(
                                             [{"label": str(i), "value": str(i)} for i in
                                              df["age"].unique()], key=lambda x: x['label']),
                                         multi=False,
                                         value='15-19',
                                         className="dropdown",
                                         )]),
                    ]),
                    dbc.Col(dcc.Graph(id='line_chart_country_comparison', figure={})),
                ])
            ], className="mb-4", ),
            # Section with Deviation from mean fertility rate
            dbc.Card([
                dbc.CardBody([
                    dbc.Col(html.H2(id='headline_deviation', children=[])),
                    html.H3("Most countries are either exclusively above average or below average fertility rates."),
                    html.Hr(),
                    html.P("This figure shows for each country the deviation from the average fertility rate for all "
                           "countries."),
                    dbc.Row([
                        dbc.Col([
                            html.Div("Select an age group:", className='instructions'),
                            dcc.Dropdown(id='dropdown_age_2',
                                         options=sorted(
                                             [{"label": str(i), "value": str(i)} for i in
                                              df["age"].unique()], key=lambda x: x['label']),
                                         multi=False,
                                         value='15-19',
                                         className="dropdown",
                                         style={'width': '60%'},
                                         )]),
                    ]),
                    dbc.Col(dcc.Graph(id='bar_chart_deviation', figure={}, className='barchart'))
                ]),
            ])
        ], xs=6)
    ], className='p-3 hidden'),
])


# ------------------------------CONNECTION OF PLOTLY GRAPHS WITH DASH COMPONENTS----------------------------------------

# Section with Slider, Age Buttons, World Map and container
@app.callback(
    Output('container_1_text', 'children'),
    Output('container_1_value', 'children'),
    Output('container_2_text', 'children'),
    Output('container_2_value', 'children'),
    Output('container_3_text', 'children'),
    Output('container_3_value', 'children'),
    Output('world_map', 'figure'),
    Output('top10_barchart', 'figure'),
    Output('low10_barchart', 'figure'),
    Input('year_slider', 'value'),
    Input("age_buttons", "value")
)
def update_graph(year_selected, age_selected):
    # Data Preparation
    dff = df.copy()
    dfg = dff[dff["age"] == age_selected]
    avg_rate_all_years = dfg["rate"].mean().astype(int)
    dff = dff[dff["year"] == year_selected]
    avg_rate_all_ages = dff["rate"].mean().astype(int)
    dff = dff[dff["age"] == age_selected]
    avg_rate = dff["rate"].mean().astype(int)
    dff["benchmark"] = dff["rate"].mean()

    # Container
    container_1_text = html.Div(
        ["out of 1000 women", html.Br(), html.B(" aged "), html.B(str(age_selected)), html.Br(), " gave birth in ",
         html.Br(), html.B(str(year_selected))]
    )

    container_1_value = str(avg_rate)

    container_2_text = html.Div(
        ["out of 1000 women", html.Br(), html.B(" aged 15-44 "), html.Br(), " gave birth in ", html.Br(),
         html.B(str(year_selected))])

    container_2_value = str(avg_rate_all_ages)

    container_3_text = html.Div(
        ["out of 1000 women", html.Br(), html.B(" aged "), html.B(str(age_selected)), html.Br(), " gave birth ",
         html.Br(), html.B("over all years")])

    container_3_value = str(avg_rate_all_years)

    # World Map
    map = px.choropleth(
        data_frame=dff,
        locations='country_name',
        locationmode='country names',
        scope="world",
        color='rate',
        hover_name='country_name',
        hover_data={'country_name': False},
        labels={'rate': 'Fertility Rate'},
    )

    map.update_layout({"plot_bgcolor": "rgba(0, 0,0, 0.5)", "paper_bgcolor": "rgba(0, 0,0,0)"},
                      transition_duration=500,
                      margin=dict(l=2, r=2, b=2, t=2),
                      )

    # Remove Antarctica from default zoom
    map.update_geos(lataxis_range=[-59, 90])

    # map.layout.autosize

    # Top 10 and Low 10 charts
    def ten_countries(dataframe):
        fig = px.bar(data_frame=dataframe, x="rate", y="country_name", orientation='h', text_auto=True,
                     hover_name='country_name',
                     hover_data={'country_name': False},
                     labels={'rate': 'Fertility Rate'},
                     )

        fig.update_layout(xaxis_title="fertility rate", yaxis_title=None,
                          template="simple_white", yaxis=dict(autorange="reversed"), xaxis_range=[0, 350],
                          margin=dict(l=20, r=20, t=10, b=20))

        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False,
                          marker_color='#D46351')

        fig.add_traces(
            go.Scatter(x=dataframe.benchmark, y=dataframe.country_name, mode='lines', name='mean',
                       line=dict(color="black")))

        # fig.layout.autosize
        return fig

    fig1 = ten_countries(dff.nlargest(10, "rate"))
    fig2 = ten_countries(dff.nsmallest(10, "rate")).update_traces(marker_color='#596A8E')

    return container_1_text, container_1_value, container_2_text, container_2_value, container_3_text, \
        container_3_value, map, fig1, fig2


# Dynamic Headline 2
@app.callback(
    Output('info_country', 'children'),
    Output('headline_2', 'children'),
    Input('world_map', 'clickData')
)
def update_graph(clickData):
    # Get selected country from world map click data
    if clickData:
        country_selected = clickData['points'][0]['location']
    else:
        country_selected = 'Germany'

    container_info = "You have selected: " + str(country_selected)
    container_headline = "Deep Dive: " + str(country_selected)

    return container_info, container_headline


# Bar charts for each age group
@app.callback(
    Output('headline_rates_development', 'children'),
    [Output(f'bar_chart_{age}', 'figure') for age in ['19', '24', '29', '34', '39', '44']],
    [Output(f'indicator_{age}', 'figure') for age in ['19', '24', '29', '34', '39', '44']],
    Input('world_map', 'clickData')
)
def update_graph(clickdata):
    # Get selected country from world map click data
    if clickdata:
        country_selected = clickdata['points'][0]['location']
    else:
        country_selected = 'Germany'

    # Data Preparation
    dff = df[df["country_name"] == country_selected]
    max_rate = dff["rate"].max()
    figures = []

    # Headline
    container = "Development of Fertility Rates: " + str(country_selected)

    # Loop to go through all age groups
    for age in ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44']:
        dff_age = dff[dff["age"] == age]
        dff_min_year = dff_age[dff_age["year"] == dff_age["year"].min()]
        dff_max_year = dff_age[dff_age["year"] == dff_age["year"].max()]

        # Bar chart
        figure = px.bar(dff_age, x='year', y='rate', hover_data=['rate', 'year'], color='rate')
        figure.update_layout(height=150, xaxis_title="Year", yaxis_title=None, coloraxis_showscale=False,
                             template="simple_white", yaxis_range=[0, max_rate],
                             title={'text': f"Fertility rate among women aged <b>{age}</b> years",
                                    'font': {'size': 14}},
                             margin=dict(l=80, r=0, b=0, t=30),
                             )
        figures.append(figure)

        # Indicator
        indicator = go.Figure(go.Indicator(
            mode='number+delta',
            value=int(dff_max_year['rate'].values),
            title={"text": "current fertility rate:", "font_color": 'black', 'font_size': 14},
            delta={"reference": int(dff_min_year['rate'].values), 'relative': True, 'valueformat': '.1%'},
            number={'font_color': 'black', 'font_size': 30}
        ))

        indicator.update_layout(height=150)

        figures.append(indicator)

    return container, figures[0], figures[2], figures[4], figures[6], figures[8], figures[10], figures[1], figures[3], \
        figures[5], figures[7], figures[9], figures[11]


# Multi Dropdown Menu for countries
@app.callback(Output('dropdown_countries', 'value'),
              Input('world_map', 'clickData')
              )
def update_dropdown(click_data):
    if click_data is not None:
        selected_country = click_data['points'][0]['location']
        return [selected_country]
    else:
        return 'Germany'


# Country Comparison
@app.callback(
    Output('line_chart_country_comparison', 'figure'),
    Input('dropdown_age_1', 'value'),
    Input('dropdown_countries', 'value')
)
def update_graph(age_selected, country_selected):
    # Data Preparation
    dff = df.copy()
    dff = dff[dff["age"] == age_selected]
    dff = dff.query('country_name==@country_selected').sort_values(by=["year", "country_name"])

    figure = px.line(dff, x='year', y='rate', color='country_name', template="simple_white")

    figure.update_traces(mode="markers+lines", hovertemplate=None)

    figure.update_layout(height=400, xaxis_title="Year", yaxis_title="Fertility Rate",
                         legend_title="Countries", hovermode="x unified")

    return figure


# Deviation from mean fertility rate
@app.callback(
    Output("headline_deviation", "children"),
    Output("bar_chart_deviation", 'figure'),

    Input('dropdown_age_2', 'value'),
    Input('world_map', 'clickData')
)
def update_graph(age_selected, clickdata):
    # Data Preparation
    dff = df.copy()
    dff = dff[dff["age"] == age_selected]
    dff['mean'] = dff.groupby('year')['rate'].transform('mean')
    dff['deviation'] = (dff['rate'] - dff['mean']).astype(int)

    # Get selected country from world map click data
    if clickdata:
        country_selected = clickdata['points'][0]['location']
    else:
        country_selected = 'Germany'
    dff = dff[dff["country_name"] == country_selected]

    # Headline
    container = "Deviation from mean fertility rate: " + str(country_selected)

    # Bar chart
    # Define the colors for the diverging scale
    color_a = '#4F6C96'
    color_b = '#EB6144'

    # Generate the color scale using colorlover
    n_colors = 11  # Number of colors in the scale
    scale = cl.scales[str(n_colors)]['div']['RdBu']

    # Adjust the scale to start and end with the specified colors
    start_color_index = (n_colors // 2) - 1
    end_color_index = n_colors // 2

    scale[start_color_index] = color_a
    scale[end_color_index] = color_b

    figure = px.bar(dff, x='year', y='deviation', color='deviation', color_discrete_sequence=scale,
                    range_color=(-100, 100))
    figure.update_layout(height=300, xaxis_title="Year", yaxis_title='deviation from average',
                         coloraxis_showscale=False, template="simple_white", yaxis_range=[-300, 300],
                         margin=dict(l=80, r=0, b=0, t=30),
                         )

    figure.add_hline(y=0, line_width=3, line_dash="dash", line_color="black")

    return container, figure


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
