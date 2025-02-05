from typing import List
from ..database import supabase
from .models import ItemIds, ProductNutritionalData, Products


def insert_ids(items: List[ItemIds]) -> None:
    try:
        product_ids_dict = [item.model_dump() for item in items]
        supabase.table("product_ids").insert(product_ids_dict).execute()
    except Exception as e:
        print(f"Error inserting IDs: {e}")


def insert_products(products: List[Products]) -> List[Products]:
    try:
        data_to_upsert = [product.model_dump(exclude={"id"}) for product in products]
        result = (
            supabase.table("products").upsert(data_to_upsert, on_conflict="product_id").execute()
        )
        return result
    except Exception as e:
        print(f"Error inserting products: {e}")
        return []


def insert_product_nutritional_data(nutritional_data: List[ProductNutritionalData]) -> None:
    try:
        data_to_upsert = [data.model_dump(exclude={"id"}) for data in nutritional_data]

        result = (
            supabase.table("product_nutritional_data")
            .upsert(
                data_to_upsert,
                on_conflict="product_id,product_nutritional_value",
            )
            .execute()
        )
        return result
    except Exception as e:
        print(f"Error inserting nutritional data: {e}")


def get_product_ids() -> List[int]:
    all_product_ids = []
    limit = 1000  # Number of records per batch
    offset = 0

    while True:
        # Fetch a batch of records
        result = (
            supabase.table("product_ids")
            .select("product_id")
            .range(offset, offset + limit - 1)
            .execute()
        )
        batch = [row["product_id"] for row in result.data]
        all_product_ids.extend(batch)

        # Stop if we've fetched all records
        if len(batch) < limit:
            break

        # Increment the offset for the next batch
        offset += limit

    return all_product_ids
