from typing import Any, Dict, List
from sqlalchemy import String, Column, DECIMAL
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from decimal import Decimal


class ItemIds(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    item_id: int = Field(nullable=False)
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)


class Products(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    retailerProductId: int = Field(nullable=False)
    productType: str
    productName: str = Field(nullable=False)
    productBrand: str
    productPackSizeDescription: str
    productPriceAmount: Decimal = Field(sa_column=Column(DECIMAL(10, 2), nullable=False))
    productCurrency: str
    productUnitPriceAmount: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    productUnitPriceCurrency: str
    productUnitPriceUnit: str
    productAvailable: bool
    productAlcohol: bool
    productCategories: List[str] = Field(sa_column=Column(ARRAY(String)))
    created_at: datetime = Field(default=datetime.now(timezone.utc), nullable=False)

    @classmethod
    def from_dict(cls, product_data: Dict[str, Any]) -> "Products":
        """Parses a dictionary into a Products instance."""
        unit_price = product_data.get("unitPrice", {})
        unit_price_price = unit_price.get("price", {})

        return cls(
            retailerProductId=product_data["retailerProductId"],
            productType=product_data["type"],
            productName=product_data["name"],
            productBrand=product_data.get("brand", ""),
            productPackSizeDescription=product_data.get("packSizeDescription", ""),
            productPriceAmount=Decimal(product_data["price"]["amount"]),
            productCurrency=product_data["price"]["currency"],
            productUnitPriceAmount=Decimal(unit_price_price.get("amount", 0)),
            productUnitPriceCurrency=unit_price_price.get("currency", ""),
            productUnitPriceUnit=unit_price.get("unit", ""),
            productAvailable=product_data.get("available", False),
            productAlcohol=product_data.get("alcohol", False),
            productCategories=product_data.get("categoryPath", []),
        )
