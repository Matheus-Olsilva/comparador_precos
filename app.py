import streamlit as st
import threading
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy import signals
from twisted.internet import reactor

# Importar os spiders
from spiders.mercado_livre_spider import MercadoLivreSpider
from spiders.kabum_spider import KabumSpider

st.title('Comparador de Preços')

produto = st.text_input('Digite o nome do produto que deseja pesquisar:')

if produto:
    with st.spinner('Buscando informações...'):
        resultados = []

        # Função para coletar itens extraídos pelos spiders
        def crawler_results(item, response, spider):
            resultados.append(item)

        # Conectar o sinal de item_scraped ao coletor de resultados
        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        # Função para rodar o Scrapy em uma thread separada
        def run_crawler():
            runner = CrawlerRunner()
            runner.crawl(MercadoLivreSpider, produto=produto)
            runner.crawl(KabumSpider, produto=produto)
            reactor.run(installSignalHandlers=False)  # Evita conflitos com o reactor

        # Rodar os crawlers em uma thread separada
        threading.Thread(target=run_crawler).start()

        # Esperar até que o crawler finalize
        while reactor.running:
            pass

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
