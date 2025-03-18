from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Base(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        # Convert datetime fields to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        decimal_fields = ["product_price_amount", "product_unit_price_amount"]
        for field in decimal_fields:
            if field in data and isinstance(data[field], Decimal):
                data[field] = float(data[field])
        return data


class ItemIds(Base):
    product_id: int = Field(default=None, primary_key=True)


class Products(Base):
    product_id: int = Field(primary_key=True)
    product_type: str
    product_name: str
    product_description: str
    product_brand: str
    product_pack_size_description: str
    product_price_amount: Decimal = Field(max_digits=10, decimal_places=2)
    product_currency: str
    product_unit_price_amount: Decimal = Field(max_digits=10, decimal_places=2)
    product_unit_price_currency: str
    product_unit_price_unit: str

    product_available: bool
    product_alcohol: bool
    product_cooking_guidelines: str
    product_categories: List[str]

    @classmethod
    def from_dict(cls, product_data: Dict[str, Any]) -> "Products":
        """Parses a dictionary into a Products instance."""
        unit_price = product_data.get("unitPrice", {})
        unit_price_price = unit_price.get("price", {})

        return cls(
            product_id=product_data["retailerProductId"],
            product_type=product_data["type"],
            product_name=product_data["name"],
            product_description=product_data["description"],
            product_brand=product_data.get("brand", ""),
            product_pack_size_description=product_data.get("packSizeDescription", ""),
            product_price_amount=Decimal(product_data["price"]["amount"]),
            product_currency=product_data["price"]["currency"],
            product_unit_price_amount=Decimal(unit_price_price.get("amount", 0)),
            product_unit_price_currency=unit_price_price.get("currency", ""),
            product_unit_price_unit=unit_price.get("unit", ""),
            product_available=product_data.get("available", False),
            product_alcohol=product_data.get("alcohol", False),
            product_cooking_guidelines=product_data.get("cookingGuidelines", ""),
            product_categories=product_data.get("categoryPath", []),
        )


class ProductNutritionalData(Base):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    product_nutritional_value: Optional[str] = None
    product_nutritional_quantity: Optional[str] = None
