from .models import ItemIds, Products
from urllib.parse import unquote

import requests
from xml.etree import ElementTree
import json


def fetch_product_ids() -> list[ItemIds]:
    """
    Fetches product Ids from the sitemap XML.
    Decodes and processes them into ItemIds objects.
    """
    response = requests.get(
        "https://www.compraonline.bonpreuesclat.cat/sitemaps/sitemap-products-part1.xml"
    )

    if response.status_code != 200:
        raise Exception("Failed to fetch URL list")

    response.encoding = "utf-8"
    root = ElementTree.fromstring(response.text)
    namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    item_ids_to_insert = []
    for url in root.findall(".//sm:url/sm:loc", namespaces):
        url_text = url.text
        if url_text:
            decoded_url = unquote(url_text)
            parts = decoded_url.rstrip("/").split("/")
            item_id = int(parts[-1]) if parts else None

            if item_id:
                item_ids_to_insert.append(ItemIds(item_id=item_id))
    return item_ids_to_insert


def fetch_product_data(product_id: int) -> Products:
    """Get product data from the product_id

    Args:
        product_id (int): retailerProductId. Will be used to call the api endpoint to get the data

    Returns:
        Products (Products): Products model with the product data
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ca-ES,ca;q=0.9",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    }
    url = f"https://www.compraonline.bonpreuesclat.cat/api/webproductpagews/v5/products/bop?retailerProductId={product_id}"
    response = requests.get(url=url, headers=headers)
    response.encoding = "utf-8"
    response_json = response.json()

    product_data = response_json["product"]

    product = Products.from_dict(product_data)

    return product
    # print(product)
    # with open("data.json", "w") as f:
    #     json.dump(response_json, f, ensure_ascii=False)
