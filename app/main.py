import pandas as pd
import requests
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, SQLModel
import json

from .database import engine, get_db
from .import_module.crud import insert_ids
from .import_module.service import fetch_product_ids, fetch_product_data

app = FastAPI()


SQLModel.metadata.create_all(bind=engine)


@app.get("/")
def get_product():
    product = fetch_product_data(25535)
    print(product)


@app.get("/insert_urls")
def get_ids_list(db: Session = Depends(get_db)):
    item_ids = fetch_product_ids()()
    print(item_ids)
    insert_ids(db, item_ids)
