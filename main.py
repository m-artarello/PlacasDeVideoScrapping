import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Formatos de pesquisa mapeados
search_formats = [
    "busca/{}",
    "busca?str={}",
    "search?q={}",
    "pesquisa?q={}",
    "?s={}",
]
tags = [
    "a",
    "div",
    "li"
]

# Solicita qual e-commerce acessar e converte na query de pesquisa
eCommerce = input("Qual e-commerce deseja acessar? ")
queryECommerce = quote(f"{eCommerce} site oficial")

# Faz a busca do e-commerce no Bing
search_url = f"https://www.bing.com/search?q={queryECommerce}"

# Faz a requisição ao Bing
response = requests.get(search_url)

if response.status_code == 200:
    # converte o resultado da pesquisa no Bing em um HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Pega o primeiro link nos resultados
    first_result = soup.find("a", class_="tilk")

    if first_result:
        link = first_result["href"]
        print(f"Acessando o e-commerce: {link}")
    else:
        print("Nenhum resultado encontrado.")
else:
    print("Erro ao acessar o Bing.")

# solicita a categoria e o produto para o usuário
category = input("Qual a categoria do produto?")
productSearch = input("Qual produto deseja pesquisar?")

# converte o texto de produto informado para poder realizar a pesquisa
queryProduct = quote(category + productSearch)

browser = webdriver.Chrome()

# tenta todos os formatos de pesquisa até dar certo
for format_url in search_formats:
    search_url = f"{link}{format_url.format(queryProduct)}"
    print(f"Tentando acessar a URL: {search_url}")

    browser.get(search_url)

    try:
        # Aguarda até que algum conteúdo da página tenha sido carregado
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        print(f"Página carregada com sucesso com o formato: {search_url}")
        break  # Sai do loop se a página for carregada com sucesso
    except Exception as e:
        print(f"Erro ao acessar a página com a URL {search_url}: {e}")
        continue  # Tenta o próximo formato de URL

# Se nenhuma URL carregou com sucesso
if not browser.current_url:
    print("Não foi possível acessar a página de pesquisa do produto.")
else:
    print(f"URL de pesquisa carregada com sucesso: {browser.current_url}")

# Espera até que os produtos sejam carregados
try:
    WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    print("Página carregada com sucesso!")
except:
    print("Erro ao carregar os produtos.")
    browser.quit()
    exit()

content = browser.page_source

# Converte o conteúdo da página para BeautifulSoup
converted_content = BeautifulSoup(content, 'html.parser')

# Lista para armazenar os produtos encontrados
products = []

for tag in tags:
    print(tag)
    for product in converted_content.find_all(tag, class_=re.compile("product")):
        print(product)

browser.close()

# # Itera sobre os produtos encontrados na página
# for product in converted_content.find_all("div", class_=re.compile("product")):
#     title_element = product.find("h2")
#
#     if title_element:
#         title_text_normalized = title_element.get_text(strip=True).lower()
#         product_search_normalized = productSearch.lower().strip()
#         category_normalized = category.lower().strip()
#
#         if title_text_normalized.startswith(category_normalized) and product_search_normalized in title_text_normalized:
#             product_name = title_text_normalized
#
#             link_element = product.find("a", class_="product-item__name")
#             product_href = link_element["href"] if link_element else None
#
#             price = product.find("div", class_=re.compile("price"))
#             new_price = price.get_text(strip=True) if price else None
#
#             if new_price:
#                 new_price_adjusted = new_price.replace("\n", "").replace(" ", "").replace("àvista", " à vista").strip()
#
#                 product_info = {
#                     "Nome": product_name,
#                     "Preço": new_price_adjusted,
#                     "Link": product_href
#                 }
#                 products.append(product_info)
#
# # Exibe os resultados encontrados
# if products:
#     for product in products:
#         print("Nome: " + product["Nome"])
#         print("Preço: " + product["Preço"])
#         print("Link: " + product["Link"])
#         print("")
# else:
#     print("Não foram encontrados produtos.")
