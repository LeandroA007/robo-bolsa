from flask import Flask, render_template_string
from app import analisar_acoes

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Robô de Análise da Bolsa</title>
</head>
<body>
    <h1>Relatório de Assimetria - Bolsa de Valores</h1>
    <table border="1" cellpadding="8">
        <tr><th>Ação</th><th>Análise</th></tr>
        {% for acao, resultado in analise.items() %}
        <tr><td>{{acao}}</td><td>{{resultado}}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def home():
    acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"]
    analise = analisar_acoes(acoes)
    return render_template_string(HTML, analise=analise)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
