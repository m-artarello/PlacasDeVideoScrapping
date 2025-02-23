from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote


def iniciar_navegador():
    """Inicializa o navegador"""
    return webdriver.Chrome()


def carregar_pagina(browser, url):
    """Carrega a página e retorna o BeautifulSoup"""
    browser.get(url)
    print("Pesquisando:", url)
    time.sleep(3)
    return BeautifulSoup(browser.page_source, 'html.parser')


def extrair_produtos(soup, categoria, produto, browser):
    """Extrai os produtos da página"""
    products = []
    unique_products = set()

    for block in soup.find(True):
        if not block or not hasattr(block, 'attrs'):
            continue

        if (not any('product' in str(value) for tag in block.find_all(True) for value in tag.attrs.values())) and (not block.find(class_=re.compile(r'products'))):
            continue

        link = extrair_link(block)
        if link:
            name = extrair_nome(block, categoria, produto)

            if name:
                price = extrair_preco(block, browser)

        if link and name and price and (name, price) not in unique_products:
            unique_products.add((name, price))
            products.append({'name': name, 'price': price, 'link': link})

    return products


def extrair_link(block):
    """Extrai o link do produto"""
    link_tag = block.find('a', href=True)
    parent_with_products = link_tag.find_parent(class_=re.compile(r'products'))
    return link_tag['href'] if link_tag else None


def extrair_nome(block, categoria, produto):
    """Extrai o nome do produto"""
    category_normalized = categoria.lower().strip()
    product_search_normalized = produto.lower().strip()

    for tag in block.find_all(True):
        if tag.find_all(True):
            continue

        title_text_normalized = tag.get_text(strip=True).lower().strip()
        if title_text_normalized.startswith(category_normalized) and product_search_normalized in title_text_normalized:
            return tag.get_text(strip=True)

    return None


def extrair_preco(block, browser):
    """Extrai o preço do produto"""
    price_match = re.search(r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', block.get_text())
    if not price_match:
        return None

    possible_price = price_match.group()
    try:
        element = browser.find_element("xpath", f"//*[text()='{possible_price}']")
        text_decoration = element.value_of_css_property('text-decoration')
        if 'line-through' not in text_decoration:
            return possible_price
    except Exception:
        pass

    return None


def realizar_busca(site, categoria, produto, search_formats):
    """Realiza a busca utilizando diferentes formatos de URL"""
    browser = iniciar_navegador()
    found_products = False

    for search_format in search_formats:
        pesquisa_produto = f"{site}{search_format.format(quote(f'{categoria} {produto}'))}"
        soup = carregar_pagina(browser, pesquisa_produto)
        products = extrair_produtos(soup, categoria, produto, browser)

        if products:
            found_products = True
            print(f"Encontrados {len(products)} produtos na URL: {pesquisa_produto}")
            for product in products:
                print("Nome:", product["name"])
                print("Preço:", product["price"])
                print("Link:", site + product["link"])
                print("")
            break

    browser.quit()
    if not found_products:
        print("Não foram encontrados produtos em nenhum formato de pesquisa.")


if __name__ == "__main__":
    site = "https://www.pichau.com.br/"
    categoria = "monitor"
    produto = "aoc"
    search_formats = ["search?q={}", "busca/{}", "busca?str={}", "pesquisa?q={}", "?s={}"]

    realizar_busca(site, categoria, produto, search_formats)
