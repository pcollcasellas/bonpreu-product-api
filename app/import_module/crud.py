from requests import session
from ..database import Session
from .models import ItemIds, Products
from typing import List
from sqlalchemy.exc import IntegrityError


def insert_ids(db: Session, items: List[ItemIds]) -> None:
    """
    Inserts a list of ItemIds objects into the database using bulk insert.
    """
    try:
        db.add_all(items)
        db.commit()
    except IntegrityError:
        db.rollback()
        print("Error: Duplicate item_id found during insert.")


def insert_product(db: Session, product: Products) -> None:
    try:
        db.add(product)
        db.commit()
    except:
        db.rollback()
        print(f"Could not insert product {product.id}")
