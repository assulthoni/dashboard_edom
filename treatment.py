import os
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import flask
import glob
from navbar import Navbar


NAVBAR = Navbar()

BODY = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H3(
                        "Dashboard ini dibuat menggunakan Dash-plotly untuk kepentingan pengambilan keputusan di Program Studi Sistem Informasi Tel-U.",
                        style={'marginTop': 30}
                    ),
                    dbc.Button(
                        "Description",
                        id="collapse-button",
                        className="mb-3",
                        color="info",
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody([
                                html.P("Model untuk klasifikasi sentiment dibangun melalui kaidah NLP. "
                                       "Proses cleansing meliputi Stemming, Tokenisasi, Stopwords Removal, Punctuations Removal. "
                                       "Proses feature extraction meliputi Term Frequency-Inverse Document Frequency (TF-IDF) yang menghasilkan features berupa vector. "
                                       "Proses pemodelan meliputi Random Over Sampling dan Voting Classification dengan estimator Random Forest, Naive Bayes dan Support Vector Machine"),
                                html.H4("CLASSIFICATION REPORT PADA DATASET TEST :"),
                                html.Img(src='assets/classification report.png')
                            ]
                            )
                        ),
                        id="collapse",
                    ),

                ]
                )
            ),
        ),
    ])

def Treatment():
    layout = html.Div(children=[NAVBAR, BODY])
    return layout
