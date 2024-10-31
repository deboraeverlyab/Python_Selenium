from crawler import Crawler
from crawler_local import Crawler_Local
from googledriveuploader import GoogleDriveUploader 

def main():
    url = "https://www.compras.rs.gov.br/editais/pesquisar"

    palavras = ['Professor', 'palavra', 'escola']
    
    crawler = Crawler(url)
    crawler.iniciar_driver()
    crawler.crawler(palavras)
    crawler.fechar_driver()
    
    '''
    # crawler com Local
    crawler_local = Crawler_Local(url)
    crawler_local.iniciar_driver()
    crawler_local.crawler(palavras)
    crawler_local.fechar_driver()'''

    # compartilhando no drive
    '''# Configurações para o upload do Google Drive
    credentials_path = "pythonselenium-440223-152f243ca4a9.json"  
    drive_folder_id = "1C69yH9rBdE5x-M6ny9QPDGSwz2odryRd"     
    file_path = "resultado_pesquisa.csv"                

    # Instancia o uploader e faz o upload do arquivo
    uploader = GoogleDriveUploader(credentials_path, drive_folder_id)
    uploader.upload_file(file_path, file_name="resultado_final.csv")'''

if __name__ == "__main__":
    main()
