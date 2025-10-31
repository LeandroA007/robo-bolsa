from flask import Flask, render_template_string, request
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
    <h1>Robô de Análise de Ações</h1>
    <form method="post">
        <label>Digite os códigos das ações (separados por vírgula):</label><br>
        <input type="text" name="acoes" size="50" placeholder="Ex: PETR4.SA,VALE3.SA,ITUB4.SA">
        <input type="submit" value="Analisar">
    </form>
    {% if analise %}
    <h2>Resultados:</h2>
    <table border="1" cellpadding="8">
        <tr><th>Ação</th><th>Análise</th></tr>
        {% for acao, resultado in analise.items() %}
        <tr><td>{{acao}}</td><td>{{resultado}}</td></tr>
        {% endfor %}
    </table>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    analise = None
    if request.method == "POST":
        entrada = request.form.get("acoes")
        if entrada:
            lista_acoes = [a.strip() for a in entrada.split(",") if a.strip()]
            analise = analisar_acoes(lista_acoes)
    return render_template_string(HTML, analise=analise)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
