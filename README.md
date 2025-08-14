# SEFAZ Status API

This project is a Flask API that checks the status of SEFAZ (Secretaria da Fazenda) services and returns a formatted HTML table with the results. The API is ideal for integration with Power Automate Cloud, allowing automatic email notifications in case of errors or service instability.

---

## ⚙️ Features

- Automatic query of SEFAZ availability page.
- Interpretation of status icons (green, yellow, red).
- JSON response with:
  - `subject`: email subject.
  - `body`: HTML content with alert and formatted table.
- Error simulation support via `?teste=true` parameter.

---

## 🔗 Integration with Power Automate

- Configure a scheduled flow every 5 minutes.
- Use the HTTP action to call the API.
- Add a condition: `@not(empty(body('HTTP')['body']))`
- If true, send an email with:
  - Subject: `@body('HTTP')['subject']`
  - Body: `@body('HTTP')['body']` (mark as HTML)

---

## 📦 Deployment on Render

- Service type: Web Service
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Port: Render uses the `PORT` environment variable, already handled in the code.

---

## 🧪 Simulated Error Test

To test email sending with an error, access:
https://your-api-on-render.com/sefaz-status?teste=true

## 🧑‍💻 Authors

Maria Eduarda Herrera dos Santos  
Thalita Silva  
Jr. Associate Support Engineer II
