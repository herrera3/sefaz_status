from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os


app = Flask(__name__)

@app.route('/sefaz-status', methods=['GET'])
def sefaz_status():
    url = "https://www.nfe.fazenda.gov.br/portal/isponibilidade.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({
            "subject": "Erro ao acessar SEFAZ",
            "body": f"<p>Não foi possível acessar o site da SEFAZ. Erro: {e}</p>"
        })

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
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
    if status == "Error":
        mensagem_alerta = "<p style='color:red; font-weight:bold;'>⚠️ Atenção: Um ou mais serviços da SEFAZ estão com erro.</p>"
    elif status == "Warning":
        mensagem_alerta = "<p style='color:orange; font-weight:bold;'>⚠️ Aviso: Alguns serviços da SEFAZ estão com instabilidade.</p>"

    html = f"Status SEFAZ:<br>{mensagem_alerta}<table style='border-collapse: collapse'>\n<tr>"
    for header in table_data[0]:
        html += f"<th style='border: 1px solid black;'>{header}</th>"
    html += "</tr>\n"

    for row in table_data[1:]:
        html += "<tr>\n"
        for cell in row:
            html += f"<td style='border: 1px solid black;'>{cell}</td>"
        html += "</tr>\n"
    html += "</table>"

    return jsonify({
        "subject": f"Status SEFAZ: {status}",
        "body": html
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




