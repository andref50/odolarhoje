import os
import requests
from atproto import Client
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler


def main():
    load_dotenv()
    
    email = os.getenv('EMAIL')
    senha = os.getenv('SENHA')

    api_url = 'https://br.dolarapi.com/v1/cotacoes/usd'
    resposta = requests.get(api_url)
    
    client = Client()
    profile = client.login(email, senha)
    print('Welcome,', profile.handle)

    if resposta.status_code == 200:
        dados = resposta.json()
        variacao = (dados['compra'] - dados['fechoAnterior']) / dados['fechoAnterior'] * 100
        valor_dolar = str(dados['compra']).replace('.', ',')[:-2]
        text1 = f'O dólar 💵 fechou em R${valor_dolar}.\n'
        text1 += '📈 Alta' if variacao > 0 else '📉 Baixa'
        text1 += f' de {variacao:.2f}% em relação à ontem.\n\n'
        text1 += '#cotacao #dolar'
        print(text1)
        post = client.send_post(text1)

    else:
        print(f'Erro ao obter o valor do dólar: {resposta.status_code}')


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # scheduler.add_job(main, 'cron', hour=22, minute=50)
    scheduler.add_job(main, 'interval', minutes=1)
    scheduler.start()
