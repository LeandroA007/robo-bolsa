import yfinance as yf
import pandas as pd
import numpy as np

def buscar_dados(ticker, periodo="6mo"):
    try:
        dados = yf.download(ticker, period=periodo, progress=False)
        dados["Retorno"] = dados["Close"].pct_change()
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

def analisar_acoes(lista):
    resultados = {}
    for acao in lista:
        dados = buscar_dados(acao)
        resultado = detectar_assimetria(dados)
        resultados[acao] = resultado
    return resultados
