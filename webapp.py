from flask import Flask, render_template_string, request, send_file
from app import analisar_acoes, exportar_csv

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Robô de Análise da Bolsa</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        // Atualiza automaticamente a página a cada 5 minutos
        setTimeout(function(){
           document.getElementById('formulario').submit();
        }, 300000);
    </script>
</head>
<body>
    <h1>Robô de Análise de Ações - Atualização Automática</h1>
    <form method="post" id="formulario">
        <label>Digite os códigos das ações (separados por vírgula):</label><br>
        <input type="text" name="acoes" size="50" placeholder="Ex: PETR4.SA,VALE3.SA"
               value="{{ entrada if entrada else '' }}">
        <label>Período histórico:</label>
        <select name="periodo">
            <option value="1mo" {% if periodo=="1mo" %}selected{% endif %}>1 mês</option>
            <option value="3mo" {% if periodo=="3mo" %}selected{% endif %}>3 meses</option>
            <option value="6mo" {% if periodo=="6mo" %}selected{% endif %}>6 meses</option>
            <option value="1y" {% if periodo=="1y" %}selected{% endif %}>1 ano</option>
        </select>
        <input type="submit" value="Analisar">
    </form>

    {% if analise %}
    <h2>Resultados:</h2>
    <table border="1" cellpadding="8">
        <tr><th>Ação</th><th>Análise</th><th>Alerta</th></tr>
        {% for acao, info in analise.items() %}
        <tr style="color:{% if info['Alerta']=='POTENCIAL COMPRA' %}green{% elif info['Alerta']=='POTENCIAL VENDA' %}red{% else %}black{% endif %}">
            <td>{{acao}}</td>
            <td>{{info['Analise']}}</td>
            <td>{{info['Alerta']}}</td>
        </tr>
        {% endfor %}
    </table>
    <a href="/exportar">Exportar resultados para CSV</a>

    <h2>Gráficos:</h2>
    {% for acao, info in analise.items() %}
        <h3>{{acao}}</h3>
        <div id="grafico_{{acao}}" style="height:500px;"></div>
        <script>
            var trace1 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['Close'].tolist()}}, mode: 'lines', name: 'Fechamento' };
            var trace2 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['SMA20'].tolist()}}, mode: 'lines', name: 'SMA20' };
            var trace3 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['EMA20'].tolist()}}, mode: 'lines', name: 'EMA20' };
            var trace4 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['RSI14'].tolist()}}, mode: 'lines', name: 'RSI14', yaxis: 'y2' };
            var trace5 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['MACD'].tolist()}}, mode: 'lines', name: 'MACD', yaxis: 'y3' };
            var trace6 = { x: {{info['Dados'].index.tolist()}}, y: {{info['Dados']['Signal'].tolist()}}, mode: 'lines', name: 'Signal', yaxis: 'y3' };
            
            var layout = {
                yaxis: {title: 'Preço'},
                yaxis2: {title: 'RSI', overlaying: 'y', side: 'right'},
                yaxis3: {title: 'MACD', overlaying: 'y', side: 'left', position: 0.95},
                height: 500,
                margin: { t: 50 }
            };
            var data = [trace1, trace2, trace3, trace4, trace5, trace6];
            Plotly.newPlot('grafico_{{acao}}', data, layout, {responsive:true});
        </script>
    {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    analise = None
    entrada = ""
    periodo = "6mo"
    if request.method == "POST":
        entrada = request.form.get("acoes")
        periodo = request.form.get("periodo") or "6mo"
        if entrada:
            lista_acoes = [a.strip() for a in entrada.split(",") if a.strip()]
            analise = analisar_acoes(lista_acoes, periodo)
    return render_template_string(HTML, analise=analise, entrada=entrada, periodo=periodo)

@app.route("/exportar")
def exportar():
    if 'analise' in globals():
        arquivo = exportar_csv(globals()['analise'])
        if arquivo:
            return send_file(arquivo, as_attachment=True)
    return "Nenhum resultado para exportar"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
