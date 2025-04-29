from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time

# Configurar o driver do Selenium (exemplo com Chrome)
driver = webdriver.Chrome()  # Certifique-se de que o chromedriver está no PATH
driver.get("URL_DA_PAGINA")  # Substitua pela URL da página que contém a tabela

try:
    # Esperar até que o wrapper da tabela esteja visível
    wait = WebDriverWait(driver, 10)
    wrapper = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inbox-messaging__wrapper")))

    # Localizar todos os elementos que correspondem ao padrão desejado
    notification_items = wrapper.find_elements(By.CLASS_NAME, "notification__item")

    for item in notification_items:
        try:
            # Re-localizar o elemento para evitar StaleElementReferenceException
            talk_id_element = item.find_element(By.CLASS_NAME, "notification-inner__title_message_talk-id")
            talk_id = talk_id_element.text

            print(f"Talk ID: {talk_id}")
        except StaleElementReferenceException:
            print("Elemento não encontrado ou atualizado no DOM.")

finally:
    # Fechar o navegador
    driver.quit()