import os
import requests
import datetime
import logging
from atproto import Client, client_utils
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler


logger = logging.getLogger()
logging.basicConfig(filename='main.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger.info('Starting the application...')

api_url = 'https://br.dolarapi.com/v1/cotacoes/usd'


def principal():
    data_hoje = datetime.date.today().strftime('%d/%m/%Y')
    resposta = requests.get(api_url)

    text_builder = client_utils.TextBuilder()

    if resposta.status_code == 200:
        dados = resposta.json()
        
        valor_dolar = f'{dados["compra"]:.2f}'.replace('.', ',')
        variacao = (dados["compra"] - dados["fechoAnterior"]) / dados["fechoAnterior"] * 100

        text1 = f'🗓️ {data_hoje} \n\n'
        text1 += f'💵 O dólar fechou em R${valor_dolar}\n'
        text1 += '📈 Alta ' if variacao > 0 else '📉 Baixa '
        text1 += 'de ' + f'{variacao:.2f}'.replace('.', ',') + '% em relação ao dia anterior\n\n'

        text_builder.text(text1)
        text_builder.tag('#cotacao ', 'cotacao')
        text_builder.tag('#dolar', 'dolar')   

        post = client.send_post(text_builder)
        logger.info('Post enviado: ' + post.uri)

        print(text1)
    else:
        print(f'Erro ao obter o valor do dólar: {resposta.status_code}')

def rebluite():
    response = client.app.bsky.feed.get_author_feed(params={'actor': 'odolarhoje.bsky.social', 'limit': 1, 'filter': 'posts_no_replies'})
    
    if response.feed:
        latest_post = response.feed[0].post
        client.repost(latest_post.uri, latest_post.cid)
        logger.info('Post rebluitado: ' + latest_post.uri)
        print('Post rebluitado:', latest_post.uri)
    else:
        print('Nenhum post encontrado para rebluitar.')


if __name__ == "__main__":
    load_dotenv()
    
    email = os.getenv('EMAIL')
    senha = os.getenv('SENHA')

    try:
        client = Client()
        profile = client.login(email, senha)

        logger.info('Login successful: ' + profile.handle)
        print('Bem-vindo,', profile.handle)
    except Exception as e:
        logger.error('Login failed: ' + str(e))
        print('Login failed: ', str(e))
        exit(1)


    scheduler = BlockingScheduler()
    scheduler.add_job(principal, 'cron', hour=18, minute=45, day_of_week='mon-fri', timezone='America/Sao_Paulo')
    scheduler.add_job(rebluite, 'cron', hour=10, day_of_week='tue-fri', timezone='America/Sao_Paulo')

    scheduler.start()

