# versão 1.1 - 30-9-25

import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from api_key import api_key


url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange=NASDAQ&limit=50&apikey={api_key}"
data = requests.get(url).json()
url_nyse = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange=NYSE&limit=50&apikey={api_key}"
data_nyse = requests.get(url_nyse).json()
url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange=NYSE&limit=50&apikey={api_key}"



linhas = []
for acao in data:
    ticker = acao['symbol']
    nome = acao['companyName']
    

    r = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={api_key}")
    ratios = r.json()
    if not ratios: 
        continue
    ratios = ratios[0]  
    

    linhas.append({
        "Papel": ticker,
        "Cotação": acao.get("price"),
        "Div.Yield": acao.get("lastAnnualDividendYield"),
        "ROE": ratios.get("returnOnEquity"),
        "ROIC": ratios.get("returnOnInvestedCapital"),
        "P/L": ratios.get("priceEarningsRatio"),
        "P/VP": ratios.get("priceToBookRatio"),
        "EV/EBIT": ratios.get("enterpriseValueOverEBITDA"),
        "Liquidez": acao.get("volume"),
        "Patrim.Liq": acao.get("marketCap")
    })

linhas_nyse = []
for acao in data_nyse:
    ticker = acao['symbol']
    nome = acao['companyName']
    

    r = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={api_key}")
    ratios = r.json()
    if not ratios: 
        continue
    ratios = ratios[0]  
    

    linhas_nyse.append({
        "Papel": ticker,
        "Cotação": acao.get("price"),
        "Div.Yield": acao.get("lastAnnualDividendYield"),
        "ROE": ratios.get("returnOnEquity"),
        "ROIC": ratios.get("returnOnInvestedCapital"),
        "P/L": ratios.get("priceEarningsRatio"),
        "P/VP": ratios.get("priceToBookRatio"),
        "EV/EBIT": ratios.get("enterpriseValueOverEBITDA"),
        "Liquidez": acao.get("volume"),
        "Patrim.Liq": acao.get("marketCap")
    })

sp500 = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}").json()

linhas_sp500 = []
for acao in sp500:
    ticker = acao['symbol']
    nome = acao['name']  # no sp500_constituent o campo é "name"

    r = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={api_key}")
    ratios = r.json()
    if not ratios:
        continue
    ratios = ratios[0]

    linhas_sp500.append({
        "Papel": ticker,
        "Cotação": None,  # precisa buscar em /quote se quiser a cotação
        "Div.Yield": None, # também vem do /quote
        "ROE": ratios.get("returnOnEquity"),
        "ROIC": ratios.get("returnOnInvestedCapital"),
        "P/L": ratios.get("priceEarningsRatio"),
        "P/VP": ratios.get("priceToBookRatio"),
        "EV/EBIT": ratios.get("enterpriseValueOverEBITDA"),
        "Liquidez": None,  # também em /quote
        "Patrim.Liq": None # marketCap vem de /profile ou /quote
    })



df_nasdaq = pd.DataFrame(linhas)
df_nyse = pd.DataFrame(linhas_nyse)


st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="Fundamentus - Tunado",
)
st.title("Fundamentus - Tunado")
st.subheader("Análise de Ações com a Magic Formula e Metodo Barsi ( VERSÃO BETA )")

ibov = yf.download("^BVSP", period="30d")
sp500 = yf.download("^GSPC", period="30d")
nasdac = yf.download("^QQQ", period="30d")
nyse = yf.download("^NYA", period="30d")
coluna1, coluna2 = st.columns(2)

genre = coluna2.radio("Escolha o índice para análise:", ('Ibovespa', 'S&P 500', 'Nasdaq', 'Nyse'))
if genre == 'Nasdaq':
    df_nasdaq
elif genre == 'Nyse':
    df_nyse
elif genre == 'Ibovespa':
    close = ibov['Close'].dropna()
    nome_indice = "Ibovespa"
    pais = 'brazil'
else:
    close = sp500['Close'].dropna()
    nome_indice = "S&P 500"
    pais = 'united states'

if len(close) >= 2:
    variacao = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100

    if variacao >= 1:
        status = "Alta"
        cor = "normal"
    else:
        status = "Baixa"
        cor = "inverse"

    coluna2.metric(
        label=f"{nome_indice} (30 dias)",
        value=f"{float(close.iloc[-1]):,.0f}",
        delta=f"{variacao:.2f}%",
        delta_color=cor
    )

    coluna2.write(f"O mercado está em **{status}** nos últimos 30 dias.")
else:
    st.warning('Dados insuficientes para calculo!')


if pais == 'brazil':
    try:
        url = "https://www.fundamentus.com.br/resultado.php"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        dfs = pd.read_html(response.text, decimal=',', thousands='.')
        tabela = dfs[0]

        for col in ['ROIC', 'ROE', 'Div.Yield']:
            if col in tabela.columns:
                tabela[col] = (
                    tabela[col]
                    .astype(str)
                    .str.replace('[^0-9\-,\.]', '', regex=True)  # remove caracteres não numéricos
                    .str.replace('.', ',', regex=False)            # troca ponto de milhar por vírgula
                    .str.replace(',', '.', regex=False)           # troca vírgula decimal por ponto
                )
                tabela[col] = pd.to_numeric(tabela[col], errors='coerce')

        st.write("Tabela completa do Fundamentus:")
        st.dataframe(tabela)

        colunas_barsi = [c for c in ['Papel', 'Cota��o', 'Div.Yield', 'ROIC', 'ROE', 'P/L', 'P/VP'] if c in tabela.columns]
        colunas_greenblat = [c for c in ['Papel', 'Cota��o','Div.Yield', 'P/VP', 'ROIC', 'Liquidez', 'Patrim.Liq', 'EV/EBIT'] if c in tabela.columns]

        tabela_barsi = tabela[colunas_barsi]
        tabela_greenblat = tabela[colunas_greenblat]
        tabela_greenblat['Ranking_roic'] =  tabela_greenblat['ROIC'].rank(ascending=True)
        tabela_greenblat['Ranking_ev_ebit'] =  tabela_greenblat['EV/EBIT'].rank(ascending=True) 
        tabela_greenblat['Ranking_total'] = tabela_greenblat['Ranking_roic'] + tabela_greenblat['Ranking_ev_ebit']
        tabela_greenblat['Ranking_total'] = tabela_greenblat['Ranking_total'].rank()

            



        on = coluna2.toggle("Mostrar Tabela Barsi", True)
        if on:
            tabela_barsi_filtrada = tabela_barsi[tabela_barsi['Div.Yield'] > 2]
            coluna1.write("### Tabela Metodo Barsi")
            coluna1.dataframe(tabela_barsi_filtrada)
        else:
            tabela_greenblat_filtrada = tabela_greenblat[tabela_greenblat['Div.Yield'] > 1]
            coluna1.write("### Tabela Metodo Magic Formula")
            coluna1.dataframe(tabela_greenblat_filtrada)
    except Exception as e:
        st.warning(f"Erro ao buscar dados do Fundamentus: {e}")
else:
    st.info("Tabela Fundamentus disponível apenas para ações brasileiras (Ibovespa).")
