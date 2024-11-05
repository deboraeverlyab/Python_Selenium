from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
from datetime import datetime, timedelta
import pandas as pd
import re
from unidecode import unidecode

class Crawler_Local:
    def __init__(self, url):
        self.url = url
        self.service = Service(executable_path="chromedriver.exe")
        self.driver = None

    def iniciar_driver(self):
        try:
            self.driver = webdriver.Chrome(service=self.service)
            self.driver.get(self.url)
            self.driver.maximize_window()
            print("Conexão bem-sucedida. Página carregada com sucesso.")
        except WebDriverException as e:
            print(f"Falha ao carregar a página: {e}")
            print("Cancelando a execução.")
            if self.driver:
                self.driver.quit()

    def crawler(self, palavras):
        data_fim = datetime.today()
        data_inicio = data_fim - timedelta(days=90)
        print('datas: ', data_inicio, data_fim)
        dados = []
        palavras_sem_resultados = []

        for palavra in palavras:
            try:
                print(f"Palavra a ser buscada é: '{palavra}'")
                self._realizar_pesquisa(data_inicio, data_fim, palavra, dados, palavras_sem_resultados)
            except Exception as e:
                print(f"Erro ao realizar pesquisa para '{palavra}': {e}")

            try:
                self.salvar(dados, palavras_sem_resultados)
            except Exception as e:
                print(f"Erro ao salvar resultados: {e}")

    def _realizar_pesquisa(self, data_inicio, data_fim, palavra, dados, palavras_sem_resultados):
        try:
            data_inicio_input = self.driver.find_element(By.ID, "publicationStartDate")
            data_fim_input = self.driver.find_element(By.ID, "publicationEndDate")
            data_inicio_input.clear()
            data_fim_input.clear()
            data_inicio_input.send_keys(data_inicio.strftime('%d/%m/%Y'))
            data_fim_input.send_keys(data_fim.strftime('%d/%m/%Y'))
            self.driver.find_element(By.TAG_NAME, 'body').click()  # Fecha o calendário
        except NoSuchElementException as e:
            print(f"Erro ao configurar as datas para '{palavra}': {e}")
            return

        try:
            descricao_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "description")))
            descricao_input.clear()
            descricao_input.send_keys(palavra)
        except NoSuchElementException as e:
            print(f"Erro ao inserir a palavra '{palavra}' na descrição: {e}")
            return

        try:
            pesquisar_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "PsButton_pesquisar")))
            pesquisar_button.click()
            time.sleep(2)  # Temporário para aguardar a tabela carregar
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Erro ao clicar no botão de pesquisa para '{palavra}': {e}")
            return

        try:
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "procurementsDatatable")))
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Tabela de resultados não encontrada para '{palavra}': {e}")
            return

        while True:
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                row_data = {"termo": palavra}

                try:
                    row_data["central_compras"] = cols[0].text.replace("\n", " ").strip()
                    row_data["processo"] = cols[1].text.replace("\n", " ").strip()
                    row_data["numero"] = cols[2].text.replace("\n", " ").strip()
                    row_data["link"] = cols[2].find_element(By.TAG_NAME, "a").get_attribute("href") if len(cols) > 2 else None
                    row_data["data_publicacao"] = cols[3].text.replace("\n", " ").strip()
                    row_data["modalidade"] = cols[4].text.replace("\n", " ").strip()
                    row_data["descricao"] = cols[5].text.replace("\n", " ").strip()
                    row_data["data_abertura"] = cols[6].text.replace("\n", " ").strip() 

                    if row_data["link"]:
                        self.driver.get(row_data["link"]) 
                        time.sleep(2)  # Espera o conteúdo carregar
                        
                        try:
                            local_text = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//tr[th[contains(text(), 'Local')]]/td"))).text
                            row_data["local"] = local_text.strip()
                        except Exception as e:
                            print(f"Erro ao encontrar a classe 'local': {e}")
                            row_data["local"] = None  

                        # Volta para a página de resultados
                        self.driver.back()

                        # Re-localiza a tabela após a navegação para garantir que o DOM foi atualizado
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "procurementsDatatable")))
                        table = self.driver.find_element(By.ID, "procurementsDatatable")  # Re-localiza a tabela

                except IndexError as e:
                    print(f"Erro ao acessar coluna: {e}")
                    continue  # Continue caso ocorra um erro

                dados.append(row_data)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                next_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next")))
                if "disabled" not in next_button.get_attribute("class"):
                    next_button.click()
                else:
                    break
                time.sleep(2)  # sleep para dar tempo a tabela carregar corretamente
            except (TimeoutException, NoSuchElementException) as e:
                break

    def salvar(self, dados, palavras_sem_resultados):
        try:
            df = pd.DataFrame(dados)
            df["cidade"] = df["local"].apply(lambda x: x.split("-")[-2].strip() if pd.notna(x) else None)
            df["estado"] = df["local"].apply(lambda x: x.split("-")[-1].strip() if pd.notna(x) else None)
            output_csv = 'resultado_pesquisa.csv'
            df.to_csv(output_csv, index=False, encoding="utf-8-sig")
            print("Resultados salvos com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar dados CSV: {e}")

        if palavras_sem_resultados:
            try:
                with open('sem_resultados.txt', 'w', encoding="utf-8-sig") as f:
                    for aviso in palavras_sem_resultados:
                        f.write(aviso + "\n")
                print("Palavras sem resultados salvas com sucesso.")
            except Exception as e:
                print(f"Erro ao salvar palavras sem resultados: {e}")   

    def fechar_driver(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Erro ao fechar o driver: {e}") 
