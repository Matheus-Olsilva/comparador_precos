import streamlit as st
import nest_asyncio
import asyncio
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy import signals

import pandas as pd

# Importar os spiders
from spiders.mercado_livre_spider import MercadoLivreSpider
from spiders.kabum_spider import KabumSpider
# Importe aqui os outros spiders

# Configurar o loop de eventos
nest_asyncio.apply()
loop = asyncio.get_event_loop()

st.title('Comparador de Preços')

produto = st.text_input('Digite o nome do produto que deseja pesquisar:')

if produto:
    with st.spinner('Buscando informações...'):
        resultados = []

        # Função para coletar itens extraídos pelos spiders
        def crawler_results(item, response, spider):
            resultados.append(item)

        # Conectar o sinal de item_passed ao coletor de resultados
        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        # Função assíncrona para executar os spiders
        async def crawl():
            runner = CrawlerRunner()
            # Executar os spiders
            await runner.crawl(MercadoLivreSpider, produto=produto)
            await runner.crawl(KabumSpider, produto=produto)
            # Adicione aqui os outros spiders

        loop.run_until_complete(crawl())

        # Processar os resultados
        if resultados:
            df = pd.DataFrame(resultados)
            preco_medio = df['preco'].mean()
            preco_minimo = df['preco'].min()
            indices_minimos = df[df['preco'] == preco_minimo].index
            links_minimos = df.loc[indices_minimos, ['link', 'site']]

            st.write(f'**Preço médio:** R$ {preco_medio:.2f}')
            st.write(f'**Preço mínimo:** R$ {preco_minimo:.2f}')
            st.write('**Links para o menor preço:**')
            for idx, row in links_minimos.iterrows():
                st.write(f'- [{row["site"]}]({row["link"]})')
        else:
            st.write('Nenhum produto encontrado.')
