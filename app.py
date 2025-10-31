import yfinance as yf
import pandas as pd
import numpy as np

def buscar_dados(ticker, periodo="6mo"):
    try:
        dados = yf.download(ticker, period=periodo, progress=False)
        dados["Retorno"] = dados["Close"].pct_change()
        dados["SMA20"] = dados["Close"].rolling(window=20).mean()
        dados["EMA20"] = dados["Close"].ewm(span=20, adjust=False).mean()
        delta = dados["Close"].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        RS = roll_up / roll_down
        dados["RSI14"] = 100 - (100 / (1 + RS))
        return dados
    except:
        return None

def detectar_assimetria(dados):
    if dados is None or dados.empty:
        return "Erro ao buscar dados"
    media = dados["Retorno"].mean()
    skew = (dados["Retorno"] - media).skew()
    if skew > 0.5:
        return "Tendência de alta (assimetria positiva)"
    elif skew < -0.5:
        return "Tendência de baixa (assimetria negativa)"
    else:
        return "Sem assimetria relevante"

def gerar_alerta(dados):
    if dados is None or dados.empty or pd.isna(dados["RSI14"].iloc[-1]):
        return "Sem dados para alerta"
    rsi = dados["RSI14"].iloc[-1]
    skew = detectar_assimetria(dados)
    if skew == "Tendência de alta (assimetria positiva)" and rsi < 30:
        return "POTENCIAL COMPRA"
    elif skew == "Tendência de baixa (assimetria negativa)" and rsi > 70:
        return "POTENCIAL VENDA"
    else:
        return "Sem sinal relevante"

def analisar_acoes(lista, periodo="6mo"):
    resultados = {}
    for acao in lista:
        dados = buscar_dados(acao, periodo)
        resultado = detectar_assimetria(dados)
        alerta = gerar_alerta(dados)
        resultados[acao] = {"Analise": resultado, "Alerta": alerta, "Dados": dados}
    return resultados
