from crawler import Crawler

def main():
    url = "https://www.compras.rs.gov.br/editais/pesquisar"

    palavras = ['Professor', 'palavra', 'escola']
    
    crawler = Crawler(url)
    crawler.iniciar_driver()
    crawler.crawler(palavras)
    crawler.fechar_driver()

if __name__ == "__main__":
    main()
