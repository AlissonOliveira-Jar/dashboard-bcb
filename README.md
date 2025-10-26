# Dashboard de macroeconomia do Brasil consumindo API do Banco Central do Brasil

Este projeto é um dashboard interativo construído com Python e Dash para visualizar e analisar 
indicadores macroeconômicos chave do Brasil (SELIC, IPCA, Câmbio PTAX) em tempo real, consumindo 
diretamente as APIs de Dados Abertos do Banco Central do Brasil (BCB).

## 🚀 Features (Funcionalidades) - EM CONSTRUÇÃO

Escopo Mínimo

Visualização da série histórica da Taxa SELIC (Meta). ✅

Visualização da série histórica do IPCA (Mensal e Acumulado 12m). ✅

Visualização do Câmbio PTAX (USD e EUR). ✅

Filtros interativos por período (DatePickerRange). ✅

Filtros interativos por indicador/moeda (Dropdown). ✅

Funcionalidades Adicionais (Excelente)

Cartões de Insight: Resumo com os valores mais recentes e variação (ex: "IPCA 12m: Y%"). ❌

Aba de Expectativas: Visualização das projeções do Boletim Focus (IPCA, PIB, Câmbio).

Cache de Dados: Uso de Flask-Caching para reduzir a latência e o número de chamadas às APIs do BCB.

Tema Claro/Escuro: Toggle para alternar o tema do dashboard (Dash Bootstrap Components).

Design Responsivo: O layout se adapta a dispositivos móveis. ✅

## 🛠️ Tecnologias Utilizadas

Python 3.12.9

Dash & Plotly: Para a construção do dashboard e gráficos interativos.

Dash Bootstrap Components: Para layout responsivo e componentes de UI modernos.

Pandas: Para manipulação e transformação dos dados.

## ⚙️ Instalação e Execução

1. Ambiente Local (via venv)

Pré-requisitos: Python 3.12.9 ou superior e pip.

Clone o repositório:

```terminal
git clone git@github.com:AlissonOliveira-Jar/dashboard-bcb.git
```
cd dashboard-bcb 

Crie e ative um ambiente virtual:

**Windows**
```terminal
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS**
```terminal
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```terminal
pip install -r requirements.txt
```

Execute a aplicação:

```terminal
python app.py
```

Acesse o dashboard no seu navegador: http://127.0.0.1:8050

## 📊 Fontes dos Dados

Todos os dados são obtidos em tempo real do Portal de Dados Abertos do Banco Central do Brasil.

SGS (Sistema Gerenciador de Séries Temporais): SELIC, IPCA.

PTAX: Cotações de câmbio.

Expectativas: Dados do Boletim Focus.

## 📄 Licença

Este projeto está sob a licença MIT.