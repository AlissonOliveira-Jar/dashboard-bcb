import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from datetime import date
from dateutil.relativedelta import relativedelta

from data import fetch_sgs_data, INDICADORES

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

dropdown_options = [
    {'label': f"{info['nome']} ({info['unidade']})", 'value': codigo}
    for codigo, info in INDICADORES.items()
]

data_hoje = date.today()
data_5_anos_atras = data_hoje - relativedelta(years=5)

app.layout = dbc.Container(fluid=True, className="dbc", children=[

    dbc.Row(
        dbc.Col(
            html.H1("Dashboard de Indicadores Econômicos (BCB)",
                    className="text-center text-primary my-4"),
            width=12
        )
    ),

    dbc.Row([
        dbc.Col(md=6, children=[
            dbc.Card(dbc.CardBody([
                html.H5("Selecione o Indicador", className="card-title"),
                dcc.Dropdown(
                    id='indicador-dropdown',
                    options=dropdown_options,
                    value='1178',   # SELIC
                    clearable=False
                )
            ]))
        ]),

        dbc.Col(md=6, children=[
            dbc.Card(dbc.CardBody([
                html.H5("Selecione o Período", className="card-title"),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=date(1990, 1, 1).isoformat(),
                    max_date_allowed=data_hoje.isoformat(),
                    start_date=data_5_anos_atras.isoformat(),
                    end_date=data_hoje.isoformat(),
                    display_format='DD/MM/YYYY'
                )
            ]))
        ]),
    ], className="mb-4"),

    dbc.Row(
        dbc.Col(
            dbc.Card(dbc.CardBody([
                dcc.Loading(
                    id="loading-spinner",
                    type="circle",
                    children=dcc.Graph(id='main-chart', style={'height': '60vh'})
                )
            ])),
            width=12
        )
    )
])

@app.callback(
    Output('main-chart', 'figure'),
    [Input('indicador-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(cod_sgs, start_date, end_date):
    if not all([cod_sgs, start_date, end_date]):
        return dash.no_update

    df_full = fetch_sgs_data(cod_sgs)

    if df_full.empty:
        return px.line(title="Não foi possível carregar os dados para este indicador.") \
            .update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    df_filtered = df_full.loc[start_date:end_date]

    nome_coluna = df_filtered.columns[0]

    fig = px.line(
        df_filtered.reset_index(),
        x='Data',
        y=nome_coluna,
        title=f"Série Histórica - {INDICADORES[str(cod_sgs)]['nome']}"
    )

    # 5. Estiliza o gráfico
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title="Período",
        yaxis_title=INDICADORES[str(cod_sgs)]['unidade']
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
