import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

browser = webdriver.Chrome()  # start a web browser
browser.get("https://www.terabyteshop.com.br/busca?str=rtx+3060")  # navigate to URL
# wait for page to load
# by waiting for <h1> element to appear on the page
title = (
    WebDriverWait(driver=browser, timeout=10)
    .until(EC.title_contains("rtx 3060"))
)
# retrieve fully rendered HTML content
content = browser.page_source
browser.close()

soup = BeautifulSoup(content, 'html.parser')

# Lista para armazenar os produtos encontrados
rtx_products = []

# Procura por todos os elementos com a classe `product-item__box`
for product in soup.find_all("div", class_="product-item__box"):
    # Encontra o elemento `h2` que contém o título do produto
    title_element = product.find("h2")

    # Verifica se o título contém o texto "RTX"
    if title_element and "RTX 3060" in title_element.get_text() and "Placa de Vídeo" in title_element.get_text():
        product_name = title_element.get_text(strip=True)

        link_element = product.find("a", class_="product-item__name")
        product_href = link_element["href"] if link_element else None

        old_price_element = product.find("div", class_="product-item__old-price")
        old_price = old_price_element.get_text(strip=True) if old_price_element else None

        new_price_element = product.find("div", class_="product-item__new-price")
        new_price = new_price_element.get_text(strip=True) if new_price_element else None

        if new_price:
            new_price_adjusted = new_price.replace("\n", "").replace(" ", "").replace("àvista", " à vista").strip()
        else:
            new_price_adjusted = None

        # Armazena as informações do produto em um dicionário
        product_info = {
            "Nome": product_name,
            "Preço antigo": old_price,
            "Preço novo": new_price_adjusted,
            "Link": product_href
        }

        # Adiciona o produto à lista de produtos encontrados
        rtx_products.append(product_info)

for product in rtx_products:
    print("Nome: " + product.get("Nome"))
    if product.get("Preço novo") is not None:
        print("Valor: " + product.get("Preço novo"))
    else:
        print("Valor: Preço não encontrado")
    print("Link: " + product.get("Link"))
    print("")


# pesquisa = 'RTX 3060'
#
# def formatar_pesquisa_terabyte(pesquisa):
#     return 'str=' + pesquisa.replace(" ", "+")
#
# def pesquisar_produto_terabyte(pesquisa):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
#     }
#
#     pesquisa_formatada = formatar_pesquisa_terabyte(pesquisa)
#     request = requests.get("https://www.terabyteshop.com.br/busca?"+pesquisa_formatada, headers=headers)
#
#     print(request.text)
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     pesquisar_produto_terabyte(pesquisa)
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
