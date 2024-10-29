from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time
from datetime import datetime, timedelta
import pandas as pd

class Crawler:
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
        dados = []
        palavras_sem_resultados = []

        for palavra in palavras:
            self._realizar_pesquisa(data_inicio, data_fim, palavra, dados, palavras_sem_resultados)

        self.salvar(dados, palavras_sem_resultados)

    def _realizar_pesquisa(self, data_inicio, data_fim, palavra, dados, palavras_sem_resultados):
        data_inicio_input = self.driver.find_element(By.ID, "publicationStartDate")
        data_fim_input = self.driver.find_element(By.ID, "publicationEndDate")
        data_inicio_input.clear()
        data_fim_input.clear()
        data_inicio_input.send_keys(data_inicio.strftime('%d/%m/%Y'))
        data_fim_input.send_keys(data_fim.strftime('%d/%m/%Y'))
        self.driver.find_element(By.TAG_NAME, 'body').click()  # Fecha o calendário

        descricao_input = self.driver.find_element(By.ID, "description")
        descricao_input.clear()
        descricao_input.send_keys(palavra)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "PsButton_pesquisar")))
        self.driver.find_element(By.ID, "PsButton_pesquisar").click()

        time.sleep(2) # sleep para dar tempo a tabela carregar corretamente

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "procurementsDatatable")))
        table = self.driver.find_element(By.ID, "procurementsDatatable")

        # Verifica se a tabela contém apenas uma linha com a mensagem de "sem resultados"
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        if len(rows) == 1:
            single_cell = rows[0].find_elements(By.TAG_NAME, "td")
            if len(single_cell) == 1 and "Não há editais" in single_cell[0].text:
                aviso = f"Sem resultados para a palavra: {palavra}"
                print(aviso)
                palavras_sem_resultados.append(aviso)
                return

        header = [th.text for th in table.find_elements(By.XPATH, ".//thead/tr/th")]

        while True:
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                row_data = {"Palavra": palavra}

                for i in range(len(header)):
                    if header[i] == "Edital":
                        try:
                            link_element = cols[i].find_element(By.TAG_NAME, "a")
                            row_data["Link Edital"] = link_element.get_attribute("href")
                        except:
                            row_data["Link Edital"] = None

                    row_data[header[i]] = cols[i].text

                dados.append(row_data)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                next_button = self.driver.find_element(By.CLASS_NAME, "next")
                if "disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(2)
            except Exception as e:
                break

    def salvar(self, dados, palavras_sem_resultados):
        df = pd.DataFrame(dados)
        output_csv = 'resultado_pesquisa.csv'
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")

        if palavras_sem_resultados:
            with open('sem_resultados.txt', 'w', encoding="utf-8-sig") as f:
                for aviso in palavras_sem_resultados:
                    f.write(aviso + "\n")

    def fechar_driver(self):
        if self.driver:
            self.driver.quit()
