from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote

# Definindo as variáveis iniciais
site = "https://www.kabum.com.br/"
categoria = "monitor"
produto = "aoc"

# Lista de formatos de busca
search_formats = [
    "search?q={}",
    "busca/{}",
    "busca?str={}",
    "pesquisa?q={}",
    "?s={}"
]



def realizar_busca(pesquisa_produto):
    count = 1
    name = None
    link = None
    price = None
    """Função que realiza a busca no navegador e retorna os produtos encontrados"""
    browser = webdriver.Chrome()
    browser.get(pesquisa_produto)
    print("Pesquisando:", pesquisa_produto)

    # Espera para carregamento da página (ajuste se necessário)
    time.sleep(3)

    # Coletando o conteúdo da página
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Detectando blocos de produtos
    products = []
    unique_products = set()  # Conjunto para rastrear combinações únicas de nome e preço
    blocks = soup.find_all(True)

    for block in blocks:
        link_tag = block.find('a', href=True)

        if link_tag:
            parent_with_products = link_tag.find_parent(class_=re.compile(r'products'))

            if not parent_with_products:
                parent_with_products = any('product' in value for value in link_tag.attrs.values())

            link = link_tag['href'] if parent_with_products else None
        else:
            link = None

        print(count, link, name, price)

        category_normalized = categoria.lower().strip()
        product_search_normalized = produto.lower().strip()


        for tag in block.find_all(True):
            if tag.find_all(True):
                continue

            title_text_normalized = tag.get_text(strip=True).lower().strip()

            if title_text_normalized.startswith(category_normalized) and product_search_normalized in title_text_normalized:
                parent_with_products = tag.find_parent(lambda t: any('product' in str(value) for value in t.attrs.values()))
                sibling_with_products = any(
                    'product' in str(value) for sibling in tag.find_all_next(True)
                    for value in sibling.attrs.values()
                )

                if parent_with_products or sibling_with_products:
                    name = tag.get_text(strip=True)
                    break

        if not name:
            name = None

        print(count, link, name, price)

        price_match = re.search(r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', block.get_text())

        price = None

        if price_match:
            possible_price = price_match.group()

            parent_with_products = block.find_parent(lambda t: any('product' in str(value) for value in t.attrs.values()))
            sibling_with_products = any(
                'product' in str(value) for sibling in block.find_all_next(True)
                for value in sibling.attrs.values()
            )

            if parent_with_products or sibling_with_products:
                if possible_price:
                    try:
                        element = browser.find_element("xpath", f"//*[text()='{possible_price}']")
                        text_decoration = element.value_of_css_property('text-decoration')

                        if 'line-through' not in text_decoration:
                            price = possible_price
                        else:
                            for sibling_price_tag in block.find_all_next(string=re.compile(r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?')):
                                sibling_price = sibling_price_tag.strip()
                                try:
                                    sibling_element = browser.find_element("xpath", f"//*[text()='{sibling_price}']")
                                    sibling_decoration = sibling_element.value_of_css_property('text-decoration')

                                    if 'line-through' not in sibling_decoration:
                                        price = sibling_price
                                        break
                                except Exception:
                                    continue
                    except Exception:
                        pass

        print(count, link, name, price)

        if link and name and price:
            if (name, price) not in unique_products:
                unique_products.add((name, price))
                products.append({'name': name, 'price': price, 'link': link})

    browser.quit()
    count +=1
    return products

# Tentando todas as URLs de busca
found_products = False

for search_format in search_formats:
    pesquisa_produto = f"{site}{search_format.format(quote(f'{categoria} {produto}'))}"
    products = realizar_busca(pesquisa_produto)

    if products:
        found_products = True
        print(f"Encontrados {len(products)} produtos na URL: {pesquisa_produto}")
        for product in products:
            print("Nome:", product["name"])
            print("Preço:", product["price"])
            print("Link:", site + product["link"])
            print("")
        break

if not found_products:
    print("Não foram encontrados produtos em nenhum formato de pesquisa.")
