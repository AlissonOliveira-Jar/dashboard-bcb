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

    dbc.Row([
        dbc.Col(md=4, children=[
            dbc.Card(
                [dbc.CardHeader("Último Valor Registrado"),
                 dbc.CardBody(id='card-body-recente', className="text-center")],
                className="mb-4"
            )
        ]),

        dbc.Col(md=4, children=[
            dbc.Card(
                [dbc.CardHeader("Variação no Período"),
                 dbc.CardBody(id='card-body-variacao', className="text-center")],
                className="mb-4"
            )
        ]),

        dbc.Col(md=4, children=[
            dbc.Card(
                [dbc.CardHeader("Média no Período"),
                 dbc.CardBody(id='card-body-media', className="text-center")],
                className="mb-4"
            )
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
    [Output('main-chart', 'figure'),
     Output('card-body-recente', 'children'),
     Output('card-body-variacao', 'children'),
     Output('card-body-media', 'children')],
    [Input('indicador-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph_and_cards(codigo_sgs, start_date, end_date):
    if not all([codigo_sgs, start_date, end_date]):
        return dash.no_update

    df_full = fetch_sgs_data(codigo_sgs)

    fig_vazia = px.line(title="Não foi possível carregar os dados para este indicador.") \
        .update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    if df_full.empty:
        card_vazio = html.H4("N/A", className="text-danger")
        return fig_vazia, card_vazio, card_vazio, card_vazio

    df_filtered = df_full.loc[start_date:end_date]

    if df_filtered.empty:
        card_vazio = html.H4("N/A", className="text-warning")
        return fig_vazia, card_vazio, card_vazio, card_vazio

    info = INDICADORES[str(codigo_sgs)]
    unidade = info['unidade']
    nome_coluna = df_filtered.columns[0]

    unidade_variacao = "p.p." if "%" in unidade else unidade

    valor_recente = df_filtered.iloc[-1, 0]
    data_recente = df_filtered.index[-1].strftime('%d/%m/%Y')
    card_recente_content = html.Div([
        html.H4(f"{valor_recente:.2f} {unidade}", className="text-primary"),
        html.P(f"em {data_recente}")
    ])

    media_periodo = df_filtered[nome_coluna].mean()
    card_media_content = html.Div([
        html.H4(f"{media_periodo:.2f} {unidade}", className="text-info"),
        html.P(f"entre {start_date} e {end_date}")
    ])

    if len(df_filtered) < 2:
        card_variacao_content = html.Div([
            html.H4("N/A", className="text-warning"),
            html.P("Período curto demais para calcular variação")
        ])
    else:
        valor_inicial = df_filtered.iloc[0, 0]
        data_inicial = df_filtered.index[0].strftime('%d/%m/%Y')
        variacao_abs = valor_recente - valor_inicial

        cor_variacao = "text-success" if variacao_abs >= 0 else "text-danger"

        card_variacao_content = html.Div([
            html.H4(f"{variacao_abs:+.2f} {unidade_variacao}", className=cor_variacao),
            html.P(f"Desde {data_inicial}")
        ])

    # 5. Criação do Gráfico
    fig = px.line(
        df_filtered.reset_index(),
        x='Data',
        y=nome_coluna,
        title=f"Série Histórica - {info['nome']}"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title="Período",
        yaxis_title=unidade
    )

    return fig, card_recente_content, card_variacao_content, card_media_content

if __name__ == '__main__':
    app.run(debug=True)
