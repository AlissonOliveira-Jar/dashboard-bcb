import requests
import pandas as pd

from datetime import datetime
from functools import lru_cache
from dateutil.relativedelta import relativedelta

INDICADORES = {
    # SELIC (Diária)
    '1178': {
        'nome': 'Taxa SELIC (Meta)',
        'periodicidade': 'diaria',
        'data_inicio': '1999-06-22',
        'unidade': '% a.a.'
    },
    # IPCA (Mensal)
    '433': {
        'nome': 'IPCA (Mensal)',
        'periodicidade': 'mensal',
        'data_inicio': '1980-01-01',
        'unidade': '% a.m.'
    },
    '13522': {
        'nome': 'IPCA (Acumulado 12m)',
        'periodicidade': 'mensal',
        'data_inicio': '1980-01-01',
        'unidade': '% a.a.'
    },
    # CÂMBIO PTAX (Diário)
    '1': {
        'nome': 'Dólar (USD) - PTAX Compra',
        'periodicidade': 'diaria',
        'data_inicio': '1994-11-18',
        'unidade': 'R$'
    },
    '10813': {
        'nome': 'Dólar (USD) - PTAX Venda',
        'periodicidade': 'diaria',
        'data_inicio': '1994-11-18',
        'unidade': 'R$'
    },
    '21619': {
        'nome': 'Euro (EUR) - PTAX Compra',
        'periodicidade': 'diaria',
        'data_inicio': '1999-01-04',
        'unidade': 'R$'
    },
    '21620': {
        'nome': 'Euro (EUR) - PTAX Venda',
        'periodicidade': 'diaria',
        'data_inicio': '1999-01-04',
        'unidade': 'R$'
    },
}


@lru_cache(maxsize=16)
def fetch_sgs_data(cod_sgs):
    """
    Busca uma série temporal do SGS (BCB) pelo seu código.
    Respeita a paginação de 10 anos para séries diárias.
    """
    if str(cod_sgs) not in INDICADORES:
        print(f"Código SGS {cod_sgs} não encontrado no dicionário.")
        return pd.DataFrame()

    info = INDICADORES[str(cod_sgs)]
    nome_coluna = f"{info['nome']} ({info['unidade']})"
    data_inicio = datetime.strptime(info['data_inicio'], '%Y-%m-%d')
    data_hoje = datetime.now()
    df_final = pd.DataFrame()

    print(f"Buscando dados para: {info['nome']}...")

    try:
        if info['periodicidade'] == 'diaria':
            data_inicio_bloco = data_inicio
            while data_inicio_bloco < data_hoje:
                data_fim_bloco = data_inicio_bloco + relativedelta(years=10) - relativedelta(days=1)
                if data_fim_bloco > data_hoje:
                    data_fim_bloco = data_hoje

                data_inicio_str = data_inicio_bloco.strftime('%d/%m/%Y')
                data_fim_str = data_fim_bloco.strftime('%d/%m/%Y')

                url = (
                    f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod_sgs}/dados?'
                    f'formato=json&dataInicial={data_inicio_str}&dataFinal={data_fim_str}'
                )

                response = requests.get(url, timeout=10)
                response.raise_for_status()
                dados = response.json()

                if dados:
                    df_bloco = pd.DataFrame(dados)
                    df_final = pd.concat([df_final, df_bloco], ignore_index=True)

                data_inicio_bloco = data_fim_bloco + relativedelta(days=1)

        else:
            data_inicio_str = data_inicio.strftime('%d/%m/%Y')
            data_fim_str = data_hoje.strftime('%d/%m/%Y')

            url = (
                f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod_sgs}/dados?'
                f'formato=json&dataInicial={data_inicio_str}&dataFinal={data_fim_str}'
            )

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            dados = response.json()
            if dados:
                df_final = pd.DataFrame(dados)

        if df_final.empty:
            print(f"Nenhum dado retornado para {info['nome']}.")
            return pd.DataFrame(columns=['Data', nome_coluna]).set_index('Data')

        df_final = df_final.rename(columns={'data': 'Data', 'valor': nome_coluna})
        df_final['Data'] = pd.to_datetime(df_final['Data'], format='%d/%m/%Y')
        df_final[nome_coluna] = pd.to_numeric(df_final[nome_coluna])
        df_final = df_final.drop_duplicates(subset=['Data']).set_index('Data').sort_index()

        print(f"Busca de '{info['nome']}' concluída. Total de {len(df_final)} registros.")
        return df_final

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API para {cod_sgs}: {e}")
        return pd.DataFrame(columns=['Data', nome_coluna]).set_index('Data')
