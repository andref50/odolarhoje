import os
import requests
import datetime
from atproto import Client
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler


def principal():
    data_hoje = datetime.date.fromordinal(datetime.date.today().toordinal())
    data_hoje = data_hoje.strftime('%d/%m/%Y')

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
        text1 = f'🗓️ {data_hoje} \n\n'
        text1 += f'💵 O dólar fechou em R${valor_dolar}\n'
        text1 += '📈 Alta' if variacao > 0 else '📉 Baixa'
        text1 += f' de {variacao:.2f}% em relação ao dia anterior\n\n'
        text1 += '#cotacao #dolar'
        print(text1)
        post = client.send_post(text1)

    else:
        print(f'Erro ao obter o valor do dólar: {resposta.status_code}')

def rebluite():
    load_dotenv()
    
    email = os.getenv('EMAIL')
    senha = os.getenv('SENHA')

    client = Client()
    profile = client.login(email, senha)

    response = client.app.bsky.feed.get_author_feed(params={'actor': 'odolarhoje.bsky.social', 'limit': 1, 'filter': 'posts_no_replies'})
    latest_post = response.feed[0].post

    client.repost(latest_post.uri, latest_post.cid)
    print('Post rebluitado:', latest_post.uri)


if __name__ == "__main__":

    scheduler = BlockingScheduler()
    scheduler.add_job(principal, 'cron', hour=21, minute=45)
    scheduler.add_job(rebluite, 'cron', hour=12, minute=0)
    scheduler.start()

