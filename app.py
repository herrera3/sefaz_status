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
                    elif 'amarelo' in img:
                        output = 'Warning'
                        if status != 'Error':
                            status = 'Warning'
                    elif 'vermelho' in img:
                        output = 'Error'
                        status = 'Error'
                except:
                    pass
            new_row.append(output)
        table_data.append(new_row)

    if status == 'OK':
        return jsonify({})  # Não envia nada se estiver OK

    mensagem_alerta = ""
