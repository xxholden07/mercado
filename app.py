import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

st.set_page_config(page_title="Lista de Compras - Tenda", layout="wide")
st.title("🛒 Comparador de Preços - Tenda Atacado")

uploaded_file = st.file_uploader("📤 Envie sua planilha de compras (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.dataframe(df)

    if st.button("🔍 Buscar Itens na Tenda"):
        st.info("Iniciando busca... Isso pode levar alguns segundos.")
        
        # Configurações do Selenium headless
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Inicia o driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.tendaatacado.com.br/")
        time.sleep(2)

        resultados = []

        for index, row in df.iterrows():
            produto = str(row["Produto"])
            quantidade = int(row["Quantidade"])

            st.write(f"🔎 Buscando: {produto}")

            try:
                # Localiza barra de busca
                barra_busca = driver.find_element(By.NAME, "q")
                barra_busca.clear()
                barra_busca.send_keys(produto)
                barra_busca.send_keys(Keys.RETURN)
                time.sleep(3)

                # Captura todos os itens da página de resultado
                itens = driver.find_elements(By.CSS_SELECTOR, "div.product-tile")

                opcoes = []
                for item in itens:
                    try:
                        nome = item.find_element(By.CSS_SELECTOR, "span.product-title").text
                        preco = item.find_element(By.CSS_SELECTOR, "span.sales").text
                        opcoes.append({"Nome": nome, "Preço": preco})
                    except:
                        continue

                if opcoes:
                    resultados.append({
                        "Produto Pesquisado": produto,
                        "Resultados": opcoes
                    })
                else:
                    resultados.append({
                        "Produto Pesquisado": produto,
                        "Resultados": "Nenhum item encontrado"
                    })

            except Exception as e:
                st.error(f"Erro ao buscar {produto}: {e}")
        
        driver.quit()

        st.success("Busca finalizada.")
        for item in resultados:
            st.subheader(f"🔍 {item['Produto Pesquisado']}")
            if isinstance(item["Resultados"], list):
                for opcao in item["Resultados"]:
                    st.markdown(f"- **{opcao['Nome']}** — {opcao['Preço']}")
            else:
                st.write("⚠️ Nenhum item encontrado.")
