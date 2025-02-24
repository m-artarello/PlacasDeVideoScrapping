import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote

# Definindo as variáveis iniciais
site = None
category = None
product = None

# Lista de formatos de busca
search_formats = [
    "busca/{}",
    "search?q={}",
    "busca?str={}",
    "pesquisa?q={}",
    "?s={}"
]

def get_ecommerce_link(html):
    div = html.find("div", attrs={"data-type": "web"})

    if div:
        link = div.find("a")
        if link:
            href = link.get("href")
            print("Link encontrado:", href)
            return href
        else:
            print("Nenhum link encontrado dentro da div.")
    else:
        print("Nenhuma div encontrada.")

def user_search_data():
    # Solicita qual e-commerce acessar e converte na query de pesquisa
    eCommerce = input("Qual e-commerce deseja acessar? ")
    queryECommerce = quote(f"{eCommerce} site oficial")

    # Faz a busca do e-commerce no Bing
    search_url = f"https://search.brave.com/search?q={queryECommerce}"

    # Faz a requisição ao Bing
    response = requests.get(search_url)

    if response.status_code == 200:
        # converte o resultado da pesquisa no Bing em um HTML
        html = BeautifulSoup(response.text, "html.parser")

        site = get_ecommerce_link(html)

    # solicita a categoria e o produto para o usuário
    category = input("Qual a categoria do produto? ")
    product = input("Qual produto deseja pesquisar? ")

    category = category.lower().strip()
    product = product.lower().strip()

    return site, category, product

def start_browser():
    return webdriver.Chrome()

def stop_browser(browser):
    browser.quit()

def get_page_html(pesquisa_produto):
    count = 1
    name = None
    link = None
    price = None

    # Função que realiza a busca no navegador e retorna os produtos encontrados
    browser = start_browser()
    browser.get(pesquisa_produto)

    print("Pesquisando:", pesquisa_produto)

    # Espera para carregamento da página (ajuste se necessário)
    time.sleep(3)

    page = browser.page_source
    html_page = BeautifulSoup(page, 'html.parser')

    if html_page:
        stop_browser(browser)
        return html_page
    else:
        print("Página não encontrada.")

def get_link_tag(block):
    link_tag = block.find('a', href=lambda href: href and href != '/' and category in href and product in href)

    return link_tag if link_tag else None

def format_link(link, site):
    # Verifica se o link já começa com a URL base do site
    if link.startswith(site):
        return link  # Retorna o link completo
    else:
        return site + link  # Concatena a URL base ao link

def get_name(block):
    name_tag = block.find('h2') or block.find('h3')

    if name_tag:
        # Procura por um <span> dentro do <h2> ou <h3>
        name_span = name_tag.find('span')
        if name_span:
            name = name_span.get_text(strip=True)
        else:
            # Se não houver <span>, pega o texto diretamente do <h2> ou <h3>
            name = name_tag.get_text(strip=True)
    else:
        name = None  # Retorna None se não encontrar nenhuma tag

    return name

def strip_price(price_text):
    if not price_text is None:
        return price_text.replace("\xa0", " ")
    else:
        return "Nenhum preço encontrado"

def get_price(block):
    price = None

    if get_price_a_vista(block) != "Preço não encontrado":
        return get_price_a_vista(block)
    elif get_price_test_attribute(block) != "Preço não encontrado":
        return get_price_test_attribute(block)
    elif get_price_new_price(block) != "Preço não encontrado":
        return get_price_new_price(block)
    elif get_price_price_card(block) != "Preço não encontrado":
        return get_price_price_card(block)
    else:
        "Preço não encontrado"

def get_price_price_card(block):
    price = None

    # Procura pelo span que contém o preço atual
    price_tag = block.find('span', class_=re.compile(r'priceCard'))

    if price_tag:
        # Extrai o texto do span
        price_text = price_tag.get_text(strip=True)

        price = strip_price(price_text)
        return price

    if price is None:
        return "Preço não encontrado"

def get_price_new_price(block):
    price = None
    price_tag = block.find(lambda tag: tag and 'por:' in tag.get_text(strip=True))

    if price_tag:
        # Encontra a div que contém o preço
        price_text = price_tag.find_next('div', class_=re.compile(r'new-price'))

        if price_text:
            # Extrai o valor do preço
            price = price_text.find('span').get_text(strip=True)
            return price

    if price is None:
        return "Preço não encontrado"

def get_price_test_attribute(block):
    price = None
    price_tag = block.find('p', {'data-testid': 'price-value'})

    if price_tag:
        price_text = price_tag.get_text(separator=" ", strip=True).replace("ou ", "")
        if price_text:
            price = strip_price(price_text)
            return price

    if price is None:
        return "Preço não encontrado"

def get_price_a_vista(block):
    price = None

    price_tag = block.find(lambda tag: tag.name == 'span' and 'à vista' in tag.get_text(strip=True))

    if price_tag:
        # Encontra o próximo elemento irmão que contém o preço
        price_text = price_tag.find_next(
            lambda tag: tag.name == 'div' and re.search(r'R\$\s*\d+\.?\d*,\d{2}', tag.get_text(strip=True)))

        if price_text:
            # Extrai o texto que corresponde ao preço
            price_match = re.search(r'R\$\s*\d+\.?\d*,\d{2}', price_text.get_text(strip=True))

            if price_match:
                price = price_match.group(0)  # Extrai o valor correspondente ao padrão
                return price

    if price is None:
        return "Preço não encontrado"

def get_product_grid(html_page):
    return html_page.find(class_=re.compile(r'products-grid'))

def get_products(html_page):
    # Detectando blocos de produtos
    products = []
    unique_products = set()  # Conjunto para rastrear combinações únicas de nome e preço

    if get_product_grid(html_page):
        blocks = get_product_grid(html_page)
    else:
        blocks = html_page.find_all(True)

    for block in blocks:

        if block == '\n':
            continue

        price = None
        link = None

        product_content = block.find_all(class_=re.compile(r'content'), limit=1)
        if product_content:
            product_content = product_content[0]  # Pega o primeiro resultado
        else:
            product_content = None

        link_tag = get_link_tag(block)

        if product_content:
            name = get_name(product_content)
            if name and link_tag:
                price = get_price(product_content)
        else:
            if link_tag:
                name = get_name(link_tag)
                if name and link_tag:
                    price = get_price(link_tag)

        if link_tag:
            link = link_tag['href']

        if link and name and price:
            if (name, price, link) not in unique_products:
                unique_products.add((name, price, link))
                products.append({'name': name, 'price': price, 'link': link})
    return products

# Tentando todas as URLs de busca
found_products = False

site, category, product = user_search_data()

for search_format in search_formats:
    pesquisa_produto = f"{site}{search_format.format(quote(f'{category} {product}'))}"
    html_page = get_page_html(pesquisa_produto)
    products = get_products(html_page)

    if products:
        found_products = True
        print(f"\nEncontrados {len(products)} produtos na URL: {pesquisa_produto}\n")
        for product in products:
            print("Nome:", product["name"])
            print("Preço:", product["price"])

            link = format_link(product["link"], site)
            print("Link:", link)
            print("")
        break

if not found_products:
    print("Não foram encontrados produtos em nenhum formato de pesquisa.")
