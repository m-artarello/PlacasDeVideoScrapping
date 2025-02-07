from selenium import webdriver
from bs4 import BeautifulSoup
import re
import csv
import time
from urllib.parse import quote

# Definindo as variáveis iniciais
site = "https://www.pichau.com.br"
categoria = "monitor"
produto = "aoc"

# Criando a query de pesquisa
query = quote(f"{categoria} {produto}")
pesquisa_produto = f"{site}/search?q={query}"

# Inicializando o navegador
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
blocks = soup.find_all(True)

for block in blocks:
    # Extrair link

    link_tag = block.find('a', href=True)

    # Verifica se existe um link e se algum ancestral tem classe contendo "products"
    if link_tag:
        # Verifica se algum ancestral tem classe contendo "products"
        parent_with_products = link_tag.find_parent(class_=re.compile(r'products')) #VALIDAR ATRIBUTOS DO PAI

        # Se não encontrar ancestral com "products", verifica se o próprio link tem algum atributo contendo "product"
        if not parent_with_products:
            # Verifica se algum dos atributos do link contém o texto 'product'
            parent_with_products = any('product' in value for value in link_tag.attrs.values())

        # Define o link se um dos critérios for atendido
        link = link_tag['href'] if parent_with_products else None
    else:
        link = None

    # Definir o texto da categoria e do produto a ser procurado
    category_normalized = categoria.lower().strip()
    product_search_normalized = produto.lower().strip()

    # Procurar diretamente por elementos que atendam às condições
    name = None
    for tag in block.find_all(True):
        # Ignorar tags que tenham filhos (não são folhas)
        if tag.find_all(True):
            continue

        # Normalizar o texto da tag
        title_text_normalized = tag.get_text(strip=True).lower().strip()

        # Verifica se o título começa com a categoria e contém o produto
        if title_text_normalized.startswith(category_normalized) and product_search_normalized in title_text_normalized:

            # Verificar se há um pai ou irmão com classe/atributo contendo "product"
            parent_with_products = tag.find_parent(lambda t: any('product' in str(value) for value in t.attrs.values()))

            sibling_with_products = any(
                'product' in str(value) for sibling in tag.find_all_next(True)
                for value in sibling.attrs.values()
            )

            if parent_with_products or sibling_with_products:
                name = tag.get_text(strip=True)
                break  # Se encontrar o nome válido, sai do loop

    # Se nenhum nome válido for encontrado, será None
    if not name:
        name = None

    # Buscar preços que contenham o símbolo "R$"
    price_match = re.search(
        r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', block.get_text()
    )

    price = None

    if price_match:
        # Texto bruto do possível preço
        possible_price = price_match.group()

        # Verificar se o próprio elemento, um pai ou irmão tem uma classe ou atributo com "product"
        parent_with_products = block.find_parent(lambda t: any('product' in str(value) for value in t.attrs.values()))

        sibling_with_products = any(
            'product' in str(value) for sibling in block.find_all_next(True)
            for value in sibling.attrs.values()
        )

        # Só definir o preço se o contexto for válido
        if parent_with_products or sibling_with_products:
            price = possible_price

    # Verificar se todas as informações foram capturadas
    if link and name and price:
        products.append({'name': name, 'price': price, 'link': link})

browser.quit()

# Exibindo resultados e salvando em CSV
print(f"Encontrados {len(products)} produtos")

if products:
    for product in products:
        print("Nome: " + product["name"])
        print("Preço: " + product["price"])
        print("Link: " + site + product["link"])
        print("")
else:
    print("Não foram encontrados produtos.")
