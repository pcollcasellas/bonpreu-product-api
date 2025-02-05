from dotenv import load_dotenv
from fastapi import FastAPI
import os
from .database import supabase
from .import_module.crud import (
    get_product_ids,
    insert_ids,
    insert_product_nutritional_data,
    insert_products,
)
from .import_module.service import (
    fetch_all_products_data,
    fetch_product_ids,
)

app = FastAPI()


@app.get("/get_products_info")
async def get_product():
    product_ids = get_product_ids()
    print(len(product_ids))

    products, products_nutritional_data = await fetch_all_products_data(product_ids)

    products_result = insert_products(products)
    insert_product_nutritional_data(products_nutritional_data)
    return {"status": "success", "inserted": len(products_result)}


@app.get("/insert_ids")
def get_ids_list():
    item_ids = fetch_product_ids()
    insert_ids(item_ids)
    return {"status": "success", "inserted_ids": len(item_ids)}
