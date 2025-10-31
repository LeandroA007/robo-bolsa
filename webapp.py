from flask import Flask, render_template_string, request, send_file
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

# ==================== FUNÇÕES ====================
def calcular_indicadores(df):
    if df.empty:
        return df
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df['RSI14'] = 100 - (100 / (1 + rs))
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

def analisar_acoes(lista_acoes, periodo="6mo"):
    resultados = {}
    for acao in lista_acoes:
        try:
            df = yf.download(acao, period=periodo)
            if df.empty:
                resultados[acao] = {"Analise": "Ticker inválido ou sem dados", "Alerta":"N/A", "Dados":pd.DataFrame()}
                continue
            df = calcular_indicadores(df)
            # Alerta simples: preço acima ou abaixo da SMA20
            ultimo_preco = df['Close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1] if not df['SMA20'].isnull().all() else ultimo_preco
            if ultimo_preco > sma20:
                alerta = "POTENCIAL VENDA"
            elif ultimo_preco < sma20:
                alerta = "POTENCIAL COMPRA"
            else:
                alerta = "NEUTRO"
            resultados[acao] = {"Analise": f"Preço: {ultimo_preco:.2f}, SMA20: {sma20:.2f}", "Alerta": alerta, "Dados": df}
        except Exception as e:
            resultados[acao] = {"Analise": f"Erro ao processar: {str(e)}", "Alerta":"N/A", "Dados":pd.DataFrame()}
    return resultados

def exportar_csv(analise):
    try:
        dfs=[]
        for acao, info in analise.items():
            if not info['Dados'].empty:
                temp = info['Dados'].copy()
                temp['Ação'] = acao
                dfs.append(temp)
        if dfs:
            resultado = pd.concat(dfs)
            arquivo = "analise_acoes.csv"
            resultado.to_csv(arquivo)
            return arquivo
        return None
    except:
        return None

# ==================== TEMPLATE HTML ====================
HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Dashboard de Ações Profissional</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
body { margin:0; font-family: Arial, sans-serif; background-color:#1e1e2f; color:#f0f0f0; }
.sidebar { position: fixed; top:0; left:0; width: 320px; height:100%; background-color:#2a2a40; padding:20px; box-shadow:2px 0 5px rgba(0,0,0,0.5); overflow-y:auto; }
.main { margin-left:340px; padding:20px; display:grid; grid-template-columns: repeat(auto-fill, minmax(400px,1fr)); gap:20px; }
h1,h2,h3 { color:#f0f0f0; }
input, select { width:100%; padding:5px; margin:5px 0; border-radius:5px; border:none; }
input[type="submit"] { background-color:#4CAF50; color:white; cursor:pointer; }
input[type="submit"]:hover { background-color:#45a049; }
.card { background-color:#2a2a40; border-radius:10px; padding:15px; box-shadow:0 2px 5px rgba(0,0,0,0.5); }
.alert-compra { color:#00FF00; font-weight:bold; }
.alert-venda { color:#FF5555; font-weight:bold; }
.alert-neutro { color:#FFD700; font-weight:bold; }
</style>
<script>
    setTimeout(function(){ document.getElementById('formulario').submit(); }, 300000);
</script>
</head>
<body>
<div class="sidebar">
<h1>Configurações</h1>
<form method="post" id="formulario">
<label>Ações (vírgula separadas):</label>
<input type="text" name="acoes" placeholder="Ex: PETR4.SA,VALE3.SA" value="{{entrada if entrada else ''}}">

<label>Período histórico:</label>
<select name="periodo">
    <option value="1mo" {% if periodo=="1mo" %}selected{% endif %}>1 mês</option>
    <option value="3mo" {% if periodo=="3mo" %}selected{% endif %}>3 meses</option>
    <option value="6mo" {% if periodo=="6mo" %}selected{% endif %}>6 meses</option>
    <option value="1y" {% if periodo=="1y" %}selected{% endif %}>1 ano</option>
</select>

<label>Indicadores:</label>
<input type="checkbox" name="indicadores" value="SMA" {% if 'SMA' in indicadores %}checked{% endif %}> SMA20<br>
<input type="checkbox" name="indicadores" value="EMA" {% if 'EMA' in indicadores %}checked{% endif %}> EMA20<br>
<input type="checkbox" name="indicadores" value="RSI" {% if 'RSI' in indicadores %}checked{% endif %}> RSI14<br>
<input type="checkbox" name="indicadores" value="MACD" {% if 'MACD' in indicadores %}checked{% endif %}> MACD<br>

<input type="submit" value="Analisar">
</form>
<a href="/exportar">Exportar CSV</a>
</div>

<div class="main">
{% if analise %}
    {% for acao, info in analise.items() %}
    <div class="card">
        <h3>{{acao}}</h3>
        <p><strong>Alerta:</strong> <span class="{% if info['Alerta']=='POTENCIAL COMPRA' %}alert-compra{% elif info['Alerta']=='POTENCIAL VENDA' %}alert-venda{% else %}alert-neutro{% endif %}">{{info['Alerta']}}</span></p>
        <p>{{info['Analise']}}</p>
        {% if not info['Dados'].empty %}
        <div id="grafico_{{acao}}" style="height:300px;"></div>
        <script>
            var data=[];
            data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['Close'].tolist()}}, mode:'lines', name:'Fechamento', line:{color:'#00BFFF'}});
            {% if 'SMA' in indicadores %} data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['SMA20'].tolist()}}, mode:'lines', name:'SMA20', line:{color:'#FFD700'}}); {% endif %}
            {% if 'EMA' in indicadores %} data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['EMA20'].tolist()}}, mode:'lines', name:'EMA20', line:{color:'#FF69B4'}}); {% endif %}
            {% if 'RSI' in indicadores %} data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['RSI14'].tolist()}}, mode:'lines', name:'RSI14', yaxis:'y2', line:{color:'#7FFF00'}}); {% endif %}
            {% if 'MACD' in indicadores %} 
            data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['MACD'].tolist()}}, mode:'lines', name:'MACD', yaxis:'y3', line:{color:'#FF4500'}});
            data.push({x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['Signal'].tolist()}}, mode:'lines', name:'Signal', yaxis:'y3', line:{color:'#1E90FF'}});
            {% endif %}
            var layout={paper_bgcolor:'#1e1e2f', plot_bgcolor:'#1e1e2f', font:{color:'#f0f0f0'},
                        yaxis:{title:'Preço'}, yaxis2:{title:'RSI', overlaying:'y', side:'right'},
                        yaxis3:{title:'MACD', overlaying:'y', side:'left', position:0.95}, height:300, margin:{t:30}};
            Plotly.newPlot('grafico_{{acao}}', data, layout, {responsive:true});
        </script>
        {% endif %}
    </div>
    {% endfor %}
{% endif %}
</div>
</body>
</html>
"""

# ==================== ROTAS ====================
@app.route("/", methods=["GET","POST"])
def home():
    analise=None
    entrada=""
    periodo="6mo"
    indicadores=[]
    if request.method=="POST":
        entrada=request.form.get("acoes")
        periodo=request.form.get("periodo") or "6mo"
        indicadores=request.form.getlist("indicadores") or ["SMA","EMA","RSI","MACD"]
        if entrada:
            lista_acoes=[a.strip() for a in entrada.split(",") if a.strip()]
            analise=analisar_acoes(lista_acoes, periodo)
    return render_template_string(HTML, analise=analise, entrada=entrada, periodo=periodo, indicadores=indicadores)

@app.route("/exportar")
def exportar():
    if 'analise' in globals():
        arquivo=exportar_csv(globals()['analise'])
        if arquivo: return send_file(arquivo, as_attachment=True)
    return "Nenhum resultado para exportar"

# ==================== MAIN ====================
if __name__=="__main__":
    app.run(host="0.0.0.0", port=3000)
