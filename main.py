import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import quote

category = input("Qual a categoria do produto?")
productSearch = input("Qual produto deseja pesquisar?")

queryProduct = quote(productSearch)

browser = webdriver.Chrome()
url = f"https://www.terabyteshop.com.br/busca?str={queryProduct}"

browser.get(url)

try:
    WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-item__box"))
    )
    print("Página carregada com sucesso!")
except:
    print("Erro ao carregar os produtos.")
    browser.quit()
    exit()

content = browser.page_source
browser.close()

converted_content = BeautifulSoup(content, 'html.parser')

products = []

for product in converted_content.find_all("div", class_="product-item__box"):
    title_element = product.find("h2")

    if title_element:
        title_text_normalized = title_element.get_text(strip=True).lower()
        product_search_normalized = productSearch.lower().strip()
        category_normalized = category.lower().strip()

        if title_text_normalized.startswith(category_normalized) and product_search_normalized in title_text_normalized:
            product_name = title_text_normalized

            link_element = product.find("a", class_="product-item__name")
            product_href = link_element["href"] if link_element else None

            old_price_element = product.find("div", class_="product-item__old-price")
            old_price = old_price_element.get_text(strip=True) if old_price_element else None

            new_price_element = product.find("div", class_="product-item__new-price")
            new_price = new_price_element.get_text(strip=True) if new_price_element else None

            if new_price:
                new_price_adjusted = new_price.replace("\n", "").replace(" ", "").replace("àvista", " à vista").strip()

                product_info = {
                    "Nome": product_name,
                    "Preço antigo": old_price,
                    "Preço novo": new_price_adjusted,
                    "Link": product_href
                }
                products.append(product_info)

for product in products:
    if product:
        print("Nome: " + product.get("Nome"))
        print("Valor: " + product.get("Preço novo"))
        print("Link: " + product.get("Link"))
        print("")
    else:
        print("Não foram encontrados produtos")