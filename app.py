import yfinance as yf
import pandas as pd
import numpy as np

def buscar_dados(ticker, periodo="6mo"):
    dados = yf.download(ticker, period=periodo)
    dados["Retorno"] = dados["Close"].pct_change()
    return dados

def detectar_assimetria(dados):
    media = dados["Retorno"].mean()
    desvio = dados["Retorno"].std()
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

if __name__ == "__main__":
    acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"]
    analise = analisar_acoes(acoes)
    for acao, resultado in analise.items():
        print(f"{acao}: {resultado}")
