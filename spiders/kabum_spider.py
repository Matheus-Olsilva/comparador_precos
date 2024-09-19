import scrapy

class KabumSpider(scrapy.Spider):
    name = 'kabum'

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }

    def __init__(self, produto='', **kwargs):
        super().__init__(**kwargs)
        self.produto = produto
        self.start_urls = [f'https://www.kabum.com.br/busca/{produto.replace(" ", "%20")}']
        self.resultados = []

    def parse(self, response):
        for item in response.css('div.productCard'):
            preco = item.css('span.priceCard::text').get()
            link = item.css('a::attr(href)').get()
            if preco and link:
                preco = preco.strip().replace('R$', '').replace('.', '').replace(',', '.')
                self.resultados.append({
                    'preco': float(preco),
                    'link': response.urljoin(link),
                    'site': 'Kabum'
                })

        # Paginação
        next_page = response.css('a#listingPaginateNext::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
