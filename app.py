from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/sefaz-status', methods=['GET'])
def sefaz_status():
    # Simulação de erro para teste (opcional)
    if request.args.get("teste") == "true":
        return jsonify({
            "subject": "Erro simulado na SEFAZ",
            "body": """
                <html>
                <body>
                    <p style='color:red; font-weight:bold;'>⚠️ Erro simulado para teste. A SEFAZ está indisponível.</p>
                    <table border='1'>
                        <tr><th>Estado</th><th>Status</th></tr>
                        <tr><td>SP</td><td>Indisponível</td></tr>
                    </table>
                </body>
                </html>
            """
        }), 500

    url = "https://www.nfe.fazenda.gov.br/portal/disponibilidade.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({
            "subject": "Erro ao acessar SEFAZ",
            "body": f"""
                <html>
                <body>
                    <p style='color:red;'>Não foi possível acessar o site da SEFAZ. Erro: {e}</p>
                </body>
                </html>
            """
        }), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_gdvDisponibilidade2"})

    table_data = []
    status = 'OK'

    for tr in table.find_all('tr'):
        new_row = []
        for content in tr.contents:
            output = '-'
            if content.text.strip():
                output = content.text.strip()
            else:
                try:
                    img = content.find("img")['src']
                    if 'verde' in img:
                        output = 'OK'
                    elif 'amarel' in img:
                        output = 'Warning'
                        if status != 'Error':
                            status = 'Warning'
                    elif 'vermelh' in img:
                        output = 'Error'
                        status = 'Error'
                    else: 
                        output = 'Cannot read info'
                        status = 'Warning'
                except:
                    output = 'Cannot read info'
                    status = 'Warning'
            new_row.append(output)
        table_data.append(new_row)

    if status == 'OK':
        return jsonify({})  # Não envia nada se estiver OK
    elif status == "Error":
        mensagem_alerta = "<p style='color:red; font-weight:bold;'>⚠️ Atenção: Um ou mais serviços da SEFAZ estão com erro.</p>"
    else:
        mensagem_alerta = "<p style='color:orange; font-weight:bold;'>⚠️ Aviso: Alguns serviços da SEFAZ estão com instabilidade.</p>"


    html = f"{mensagem_alerta}<table style='border-collapse: collapse' border='1'>\n<tr>"
    for header in table_data[0]:
        html += f"<th>{header}</th>"
    html += "</tr>\n"

    for row in table_data[1:]:
        html += "<tr>\n"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>\n"
    html += "</table>"

    return jsonify({
        "subject": f"Status SEFAZ: {status}",
        "body": f"<html><body>{html}</body></html>"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
