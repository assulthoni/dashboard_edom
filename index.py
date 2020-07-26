import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_auth
from kualitatif import Kualitatif, TABLENAME_KUALITATIF
from kuantitatif import Kuantitatif, TABLENAME_KUANTITATIF
from data import username_pass, KODE_NAMA_LENGKAP_DOSEN
from app import select_by_semester
import warnings

warnings.filterwarnings('ignore')

VALID_USERNAME_PASSWORD_PAIRS = username_pass

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                url_base_pathname='/dashboard',
                )
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

])
app.title = "Dashboard EDOM SI"

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


def transform_kuantitatif(df):
    df_t = df[['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'SUBJECTNAME',
               'CLASS', 'QUESTIONCATEGORY',
               'QUESTION']].join(pd.get_dummies(df['ANSWER'])
                                 ).groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'SUBJECTNAME',
                                            'CLASS', 'QUESTIONCATEGORY',
                                            'QUESTION']).sum()
    df_t['skor'] = (((df_t['Sangat puas'] * 4) + (df_t['Puas'] * 3)
                     + (df_t['Tidak puas'] * 2) + (df_t['Sangat tidak puas'] * 1)) /
                    (df_t['Sangat puas'] + df_t['Puas'] + df_t['Tidak puas']
                     + df_t['Sangat tidak puas'])) * 25
    df_t.reset_index(inplace=True)
    return df_t


@app.callback(Output('intermediate-value', 'children'),
              [
                  Input('dropdown-year-start', 'value'),
                  Input('dropdown-year-end', 'value'),
                  Input('dropdown_semester', 'value'),
              ])
def sync_data(yearstart, yearend, semester):
    df = select_by_semester(tablename=TABLENAME_KUANTITATIF, yearstart=yearstart, yearend=yearend, semester=semester)
    df_t = transform_kuantitatif(df)
    return df_t.to_json(date_format='iso', orient='split')


@app.callback(Output('intermediate-value-kw', 'children'),
              [
                  Input('dropdown-year-start-kw', 'value'),
                  Input('dropdown-year-end-kw', 'value'),
                  Input('dropdown_semester-kw', 'value'),
              ])
def sync_data_kw(yearstart, yearend, semester):
    df = select_by_semester(tablename=TABLENAME_KUALITATIF, yearstart=yearstart, yearend=yearend, semester=semester)
    df_t = df.loc[df.QUESTION == 'Berikan masukan untuk meningkatkan performansi dosen yang mengajar matakuliah ini']
    return df_t.to_json(date_format='iso', orient='split')


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/kualitatif':
        return Kualitatif()
    else:
        return Kuantitatif()


# """
# call back untuk kuantitatif, seluruh fungsi dibawah untuk update data dan graph
# """
@app.callback(Output('line-histori-edom', 'figure'),
              [Input('intermediate-value', 'children')])
def plot_histori_edom(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER']).mean()['skor'].reset_index()
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: ' Ganjil' if x == 1 else ' Genap')
    data["period"] = data["SCHOOLYEAR"].astype(str) + data["SEMESTER"].astype(str)
    return go.Figure(
        [
            go.Scatter(
                x=data.period,
                y=data.skor,

            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('gauge-kepuasan', 'figure'),
              [Input('intermediate-value', 'children')])
def plot_gauge(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER']).mean()['skor'].reset_index()
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: ' Ganjil' if x == 1 else ' Genap')
    data["period"] = data["SCHOOLYEAR"].astype(str) + data["SEMESTER"].astype(str)
    value = float(round(data.skor.mean(), 2))
    # print(type(value))
    return go.Figure(
        [
            go.Indicator(
                # domain={'x': [0, 1], 'y': [0, 1]},
                value=value,
                mode="gauge+number+delta",
                delta={'reference': 85.0, "valueformat": ".2f"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "mediumblue"},
                       'threshold': {
                           'line': {'color': "green",
                                    'width': 4},
                           'thickness': 0.75,
                           'value': 85.0},
                       }
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=15,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('prosentase-matkul-km', 'figure'),
              [Input('intermediate-value', 'children')]
              )
def plot_prosentase_matkul(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'SUBJECTNAME']).mean()['skor'].reset_index()
    data['status'] = data.skor.apply(lambda x: 'diatas' if x >= 85 else 'dibawah')
    res = data.status.value_counts().reset_index()
    return go.Figure(
        [
            go.Pie(
                labels=['diatas KM', 'dibawah KM'],
                values=[int(res.loc[res['index'] == 'diatas']['status'].iloc[0]),
                        int(res.loc[res['index'] == 'dibawah']['status'].iloc[0])],
                marker={
                    'colors': ['lightgreen', 'tomato']
                }
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('prosentase-dosen-km', 'figure'),
              [Input('intermediate-value', 'children')])
def plot_prosentase_dosen(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE']).mean()['skor'].reset_index()
    data['status'] = data.skor.apply(lambda x: 'diatas' if x >= 85 else 'dibawah')
    res = data.status.value_counts().reset_index()
    return go.Figure(
        [
            go.Pie(
                labels=['diatas KM', 'dibawah KM'],
                values=[int(res.loc[res['index'] == 'diatas']['status'].iloc[0]),
                        int(res.loc[res['index'] == 'dibawah']['status'].iloc[0])],
                marker={
                    'colors': ['lightgreen', 'tomato']
                }
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('table-kepuasan-matkul', 'data'),
              [Input('intermediate-value', 'children'),
               Input('table-kepuasan-matkul', "page_current"),
               Input('table-kepuasan-matkul', "page_size")])
def table_update_matkul(json_data, current, size):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'SUBJECTNAME']).mean()['skor'].reset_index()
    data['status'] = data.skor.apply(lambda x: 'diatas' if x >= 85 else 'dibawah')
    data['skor'] = data.skor.apply(lambda x: round(x, 2))
    data = data.sort_values(by=['skor', 'SCHOOLYEAR'], ascending=True)
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: ' Ganjil' if x == 1 else ' Genap')
    res = data[['SCHOOLYEAR', 'SEMESTER', 'SUBJECTNAME', 'skor']]
    res.columns = ['TA', 'Semester', 'Matkul', 'Nilai']
    return res.iloc[
           current * size:(current + 1) * size
           ].to_dict('records')


@app.callback(Output('table-dosen-dibawah-km', 'data'),
              [
                  Input('intermediate-value', 'children'),
                  Input('table-dosen-dibawah-km', 'page_current'),
                  Input('table-dosen-dibawah-km', 'page_size')
              ])
def table_update_dosen(json_data, current, size):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE']).mean()['skor'].reset_index()
    data['status'] = data.skor.apply(lambda x: 'diatas' if x >= 85 else 'dibawah')
    data['skor'] = data.skor.apply(lambda x: round(x, 2))
    data = data.sort_values(by=['skor', 'SCHOOLYEAR'], ascending=True)
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: ' Ganjil' if x == 1 else ' Genap')
    res = data[['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'skor']]
    res.columns = ['TA', 'Semester', 'Dosen', 'Nilai']
    res['Dosen'] = res.Dosen.map(KODE_NAMA_LENGKAP_DOSEN)
    return res.iloc[
           current * size:(current + 1) * size
           ].to_dict('records')


@app.callback(Output('bar-aspek-terendah', 'figure'),
              [Input('intermediate-value', 'children')])
def bar_update_aspek_matkul(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'SUBJECTNAME', 'QUESTIONCATEGORY']).mean()['skor'].reset_index()
    data = data.groupby(['QUESTIONCATEGORY']).median()['skor'].reset_index()
    data['skor'] = data.skor.apply(lambda x: round(x, 2))
    data = data.loc[data.skor < 85]
    data = data.sort_values(by=['skor'], ascending=True
                            )
    return go.Figure(
        [
            go.Bar(
                x=data.QUESTIONCATEGORY,
                y=data.skor,
                marker={
                    'color': 'tomato'
                },
                text=data.skor,
                textposition='auto',
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('bar-aspek-terendah-dosen', 'figure'),
              [Input('intermediate-value', 'children')])
def bar_update_aspek_dosen(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'QUESTIONCATEGORY']).mean()['skor'].reset_index()
    data = data.groupby(['QUESTIONCATEGORY']).median()['skor'].reset_index()
    data['skor'] = data.skor.apply(lambda x: round(x, 2))
    data = data.loc[data.skor < 85]
    data = data.sort_values(by=['skor'], ascending=True)
    print(data.head())
    return go.Figure(
        [
            go.Bar(
                x=data.QUESTIONCATEGORY,
                y=data.skor,
                marker={
                    'color': 'tomato'
                },
                text=data.skor,
                textposition='auto',
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('histori-dosen', 'figure'),
              [Input('intermediate-value', 'children'),
               Input('dropdown-dosen', 'value')])
def histori_dosen(json_data, dosen):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE']).mean()['skor'].reset_index()
    data = data[data['LECTURERCODE'].isin(dosen)]
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: ' Ganjil' if x == 1 else ' Genap')
    data["period"] = data["SCHOOLYEAR"].astype(str) + data["SEMESTER"].astype(str)
    data = data.sort_values(by=['period'], ascending=True)
    return go.Figure(
        [
            go.Scatter(
                x=data.loc[data.LECTURERCODE == d]['period'],
                y=data.loc[data.LECTURERCODE == d]['skor'],
                name=d,
                text=data.loc[data.LECTURERCODE == d]['skor'].apply(lambda x: round(x, 2)),
            ) for d in dosen
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=10,
                t=10,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('bar-matkul-dosen', 'figure'),
              [Input('intermediate-value', 'children'),
               Input('dropdown-dosen', 'value')])
def histori_dosen(json_data, dosen):
    df = pd.read_json(json_data, orient='split')
    data = df.groupby(['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'SUBJECTNAME']).mean()['skor'].reset_index()
    data = data[data['LECTURERCODE'].isin(dosen)]
    data['SUBJECTNAME'] = data['SUBJECTNAME'] + ' - ' + data['SCHOOLYEAR'].astype(str)
    return go.Figure(
        [
            go.Bar(
                x=data.loc[data.LECTURERCODE == d]['SUBJECTNAME'],
                y=data.loc[data.LECTURERCODE == d]['skor'],
                name=d,
                text=data.loc[data.LECTURERCODE == d]['skor'].apply(lambda x: round(x, 2)),
                textposition='auto'
            ) for d in dosen
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                t=10,
            ),
            'height': 250,
        }
    )


# """
# call back untuk kualitatif, seluruh fungsi dibawah untuk update data dan graph
# """

@app.callback(Output('avg-sentiment', 'figure'),
              [
                  Input('intermediate-value-kw', 'children')
              ])
def pie_avg(json_data):
    df = pd.read_json(json_data, orient='split')
    data = df.LABEL.value_counts().reset_index()
    data = data.sort_values(['index'])
    return go.Figure(
        [
            go.Pie(
                labels=data['index'],
                values=data['LABEL'],
                marker={
                    'colors': ['tomato','lightgreen','lightblue',
                               ]
                }
            )
        ],
        layout={
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('histori-sentiment-edom', 'figure'),
              [
                  Input('intermediate-value-kw', 'children')
              ])
def histori_sentimen(json_data):
    df = pd.read_json(json_data, orient='split')
    df = df.groupby(by=['SCHOOLYEAR', 'SEMESTER', 'LABEL']).count().reset_index()
    data = df[['SCHOOLYEAR', 'SEMESTER', 'LABEL', 'ANSWER']]
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: 'ganjil' if x == 1 else 'genap')
    data['period'] = data['SCHOOLYEAR'].astype(str) + ' ' + data['SEMESTER'].astype(str)
    data = data.sort_values(by=['period'])
    data_pct = data.groupby(by=['period', 'LABEL']).agg({'ANSWER': 'sum'})
    data_pct = data_pct.groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).reset_index()
    return go.Figure(
        [
            go.Bar(
                x=data_pct.loc[data_pct.LABEL == 'positif'].period,
                name='Positif',
                y=data_pct.loc[data_pct.LABEL == 'positif'].ANSWER,
                marker={
                    'color': 'lightblue'
                },
                text=data_pct.loc[data_pct.LABEL == 'positif'].period.values,
                hovertemplate="<b>%{text}</b>:<br>Positif - %{y:.2f}<extra></extra>"
            ),
            go.Bar(
                x=data_pct.loc[data_pct.LABEL == 'netral'].period,
                name='Netral',
                y=data_pct.loc[data_pct.LABEL == 'netral'].ANSWER,
                marker={
                    'color': 'lightgreen'
                },
                text=data_pct.loc[data_pct.LABEL == 'netral'].period.values,
                hovertemplate="<b>%{text}</b>:<br>Netral - %{y:.2f}<extra></extra>"
            ),
            go.Bar(
                x=data_pct.loc[data_pct.LABEL == 'negatif'].period,
                name='Negatif',
                y=data_pct.loc[data_pct.LABEL == 'negatif'].ANSWER,
                marker={
                    'color': 'tomato'
                },
                text=data_pct.loc[data_pct.LABEL == 'negatif'].period.values,
                hovertemplate="<b>%{text}</b>:<br>Negatif - %{y:.2f}<extra></extra>"
            ),
        ],
        layout={
            'barmode': 'stack',
            'margin': dict(
                l=5,
                r=5,
                b=5,
                t=5,
                pad=0,
            ),
            'height': 250,
        }
    )


@app.callback(Output('histori-sentiment-dosen', 'figure'),
              [
                  Input('intermediate-value-kw', 'children'),
                  Input('dropdown-dosen-kw', 'value')
              ])
def histori_dosen(json_data, dosen):
    df = pd.read_json(json_data, orient='split')
    df = df[df['LECTURERCODE'].isin(dosen)]
    df = df.groupby(by=['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'LABEL']).count().reset_index()
    data = df[['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'LABEL', 'ANSWER']]
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: 'ganjil' if x == 1 else 'genap')
    data['period'] = data['SCHOOLYEAR'].astype(str) + ' ' + data['SEMESTER'].astype(str)
    data = data.sort_values(by=['period'])
    data = data[['period', 'LECTURERCODE', 'LABEL', 'ANSWER']]
    data = data.pivot_table('ANSWER', ['period', 'LECTURERCODE'], 'LABEL').reset_index()
    fig = go.Figure()
    print(data)
    int_offset = 0
    for d in dosen:
        res = data.loc[data.LECTURERCODE == d]
        res['pct-pos'] = res['positif'] / (res['netral'] + res['positif'] + res['negatif']) * 100
        res['pct-net'] = res['netral'] / (res['netral'] + res['positif'] + res['negatif']) * 100
        res['pct-neg'] = res['negatif'] / (res['netral'] + res['positif'] + res['negatif']) * 100
        fig.add_trace(
            go.Bar(
                x=res['period'],
                y=res['pct-pos'],
                name='Positif - ' + str(d),
                # offsetgroup=int_offset,
                marker={
                    'color': 'lightblue'
                },
                text=res['positif'].values,
                hovertemplate="<b>"+str(d)+"</b>:<br>Positif - %{y:.2f} %<br>"
                                           "%{text} rows<extra></extra>"
            )
        )
        fig.add_trace(
            go.Bar(
                x=res['period'],
                y=res['pct-net'],
                name='Netral - ' + str(d),
                # offsetgroup=int_offset,
                # base=res['pct-pos'],
                marker={
                    'color': 'lightgreen'
                },
                text=res['netral'].values,
                hovertemplate="<b>"+str(d)+"</b>:<br>Netral - %{y:.2f}"
                                           "%{text} rows<extra></extra>"
            )
        )
        fig.add_trace(
            go.Bar(
                x=res['period'],
                y=res['pct-neg'],
                name='Negatif - ' + str(d),
                # offsetgroup=int_offset,
                # base=res['pct-pos'] + res['pct-net'],
                marker={
                    'color': 'tomato'
                },
                text=res['negatif'].values,
                hovertemplate="<b>" + str(d) + "</b>:<br>Negatif - %{y:.2f}"
                                               "%{text} rows<extra></extra>",
            ),

        )

        int_offset += 1
    fig.update_layout(
        {'margin': dict(
            l=5,
            r=5,
            b=5,
            t=5,
            pad=0,
        ),
        })
    return fig


@app.callback(Output('dosen-sentiment-negatif', 'data'),
              [
                  Input('intermediate-value-kw', 'children'),
                  Input('dosen-sentiment-negatif', "page_current"),
                  Input('dosen-sentiment-negatif', "page_size")
              ])
def table_dosen_negatif(json_data, page_current, page_size):
    df = pd.read_json(json_data, orient='split')
    df = df.groupby(by=['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'LABEL']).count().reset_index()
    data = df[['SCHOOLYEAR', 'SEMESTER', 'LECTURERCODE', 'LABEL', 'ANSWER']]
    data['SEMESTER'] = data.SEMESTER.apply(lambda x: 'ganjil' if x == 1 else 'genap')
    data['period'] = data['SCHOOLYEAR'].astype(str) + ' ' + data['SEMESTER'].astype(str)
    data = data.pivot_table('ANSWER', ['period', 'LECTURERCODE'], 'LABEL').reset_index()
    data = data.fillna(0)
    data['pct-neg'] = data['negatif'] / (data['netral'] + data['positif'] + data['negatif']) * 100
    data = data.sort_values(by=['pct-neg'], ascending=False)
    res = data[['period', 'LECTURERCODE', 'pct-neg']]
    res.columns = ['Periode', 'Dosen', 'Persentase']
    res['Dosen'] = res.Dosen.map(KODE_NAMA_LENGKAP_DOSEN)
    return res.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
