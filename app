import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os

# ---------- CONFIG ----------
UPLOAD_EXAMPLE = 'lista_compras_exemplo.xlsx'
SITE_URL = 'https://www.tendaatacado.com.br/'

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Bot de Compras - Tenda Atacado", layout="wide")
st.title("🤖 Carrinho Automático - Tenda Atacado")

st.markdown("Faça upload da sua lista de compras. Ela deve conter uma coluna chamada `produto`.")

# Modelo de planilha exemplo
with open(UPLOAD_EXAMPLE, "wb") as f:
    f.write(b"produto\nArroz 5kg\nFeijao preto 1kg\nMacarrao espaguete\n")
st.download_button("📄 Baixar modelo de planilha", data=open(UPLOAD_EXAMPLE, "rb"), file_name="modelo_lista_compras.xlsx")

file = st.file_uploader("📤 Envie sua planilha de compras (.xlsx)", type=["xlsx"])

# ---------- FUNÇÃO DE BUSCA E ADIÇÃO AO CARRINHO ----------
def adicionar_produtos_ao_carrinho(produtos):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(SITE_URL)
    time.sleep(3)

    for produto in produtos:
        try:
            search_box = driver.find_element(By.NAME, 'q')
            search_box.clear()
            search_box.send_keys(produto)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            # Clica no primeiro produto encontrado
            first_product = driver.find_element(By.CSS_SELECTOR, 'div.product-box')
            first_product.click()
            time.sleep(2)

            # Adiciona ao carrinho
            botao_comprar = driver.find_element(By.ID, 'buy-button')
            botao_comprar.click()
            time.sleep(2)

            st.success(f"✅ Produto adicionado: {produto}")

            driver.get(SITE_URL)
            time.sleep(2)

        except Exception as e:
            st.warning(f"⚠️ Falha ao adicionar '{produto}': {e}")

    driver.quit()

# ---------- LÓGICA PRINCIPAL ----------
if file:
    df = pd.read_excel(file)
    if 'produto' not in df.columns:
        st.error("❌ A planilha deve conter uma coluna chamada 'produto'.")
    else:
        st.write("🛒 Lista de produtos:", df)
        if st.button("Iniciar busca e adicionar ao carrinho"):
            produtos = df['produto'].dropna().tolist()
            adicionar_produtos_ao_carrinho(produtos)
