import copy
import pandas as pd
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from app import select_all
from data import KODE_NAMA_LENGKAP_DOSEN

from navbar import Navbar

TABLENAME_KUANTITATIF = 'nlp_api_pertanyaannumerik'
KODE_DOSEN = {k: v for k, v in sorted(KODE_NAMA_LENGKAP_DOSEN.items(), key=lambda item: item[1])}
SCHOOLYEAR = list(select_all(TABLENAME_KUANTITATIF).SCHOOLYEAR.unique())
NAVBAR = Navbar()

GRAPH_OVERVIEW = dcc.Graph(
    id="graph-overview",
    figure=go.Figure(
        [
            go.Bar(x=["ABF", "DTP", "GRI"], y=[3, 2, 1])
        ],
        layout={
            'legend': dict(
                x=0,
                y=0.7,
                traceorder='normal',
            ),
            'margin': dict(
                l=5,
                r=5,
                b=15,
                t=15,
                pad=15,
            ),
        },
    ),
)
BODY = dbc.Container(
    [
        # untuk Modal Description dashboard
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='intermediate-value', style={'display': 'none'}),
        dbc.Row([

            dbc.Col(
                html.Div([
                    html.H2(
                        "Halaman Ini berisikan data kuantitatif",
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
                                                                                    id="dropdown-year-start",
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
                                                                                    id="dropdown-year-end",
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
                                                                    id='dropdown_semester',
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

                                    ],
                                    md=4
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H4("Histori Nilai EDOM", className="card-title"),
                                                    dcc.Loading(
                                                        dcc.Graph(
                                                            id="line-histori-edom",
                                                        )
                                                    )
                                                ],
                                            ),
                                        ),
                                    ],
                                    md=8
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
                                                            html.H4("Prosentase Kepuasan",
                                                                    className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id="gauge-kepuasan",
                                                                )
                                                            )

                                                        ],
                                                    ),
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Prosentase Matkul berdasarkan KM",
                                                                    className='card-title'),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id='prosentase-matkul-km',
                                                                )
                                                            )

                                                        ]
                                                    )
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Prosentase Dosen berdasarkan KM",
                                                                    className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id='prosentase-dosen-km',
                                                                )
                                                            ),

                                                        ]
                                                    )
                                                ),
                                            ]
                                        )
                                    ]
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
                                                            html.H4("Daftar Matkul dibawah KM",
                                                                    className="card-title"),
                                                            dt.DataTable(
                                                                id="table-kepuasan-matkul",
                                                                columns=[
                                                                    {'name': 'TA', 'id': "TA"},
                                                                    {'name': 'Semester', 'id': "Semester"},
                                                                    {'name': 'Matkul', 'id': "Matkul"},
                                                                    {'name': 'Nilai', 'id': "Nilai"}
                                                                ],
                                                                style_data_conditional=[
                                                                    {
                                                                        'if': {
                                                                            'column_id': 'Nilai',
                                                                            'filter_query': '{Nilai} < 85.0'
                                                                        },
                                                                        'backgroundColor': 'tomato',
                                                                        'color': 'white'
                                                                    }
                                                                ],
                                                                page_current=0,
                                                                page_size=5,
                                                                page_action='custom'
                                                            )
                                                        ]
                                                    )
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Daftar Dosen Dibawah KM",
                                                                    className="card-title"),
                                                            dt.DataTable(
                                                                id="table-dosen-dibawah-km",
                                                                columns=[
                                                                    {'name': 'TA', 'id': "TA"},
                                                                    {'name': 'Semester', 'id': "Semester"},
                                                                    {'name': 'Dosen', 'id': "Dosen"},
                                                                    {'name': 'Nilai', 'id': "Nilai"}
                                                                ],
                                                                style_data_conditional=[
                                                                    {
                                                                        'if': {
                                                                            'column_id': 'Nilai',
                                                                            'filter_query': '{Nilai} < 85.0'
                                                                        },
                                                                        'backgroundColor': 'tomato',
                                                                        'color': 'white'
                                                                    }
                                                                ],
                                                                page_current=0,
                                                                page_size=5,
                                                                page_action='custom'
                                                            )
                                                        ]
                                                    )
                                                ),
                                            ]
                                        )
                                    ]
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
                                                            html.H4("Nilai Aspek Terendah Matkul",
                                                                    className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id='bar-aspek-terendah',
                                                                )
                                                            )

                                                        ]
                                                    )
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.H4("Nilai Aspek Terendah Dosen",
                                                                    className="card-title"),
                                                            dcc.Loading(
                                                                dcc.Graph(
                                                                    id='bar-aspek-terendah-dosen',
                                                                )
                                                            )

                                                        ]
                                                    )
                                                ),
                                            ]
                                        ),
                                        # GRAPH_OVERVIEW
                                    ],
                                )
                            ],
                            style={'marginBottom': 30}
                        ),
                    ],
                    style={'marginTop': 30}
                ),
            ]
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
                                            html.H4("Histori Dosen", className="card-title"),
                                            dcc.Dropdown(
                                                options=[
                                                    {'label': nama, 'value': kode} for kode, nama in
                                                    KODE_DOSEN.items()
                                                ],
                                                id="dropdown-dosen",
                                                value=['ABF', 'DTP'],
                                                placeholder="Select Lecture",
                                                multi=True
                                            ),
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="histori-dosen",
                                                )
                                            )

                                        ],
                                    ),
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H4("Barchart Matkul per Dosen", className="card-title"),
                                            dcc.Loading(
                                                dcc.Graph(
                                                    id="bar-matkul-dosen",
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
    ],
    fluid=True,
)


# app.title = 'Dashboard EDOM'
def Kuantitatif():
    layout = html.Div(children=[NAVBAR, BODY])
    return layout
