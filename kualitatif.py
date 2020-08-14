import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_daq as daq
from app import select_all
from navbar import Navbar
from data import KODE_NAMA_LENGKAP_DOSEN

TABLENAME_KUALITATIF = 'nlp_api_pertanyaanterbuka'
SCHOOLYEAR = list(select_all(TABLENAME_KUALITATIF).SCHOOLYEAR.unique())
KODE_DOSEN = {k: v for k, v in sorted(KODE_NAMA_LENGKAP_DOSEN.items(), key=lambda item: item[1])}

NAVBAR = Navbar()

BODY = dbc.Container(
    [
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='intermediate-value-kw', style={'display': 'none'}),
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H2(
                        "Halaman Ini berisikan data Kualitatif",
                        style={'marginTop': 30, 'textAlign': 'center'}
                    ),
                ]
                ),
            ),
        ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.CardDeck(
                                            [
                                                dbc.Card([
                                                    dbc.CardHeader("Filter Adjustment"),
                                                    dbc.CardBody([
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        html.H6("Select Academic Year"),
                                                                        dbc.Row(
                                                                            [
                                                                                dbc.Col(
                                                                                    [
                                                                                        dcc.Dropdown(
                                                                                            options=[
                                                                                                {'label': i,
                                                                                                 'value': i} for i in
                                                                                                SCHOOLYEAR
                                                                                            ],
                                                                                            value='1819',
                                                                                            id="dropdown-year-start-kw",
                                                                                            placeholder="Select Year "
                                                                                                        "Start "
                                                                                        )
                                                                                    ],
                                                                                ),
                                                                                html.P("to"),
                                                                                dbc.Col(
                                                                                    [
                                                                                        dcc.Dropdown(
                                                                                            options=[
                                                                                                {'label': i,
                                                                                                 'value': i} for i in
                                                                                                SCHOOLYEAR
                                                                                            ],
                                                                                            value='1920',
                                                                                            id="dropdown-year-end-kw",
                                                                                            placeholder="Select Year "
                                                                                                        "End "
                                                                                        )
                                                                                    ]
                                                                                )
                                                                            ]
                                                                        ),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        html.H6("Select Semester"),
                                                                        dcc.Dropdown(
                                                                            options=[
                                                                                {'label': 'Ganjil', 'value': '1'},
                                                                                {'label': 'Genap', 'value': '2'}
                                                                            ],
                                                                            multi=True,
                                                                            value=[1, 2],
                                                                            id='dropdown_semester-kw',
                                                                            placeholder="Select Semester"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                    ),
                                                ],
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Rata Rata Sentiment", className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="avg-sentiment",
                                                                )
                                                            )

                                                        ],
                                                    ),
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Histori Sentiment Edom",
                                                                    className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="histori-sentiment-edom",
                                                                )
                                                            )

                                                        ],
                                                    ),
                                                ),
                                            ]
                                        ),
                                        # GRAPH_OVERVIEW
                                    ],
                                )
                            ],
                            style={'marginBottom': 30}
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.CardDeck(
                                            [

                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "Histori Sentiment Dosen",
                                                                className="card-title"),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': nama, 'value': kode} for kode, nama in
                                                                    KODE_DOSEN.items()
                                                                ],
                                                                value=['ABF', 'DTP'],
                                                                id="dropdown-dosen-kw",
                                                                placeholder="Select Lecture",
                                                                multi=True
                                                            ),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="histori-sentiment-dosen",
                                                                )
                                                            )

                                                        ],
                                                    ),
                                                ),
                                            ]
                                        ),
                                        # GRAPH_OVERVIEW
                                    ],
                                )
                            ],
                            style={'marginBottom': 30}
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H4("Dosen Dengan Sentiment Negatif",
                                                            className="card-title"),
                                                    dt.DataTable(
                                                        id="dosen-sentiment-negatif",
                                                        data=[
                                                            {'Dosen': 'Albi Fitriansyah', 'Persentase': '45'},
                                                            {'Dosen': 'Rahmadita Andreswari',
                                                             'Persentase': '76'}
                                                        ],
                                                        columns=[
                                                            {'name': 'Periode', 'id': 'Periode'},
                                                            {'name': 'Dosen', 'id': "Dosen"},
                                                            {'name': 'Persentase', 'id': "Persentase"}
                                                        ],
                                                        style_data_conditional=[
                                                            {
                                                                'if': {
                                                                    'column_id': 'Persentase',
                                                                    'filter_query': '{Persentase} < 85.0'
                                                                },
                                                                'backgroundColor': 'tomato',
                                                                'color': 'white'
                                                            }
                                                        ],
                                                        page_current=0,
                                                        page_size=10,
                                                        page_action='custom'
                                                    )
                                                ]
                                            )
                                        ),
                                    ],
                                    )
                            ],
                            style={'marginBottom': 30}
                        ),
                    ],
                    style={'marginTop': 30}
                )
            ]
        ),

    ],
    fluid=True,
)


# app.title = 'Dashboard EDOM'
def Kualitatif():
    layout = html.Div(children=[NAVBAR, BODY])
    return layout
