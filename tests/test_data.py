import pandas as pd
import requests
from datetime import datetime
from data import fetch_sgs_data, INDICADORES

MOCK_JSON_MENSAL = [
    {"data": "01/01/2025", "valor": "0.50"},
    {"data": "01/02/2025", "valor": "0.45"}
]

MOCK_JSON_DIARIA_P1 = [
    {"data": "22/06/1999", "valor": "45.00"},
    {"data": "23/06/1999", "valor": "45.00"}
]
MOCK_JSON_DIARIA_P2 = [
    {"data": "22/06/2009", "valor": "10.00"},
    {"data": "23/06/2009", "valor": "9.50"}
]

def test_fetch_serie_mensal_sucesso(mocker):
    """
    Testa o caminho para uma série mensal (ex: IPCA 433).
    Verifica se a API é chamada 1 vez e se os dados são tratados.
    """

    fetch_sgs_data.cache_clear()

    mock_response = mocker.Mock()
    mock_response.json.return_value = MOCK_JSON_MENSAL
    mock_response.raise_for_status = mocker.Mock()

    mocker.patch('data.requests.get', return_value=mock_response)

    df = fetch_sgs_data('433')  # 433 = IPCA Mensal

    assert not df.empty
    assert len(df) == 2
    assert df.index[0] == pd.to_datetime('2025-01-01')
    assert df.columns[0] == INDICADORES['433']['nome'] + ' (' + INDICADORES['433']['unidade'] + ')'
    assert df.iloc[1, 0] == 0.45  # Verifica o valor


def test_fetch_serie_diaria_sucesso_paginacao(mocker):
    """
    Teste para o caminho para uma série diária (ex: SELIC 1178).
    """

    fetch_sgs_data.cache_clear()

    mock_resp1 = mocker.Mock()
    mock_resp1.json.return_value = MOCK_JSON_DIARIA_P1
    mock_resp1.raise_for_status = mocker.Mock()

    mock_resp2 = mocker.Mock()
    mock_resp2.json.return_value = MOCK_JSON_DIARIA_P2
    mock_resp2.raise_for_status = mocker.Mock()

    mock_requests_get = mocker.patch('data.requests.get', side_effect=[mock_resp1, mock_resp2])

    mock_datetime_class = mocker.MagicMock()
    mock_datetime_class.now.return_value = datetime(2009, 6, 23)
    mock_datetime_class.strptime = datetime.strptime
    mocker.patch('data.datetime', mock_datetime_class)

    df = fetch_sgs_data('1178')

    assert not df.empty
    assert len(df) == 4

    assert mock_requests_get.call_count == 2

    assert df.index[0] == pd.to_datetime('1999-06-22')
    assert df.index[-1] == pd.to_datetime('2009-06-23')
    assert df.iloc[-1, 0] == 9.50


def test_fetch_api_falha(mocker):
    """
    Testa  o que acontece se a API do BCB falhar (ex: erro 500 ou timeout).
    A função deve falhar graciosamente e retornar um DataFrame vazio.
    """

    fetch_sgs_data.cache_clear()

    mocker.patch(
        'data.requests.get',
        side_effect=requests.exceptions.RequestException("Simulação de Erro de Rede")
    )

    df = fetch_sgs_data('433')

    assert df.empty


def test_fetch_dados_vazios(mocker):
    """
    Testa o que acontece se a API retornar 200 OK, mas com uma lista vazia [].
    """

    mock_response = mocker.Mock()
    mock_response.json.return_value = []  # Resposta vazia
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('data.requests.get', return_value=mock_response)

    df = fetch_sgs_data('433')

    assert df.empty

def test_fetch_cod_invalido():
    """
    Testa o que acontece se um código que não está no dicionário INDICADORES
    for passado. A função não deve nem tentar chamar a API.
    """

    df = fetch_sgs_data('99999')

    assert df.empty
