import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup
import tempfile

st.set_page_config(page_title="Tenda Atacado Bot", layout="wide")
st.title("🛒 Bot de Compras - Tenda Atacado")

uploaded_file = st.file_uploader("📤 Envie sua planilha de compras (CSV ou Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Itens na lista:", df)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get("https://www.tendaatacado.com.br/")
    sleep(3)

    selections = []

    for index, row in df.iterrows():
        termo = row["produto"]
        st.subheader(f"🔍 Resultados para: {termo}")

        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(termo)
        search_box.submit()
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        itens = soup.select(".product-item")

        opcoes = []
        for item in itens:
            nome = item.select_one(".product-item__name")
            preco = item.select_one(".sales") or item.select_one(".price")
            link = item.select_one("a")

            if nome and preco and link:
                opcoes.append({
                    "nome": nome.text.strip(),
                    "preco": preco.text.strip(),
                    "link": link["href"]
                })

        if not opcoes:
            st.warning(f"Nenhum resultado encontrado para '{termo}'.")
            continue

        op_df = pd.DataFrame(opcoes)
        escolha = st.selectbox(f"Escolha um item para '{termo}'", op_df["nome"].tolist(), key=termo)
        quantidade = st.number_input(f"Quantidade para '{termo}'", min_value=1, step=1, key=f"qtd_{termo}")
        selecionado = op_df[op_df["nome"] == escolha].iloc[0]
        selecionado["quantidade"] = quantidade
        selections.append(selecionado)

    st.markdown("---")
    if st.button("🛒 Adicionar ao carrinho"):
        for item in selections:
            driver.get(item["link"])
            sleep(3)
            try:
                qtd_input = driver.find_element(By.NAME, "qty")
                qtd_input.clear()
                qtd_input.send_keys(str(item["quantidade"]))
                add_btn = driver.find_element(By.CSS_SELECTOR, "button[title='Adicionar']")
                add_btn.click()
                sleep(2)
            except Exception as e:
                st.error(f"Erro ao adicionar '{item['nome']}': {e}")

        st.success("Itens adicionados ao carrinho! Você pode finalizar manualmente no site.")
        driver.quit()
