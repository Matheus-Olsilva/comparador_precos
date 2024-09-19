import scrapy

class MercadoLivreSpider(scrapy.Spider):
    name = 'mercado_livre'
 
    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7'
    }
    def __init__(self, produto='', **kwargs):
        super().__init__(**kwargs)
        self.produto = produto
        self.start_urls = [f'https://lista.mercadolivre.com.br/{produto.replace(" ", "-")}']
        self.resultados = []

    def parse(self, response):
        for item in response.css('li.ui-search-layout__item'):
            preco = item.css('span.price-tag-fraction::text').get()
            link = item.css('a.ui-search-link::attr(href)').get()
            if preco and link:
                preco = preco.replace('.', '').replace(',', '.')
                self.resultados.append({
                    'preco': float(preco),
                    'link': link,
                    'site': 'Mercado Livre'
                })

        # Paginação
        next_page = response.css('a.andes-pagination__link.ui-search-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
