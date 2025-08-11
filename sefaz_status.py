import requests
from bs4 import BeautifulSoup

url = "https://www.nfe.fazenda.gov.br/portal/disponibilidade.aspx"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    html_content = response.content
except requests.exceptions.RequestException as e:
    print("###SUBJECT###")
    print("Erro ao acessar SEFAZ")
    print("###BODY###")
    print(f"<p>Não foi possível acessar o site da SEFAZ. Erro: {e}</p>")
    exit()

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

# Se status for OK, não envia e-mail
if status == 'OK':
    print("###SUBJECT###")
    print("Status SEFAZ: OK")
    print("###BODY###")
    print("Todos os serviços da SEFAZ estão operando normalmente.")
    exit()

# Mensagem de alerta
mensagem_alerta = ""
if status == "Error":
    mensagem_alerta = "<p style='color:red; font-weight:bold;'>⚠️ Atenção: Um ou mais serviços da SEFAZ estão com erro.</p>"
elif status == "Warning":
    mensagem_alerta = "<p style='color:orange; font-weight:bold;'>⚠️ Aviso: Alguns serviços da SEFAZ estão com instabilidade.</p>"

# Monta HTML da tabela
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

# Título do e-mail
title_email = f"Status SEFAZ: {status}"

# Saída para Power Automate Desktop

print(title_email)
print(html)
