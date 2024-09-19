import streamlit as st
import asyncio
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.signalmanager import dispatcher
from scrapy import signals

# Import your spiders
from spiders.mercado_livre_spider import MercadoLivreSpider
from spiders.kabum_spider import KabumSpider

from twisted.internet import asyncioreactor

# Install the Twisted asyncio reactor
try:
    asyncioreactor.install()
except Exception:
    pass

st.title('Comparador de Preços')

produto = st.text_input('Digite o nome do produto que deseja pesquisar:')

if produto:
    with st.spinner('Buscando informações...'):
        resultados = []

        # Function to collect scraped items
        def crawler_results(item, response, spider):
            resultados.append(item)

        # Connect the item_scraped signal
        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        # Async function to run spiders
        async def run_spiders():
            runner = CrawlerRunner()
            await runner.crawl(MercadoLivreSpider, produto=produto)
            await runner.crawl(KabumSpider, produto=produto)
        
        # Run the spiders
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_spiders())

        # Process the results
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
