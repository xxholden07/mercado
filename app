# main.py
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Configurar navegador headless
def iniciar_navegador():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def buscar_e_adicionar_item(driver, produto):
    try:
        driver.get("https://www.tendaatacado.com.br/")
        time.sleep(3)

        barra_pesquisa = driver.find_element(By.NAME, "q")
        barra_pesquisa.clear()
        barra_pesquisa.send_keys(produto)
        barra_pesquisa.send_keys(Keys.RETURN)
        time.sleep(5)

        primeiro_produto = driver.find_element(By.CSS_SELECTOR, "a.product-item-photo")
        primeiro_produto.click()
        time.sleep(5)

        botao_comprar = driver.find_element(By.ID, "product-addtocart-button")
        botao_comprar.click()
        time.sleep(3)
        return True

    except Exception as e:
        st.error(f"Erro ao adicionar '{produto}': {e}")
        return False

def main():
    st.title("🛒 Carrinho Automático - Tenda Atacado")

    uploaded_file = st.file_uploader("Envie sua planilha de compras (.xlsx):", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Itens encontrados:", df)

        if st.button("Iniciar processo de compra"):
            with st.spinner("Abrindo navegador..."):
                driver = iniciar_navegador()

            for produto in df['Produto']:
                with st.spinner(f"Adicionando: {produto}"):
                    buscar_e_adicionar_item(driver, produto)

            st.success("Todos os produtos foram processados. Verifique o carrinho no site.")
            driver.quit()

if __name__ == "__main__":
    main()
