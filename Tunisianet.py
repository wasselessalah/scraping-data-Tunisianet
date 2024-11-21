import requests
from bs4 import BeautifulSoup
import csv
import math

# Input the product name to search
search_prod = input("Give me the name of the product: ").strip()
base_url = "https://www.tunisianet.com.tn/recherche?controller=search&orderby=price&orderway=asc"
output_file = f'{search_prod.replace(" ", "")}.csv'

# Scrape a single page
def scrape_page(page_url):
    try:
        response = requests.get(page_url)
        
        # detecter les err si les url n'est pas valide
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'lxml')

        # Select product section
        products = soup.find_all('div', {'class': 'item-product'})
        details = []

        for product in products:
            try:
                # Get title of the product
                product_title = product.find('h2', {'class': 'product-title'}).find('a').text.strip()

                # Get price of the product
                price_product = product.find("span", {"class": "price"}).text.strip()

                # Get description of the product
                desc_product = product.find("div", {"class": "listds"}).find("a").text.strip()
                # add product 
                details.append({
                    "Product Title": product_title,
                    "Price": price_product,
                    "Description": desc_product,
                })
            except AttributeError:
                # Skip if any detail is missing
                continue

        return details

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

# Get total pages
def get_total_pages(base_url, search_prod):
    try:
        response = requests.get(f"{base_url}&s={search_prod}&page=1")
        
        # detecter les err si les url n'est pas valide
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Extract total number of articles
        nb_article_text = soup.find("div", {"class": "col-md-6 col-sm-6 col-xs-6 text-xs-left"})
        if nb_article_text:
            nb_article = int(nb_article_text.text.strip().split(' ')[-2])
            return math.ceil(nb_article / 24)
        return 1
    except Exception as e:
        print(f"Error determining the total number of pages: {e}")
        return 1

# Main function
def main():
  
    total_pages = get_total_pages(base_url, search_prod)
    all_products = []

    for page in range(1, total_pages + 1):
        print(f"Scraping page {page} of {total_pages}...")
        page_url = f"{base_url}&s={search_prod}&page={page}"
        products = scrape_page(page_url)
        # add product
        all_products.extend(products)

    # Save to CSV
    if all_products:
        keys = all_products[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_products)
        print(f"Data saved to {output_file}")
    else:
        print("No products found.")

if __name__ == "__main__":
    main()
