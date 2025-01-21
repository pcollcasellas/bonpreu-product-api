import requests

response = requests.get("https://www.compraonline.bonpreuesclat.cat/sitemaps/sitemap-products-part1.xml")

print(response.text)
