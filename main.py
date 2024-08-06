import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de e-mail
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')

# Acessar variáveis de ambiente
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
URL = os.getenv('URL')
PROXY_URL = os.getenv('PROXY_URL')
KEY = os.getenv('KEY')


def check_teams_status():
    url = PROXY_URL

    querystring = {"url": URL, "proxy_country": "BR", "response_format": "html"}

    headers = {
        "x-rapidapi-key": KEY,
        "x-rapidapi-host": "scrapingant.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response.status_code)
    if response.status_code == 200:
        # Verifica se a página contém uma mensagem indicando problemas no serviço
        if "User reports indicate problems at Teams" in response.text:
            return False
    return True


def send_email_alert():
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = EMAIL_SUBJECT

    body = f"Microsoft Teams está passando por instabilidades. Por favor, verifique o status do serviço.\n\n{URL}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()
        print("e-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")


def main():
    while True:
        # Obter a hora atual
        now = datetime.now()

        if now.hour >= 19 or now.hour < 7:

            target_date = datetime(now.year, now.month, now.day)
            if now.hour <= 23:
                # Definir a hora de destino como 7 da manhã do dia seguinte
                target_date = target_date + timedelta(days=1)

            target_date = target_date.replace(hour=7, minute=0, second=0, microsecond=0)
            time_left = target_date - now

            time.sleep(time_left.total_seconds())

        if not check_teams_status():
            send_email_alert()
        else:
            print("Microsoft Teams está funcionando normalmente.")
        time.sleep(2700)  # Verifica a cada 45 minutos


if __name__ == "__main__":
    main()
