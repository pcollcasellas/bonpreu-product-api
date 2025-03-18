import asyncio
import logging
from typing import Any
from urllib.parse import unquote
from xml.etree import ElementTree

import httpx
import requests
from fastapi import HTTPException
from tqdm.asyncio import tqdm

from app.import_module.utils import parse_nutritional_data_table

from .models import ItemIds, Products, ProductNutritionalData


# Test de push a github
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
            product_id = int(parts[-1]) if parts else None

            if product_id:
                item_ids_to_insert.append(ItemIds(product_id=product_id))
    return item_ids_to_insert


async def fetch_all_products_data(product_ids: list[int]) -> Products:
    products = []
    products_nutritional_data = []
    semaphore = asyncio.Semaphore(50)  # Set the concurrency limit to 50 requests at a time

    async def fetch_and_append_product(product_id):
        try:
            product, nutritional_data = await fetch_single_product_data(product_id, semaphore)
            products.append(product)
            products_nutritional_data.extend(nutritional_data)
        except HTTPException as e:
            logging.info(f"Product not found {product_id}")

    tasks = [fetch_and_append_product(product_id) for product_id in product_ids]

    for _ in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching products"):
        await _

    return products, products_nutritional_data


async def fetch_single_product_data(product_id: int, semaphore: asyncio.Semaphore) -> Products:
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

    async with semaphore, httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    elif response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch product data from API."
        )

    response.encoding = "utf-8"
    response_json = response.json()
    response_json["product"]["product_id"] = product_id

    product = parse_product(response_json)
    nutritional_data = parse_nutritional_data(product_id, response_json)

    return product, nutritional_data


def parse_product(response_json: dict[str]) -> Products:
    response_json["product"]["description"] = (
        response_json["bopData"].get("detailedDescription", None).replace("<br />", "")
    )

    # Find the cookingGuidelines content in the fields
    cooking_guidelines = next(
        (
            field["content"]
            for field in response_json["bopData"]["fields"]
            if field["title"] == "cookingGuidelines"
        ),
        None,
    )
    response_json["product"]["cookingGuidelines"] = (
        cooking_guidelines.replace("<br />", "") if cooking_guidelines else ""
    )
    return Products.from_dict(response_json["product"])


def parse_nutritional_data(product_id: int, response_json: dict[str]) -> list[dict[str, Any]]:
    nutritional_data = next(
        (
            field["content"]
            for field in response_json["bopData"]["fields"]
            if field["title"] == "nutritionalData"
        ),
        None,
    )
    parsed_nutritional_data = parse_nutritional_data_table(nutritional_data)

    if parsed_nutritional_data:
        return [
            ProductNutritionalData(
                product_id=product_id,
                product_nutritional_value=entry.get("productNutritionalValue"),
                product_nutritional_quantity=entry.get("productNutritionalQuantity"),
            )
            for entry in parsed_nutritional_data
        ]

    return []
