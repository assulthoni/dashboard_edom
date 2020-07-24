import pandas as pd
from data import DOSEN, MATKUL
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
import plotly.graph_objects as go
from data import matkul_dosen
from navbar import Navbar

labeled_data = pd.read_csv('data/labeled_1920_data_si.csv')
labeled_data = labeled_data.drop(['QUESTION', 'ANSWERBY', 'QUESTIONNUMBER', 'STUDYPROGRAMNAME'], axis=1)
labeled_data.columns = ['Jawaban', 'Kode Matkul', 'Nama Matkul',
                        'Kelas', 'Dosen', 'Tahun Ajaran',
                        'Semester', 'Label']
eda_df_cnt = pd.read_csv('data/viz_dataset.csv')
eda_df_cnt_matkul = pd.read_csv('data/viz_dataset_matkul.csv')
eda_df = labeled_data.groupby(by=['Semester', 'Label']).count().reset_index()
viz_df = pd.read_csv('data/viz_dataset.csv')
viz_df_dosenmatkul = pd.read_csv('data/viz_dataset_dosenmatkul.csv')
DOSEN = DOSEN
MATKUL = MATKUL
NAVBAR = Navbar()


def plotly_boxplot():
    fig = go.Figure()
    df = viz_df_dosenmatkul.groupby(['Dosen', 'Semester']).sum().reset_index()
    df = pd.melt(df, id_vars='Semester')
    df = df.loc[df.variable.isin(['positif', 'netral', 'negatif'])]
    for i, term in enumerate(df['Semester'].unique()):
        semester = "Ganjil" if term == 1 else "Genap"
        df_plot = df[df['Semester'] == term]
        fig.add_trace(go.Box(
            x=df_plot.variable,
            y=df_plot.value,
            name="Semester " + semester
        ))
    fig.update_layout(boxmode='group', xaxis_tickangle=0,
                      title="Boxplot dosen tiap semester")
    return fig


def plotly_wordcloud(data_frame, stopwords=['dan', 'pak', 'buk', 'bu', 'pa', 'bapak', 'ibu', 'ibuk', 'mam', 'sir']):
    complaints_text = list(data_frame["Jawaban"].dropna().values)

    if len(complaints_text) < 1:
        return {}, {}, {}

    # join all documents in corpus
    text = " ".join(list(complaints_text))

    word_cloud = WordCloud(stopwords=set(stopwords), max_words=75, max_font_size=60)
    word_cloud.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[0])
        y_arr.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        textposition="top center",
        hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 300],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 300],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}
    word_list_top = word_list[:35]
    word_list_top.reverse()
    freq_list_top = freq_list[:35]
    freq_list_top.reverse()

    frequency_figure_data = {
        "data": [
            {
                "y": word_list_top,
                "x": freq_list_top,
                "type": "bar",
                "name": "",
                "orientation": "h",
            }
        ],
        "layout": {"height": "500", "margin": dict(t=20, b=20, l=100, r=20, pad=4)},
    }
    treemap_trace = go.Treemap(
        labels=word_list_top, parents=[""] * len(word_list_top), values=freq_list_top
    )
    treemap_layout = go.Layout({"margin": dict(t=10, b=10, l=5, r=5, pad=4)})
    treemap_figure = {"data": [treemap_trace], "layout": treemap_layout}
    return wordcloud_figure_data, frequency_figure_data, treemap_figure


def make_table(dosen: str, sentiment):
    labeled_data_df = labeled_data.loc[labeled_data.Dosen == dosen]
    if sentiment is not None:
        labeled_data_df = labeled_data_df.loc[labeled_data_df.Label.isin(sentiment)]
    labeled_data_df = labeled_data_df[['Nama Matkul', 'Jawaban', 'Label', ]]
    return labeled_data_df



def plotly_bar_matkul_dosen(dosen):
    df = viz_df_dosenmatkul.loc[viz_df_dosenmatkul.Dosen == dosen]
    fig = go.Figure([
        go.Bar(name='Positif',
               x=df["Nama Matkul"],
               y=df['positif']),
        go.Bar(name='Netral',
               x=df["Nama Matkul"],
               y=df['netral']),
        go.Bar(name='Negatif',
               x=df["Nama Matkul"],
               y=df['negatif']),
    ], layout={
        'xaxis': dict(rangeslider=dict(visible=True)),
        'barmode': 'group'
    }
    )
    return fig

def make_local_df(dosen: list):
    return labeled_data.loc[labeled_data.Dosen.isin(dosen)]


def make_df_sort(sort, asc, select_type='Dosen'):
    if select_type == 'Dosen':
        df = eda_df_cnt.copy()
    else:
        df = eda_df_cnt_matkul.copy()
    if sort == "positif":
        df_cnt = df.sort_values(by="positif", ascending=True if asc == "True" else False)
        df_pct = df.sort_values(by="pct_pos", ascending=True if asc == "True" else False)
    elif sort == "netral":
        df_cnt = df.sort_values(by="netral", ascending=True if asc == "True" else False)
        df_pct = df.sort_values(by="pct_net", ascending=True if asc == "True" else False)
    elif sort == "negatif":
        df_cnt = df.sort_values(by="negatif", ascending=True if asc == "True" else False)
        df_pct = df.sort_values(by="pct_neg", ascending=True if asc == "True" else False)
    else:
        df_cnt = df.sort_values(by=select_type, ascending=True if asc == "True" else False)
        df_pct = df.sort_values(by=select_type, ascending=True if asc == "True" else False)
    return df_cnt, df_pct


def plotly_bar(df, df_pct, select_type='Dosen'):
    figure_cnt = go.Figure([
        go.Bar(name='Positif',
               x=df[select_type],
               y=df['positif']),
        go.Bar(name='Netral',
               x=df[select_type],
               y=df['netral']),
        go.Bar(name='Negatif',
               x=df[select_type],
               y=df['negatif']),
    ], layout={
        'xaxis': dict(rangeslider=dict(visible=True)),
        'barmode': 'stack'
    }
    )
    figure_pct = go.Figure([go.Bar(name='Positif', x=df_pct[select_type],
                                   y=df_pct['pct_pos']),
                            go.Bar(name='Netral', x=df_pct[select_type],
                                   y=df_pct['pct_net']),
                            go.Bar(name='Negatif', x=df_pct[select_type],
                                   y=df_pct['pct_neg']),
                            ], layout={'barmode': "stack",
                                       "xaxis": dict(
                                           rangeslider=dict(visible=True))})
    return figure_cnt, figure_pct


def make_df_matkul(matkul):
    return labeled_data.loc[labeled_data['Nama Matkul'] == matkul]


def plotly_bar_matkul(df):
    fig = go.Figure()
    df = df.groupby(['Dosen', 'Label']).count().reset_index()
    for i, dosen in enumerate(df['Dosen'].unique()):
        df_plot = df[df['Dosen'] == dosen]
        fig.add_trace(go.Bar(
            x=df_plot.Label,
            y=df_plot.Jawaban,
            name=dosen
        ))
    fig.update_layout(barmode='group')
    return fig


OVERVIEW_SENTIMENT = [dbc.CardHeader("SUMMARY COUNT SENTIMENT ALL DOSEN"),
                      dbc.CardBody(
                          [
                              dbc.Row([
                                  dbc.Col([
                                      dcc.Tabs([
                                          dcc.Tab(
                                              label="BARCHART PER SENTIMENT",
                                              children=[
                                                  dcc.Graph(id='overview-sentiment',
                                                            figure=go.Figure([go.Bar(name="Semester Ganjil",
                                                                                     x=eda_df.loc[eda_df.Semester == 1][
                                                                                         'Label'],
                                                                                     y=eda_df['Jawaban']),
                                                                              go.Bar(name="Semester Genap",
                                                                                     x=eda_df.loc[eda_df.Semester == 2][
                                                                                         'Label'],
                                                                                     y=eda_df['Jawaban'])
                                                                              ], layout=dict(title="Jumlah "
                                                                                                   "keseluruhan "
                                                                                                   "sentimen tiap "
                                                                                                   "semester"))
                                                            ),
                                              ]
                                          ),
                                          dcc.Tab(
                                              label="BOXPLOT DOSEN",
                                              children=[
                                                  dcc.Graph(id='summary-boxplot',
                                                            figure=plotly_boxplot()),
                                              ]
                                          )
                                      ])
                                  ])
                              ]),

                          ],
                      ),
                      ]
SENTIMENT_DOSEN = [dbc.CardHeader("OVERALL SENTIMEN"),
                   dcc.Dropdown(
                       options=[
                           {'label': 'Dosen', 'value': 'Dosen'},
                           {'label': 'Matakuliah', 'value': 'Nama Matkul'},
                       ],
                       multi=False,
                       value="Dosen",
                       id="select-type"
                   ),
                   dbc.CardBody(
                       [
                           dbc.Row([
                               dbc.Col([
                                   html.H6("Sort by   :", style={'marginRight': '10px',
                                                                 'marginLeft': '10px'}),
                                   dcc.RadioItems(
                                       options=[
                                           {'label': "positif", 'value': "positif"},
                                           {'label': "netral", 'value': "netral"},
                                           {'label': "negatif", 'value': "negatif"},
                                       ],
                                       value="negatif",
                                       id="sort-filter",
                                       labelStyle={'display': 'inline-block',
                                                   'marginLeft': '15px'}
                                   ),
                               ]),
                               dbc.Col([
                                   html.H6("Ascending  :", style={'marginRight': '10px',
                                                                  'marginLeft': '10px'}),
                                   dcc.RadioItems(
                                       options=[
                                           {'label': "True", 'value': "True"},
                                           {'label': "False", 'value': "False"},
                                       ],
                                       value="True",
                                       id="asc-filter",
                                       labelStyle={'display': 'inline-block',
                                                   'marginLeft': '15px'}
                                   ),
                               ]),
                           ]),
                           dbc.Row([
                               dbc.Col([
                                   dcc.Tabs(
                                       id="tabs",
                                       children=[
                                           dcc.Tab(
                                               label="Count",
                                               children=[dcc.Graph(id='count-sentiment-dsn',

                                                                   )],
                                           ),
                                           dcc.Tab(
                                               label="Percentage",
                                               children=[dcc.Graph(id='pct-sentiment-dsn',

                                                                   )],
                                           ),
                                       ],
                                   )
                               ])
                           ]),

                       ],
                   ),
                   ]
WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("Most frequently used words")),
    dcc.Dropdown(
        options=[
            {'label': dosen, 'value': dosen} for dosen in DOSEN
        ],
        multi=True,
        value=[dosen for dosen in DOSEN],
        id="dosen-dropdown"
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-frequencies",
                            children=[dcc.Graph(id="frequency_figure")],
                            type="default",
                        )
                    ),
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Treemap",
                                        children=[
                                            dcc.Loading(
                                                id="loading-treemap",
                                                children=[dcc.Graph(id="bank-treemap")],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Wordcloud",
                                        children=[
                                            dcc.Loading(
                                                id="loading-wordcloud",
                                                children=[
                                                    dcc.Graph(id="bank-wordcloud")
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=8,
                    ),
                ]
            )
        ]
    ),
]
SUMMARY_DOSEN = [
    dbc.CardHeader("SUMMARY TIAP DOSEN"),
    dbc.Row([
        dbc.Col([
            html.H6("Pilih Dosen", style={'marginLeft': 5, 'marginTop': 10}),
            dcc.Dropdown(
                options=[
                    {'label': dosen, 'value': dosen} for dosen in DOSEN
                ],
                multi=False,
                value="ABF",
                id="dosen-filter"
            ),
        ]),
        dbc.Col([
            html.H6("Pilih Sentiment", style={'marginLeft': 5, 'marginTop': 10}),
            dcc.Dropdown(
                options=[
                    {'label': 'positif', 'value': 'positif'},
                    {'label': 'netral', 'value': 'netral'},
                    {'label': 'negatif', 'value': 'negatif'}
                ],
                multi=True,
                value=["positif", "netral", "negatif"],
                id="sentiment-filter"
            )
        ])
    ]),
    dbc.CardBody(
                [
                    dcc.Tabs(
                        [
                            dcc.Tab(
                                label="Kalimat",
                                children=[dt.DataTable(
                                    id='table-dosen',
                                    columns=[
                                        {"name": "Jawaban", "id": "Jawaban"},
                                        {"name": "Label", "id": "Label"},
                                    ],

                                    page_current=0,
                                    page_action='custom',
                                    page_size=8,
                                    style_cell={
                                        'whiteSpace': 'normal',
                                        'textAlign': 'left',
                                    },
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'Jawaban'},
                                         'width': '80px'},
                                        {'if': {'column_id': 'Label'},
                                         'width': '9px'},
                                    ],

                                )
                            ]),
                            dcc.Tab(
                                label="Graph",
                                children=
                                        [
                                            dcc.Graph(id="bar-matkul-dosen")
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),

                ]
SUMMARY_MATKUL = [
    dbc.CardHeader("SUMMARY TIAP MATKUL"),
    dbc.Row([
        dbc.Col([
            html.H6("Pilih Mata Kuliah", style={'marginLeft': 5, 'marginTop': 10}),
            dcc.Dropdown(
                options=[
                    {'label': matkul, 'value': matkul} for matkul in matkul_dosen.keys()
                ],
                multi=False,
                value="KALKULUS 1B",
                id="matkul-filter"
            ),
        ]),
        dbc.Col([
            html.H6("Pilih Dosen", style={'marginLeft': 5, 'marginTop': 10}),
            dcc.Dropdown(
                multi=True,
                options=[],
                id="dosen-matkul-filter"
            )
        ])
    ]),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dt.DataTable(
                                id='table-matkul',
                                columns=[
                                    {"name": "Jawaban", "id": "Jawaban"},
                                    {"name": "Label", "id": "Label"},
                                ],

                                page_current=0,
                                page_action='custom',
                                page_size=5,
                                style_cell={
                                    'whiteSpace': 'normal',
                                    'textAlign': 'left',
                                },
                                style_cell_conditional=[
                                    {'if': {'column_id': 'Jawaban'},
                                     'width': '80px'},
                                    {'if': {'column_id': 'Label'},
                                     'width': '9px'},
                                ],

                            )
                        ],
                        # md=6,

                    ),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id="loading-barchart-matkul",
                                children=[
                                    dcc.Graph(id="bar-matkul")
                                ],
                                type="default",
                            )
                        ]
                    )
                ]
            )
        ]
    ),
]
BODY = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H3(
                        "Dashboard ini dibuat menggunakan Dash-plotly untuk kepentingan pengambilan keputusan di "
                        "Program Studi Sistem Informasi Tel-U.",
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
                                       "Proses cleansing meliputi Stemming, Tokenisasi, Stopwords Removal, "
                                       "Punctuations Removal. "
                                       "Proses feature extraction meliputi Term Frequency-Inverse Document Frequency "
                                       "(TF-IDF) yang menghasilkan features berupa vector. "
                                       "Proses pemodelan meliputi Random Over Sampling dan Voting Classification "
                                       "dengan estimator Random Forest, Naive Bayes dan Support Vector Machine"),
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
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    OVERVIEW_SENTIMENT
                )
            ),
        ], style={'marginTop': 30}
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    SENTIMENT_DOSEN
                )
            ),
        ], style={'marginTop': 30}
        ),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    SUMMARY_MATKUL
                )
            ),
        ], style={'marginTop': 30}
        ),

        dbc.Row([
            dbc.Col(
                dbc.Card(
                    SUMMARY_DOSEN
                )
            ),
        ], style={'marginTop': 30}
        ),

        dbc.Row([
            dbc.Col(
                dbc.Card(
                    WORDCLOUD_PLOTS
                )
            ),
        ], style={'marginTop': 30}
        ),
    ]
)


# app.title = 'Dashboard EDOM'
def Sentiment():
    layout = html.Div(children=[NAVBAR, BODY])
    return layout
