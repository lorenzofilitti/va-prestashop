import logging
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from typing import Set, Optional, List
from dataclasses import fields

import requests
from requests import Response
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    color: Optional[str]

# TODO vedi come aggiungere oggetti al carrello tenendo conto del formato del xlm

class Cart(BaseModel):
    products: List[Product]
    id_lang: str
    id_currency: str
    id_customer: str
    id_shop_group: str
    id_shop: str
    id_address_invoice: str
    cart_row: str
    id_product: str
    id_product_attribute: str
    id_address_delivery: str
    quantity: int

class PrestaShopManager:
    def __init__(self):
        self._endpoint = "http://localhost:8080/"
        self._auth = HTTPBasicAuth("SEXH9MJL5QHYH64KN7AXAKYD7STRUDZJ", "")
        self._cart_schema: Element = self._get_cart_schema()


    def _get_cart_schema(self) -> Optional[Element]:
        fields_to_use: Set[str] = {
            "id_lang", "id_currency", "id_customer", "id_shop_group", "id_shop", "id_address_delivery",
            "id_address_invoice", "associations", "cart_rows", "cart_row", "id_product", "id_product_attribute",
            "quantity"
        }
        response: Response = requests.get(f"{self._endpoint}/api/carts?schema=blank", auth=self._auth)
        if response.status_code != 200:
            return None
        else:
            root: Element = ET.fromstring(response.content)
            cart = root.find("cart")

            for field in list(cart):
                if field.tag not in fields_to_use:
                    cart.remove(field)

            return root

    @staticmethod
    def _fill_cart_schema(cart_schema: Element, data: Cart) -> str:
        cart = cart_schema.find("cart")

        # Campi diretti sotto <cart>
        direct_fields = {
            "id_lang", "id_currency", "id_customer", "id_shop_group",
            "id_shop", "id_address_delivery", "id_address_invoice"
        }

        # Campi dentro <associations> -> <cart_rows> -> <cart_row>
        nested_fields = {
            "id_product", "id_product_attribute", "id_address_delivery",
            "quantity", "cart_row"
        }

        for key, value in dict(data):
            if key in direct_fields:
                element = cart.find(key)
                if element is not None:
                    element.text = value

            elif key in nested_fields:
                cart_row = cart.find(".//associations/cart_rows/cart_row")
                if cart_row is not None:
                    element = cart_row.find(key)
                    if element is not None:
                        element.text = value

        return ET.tostring(cart_schema, xml_declaration=True, encoding="UTF-8").decode("utf-8")

    def add_to_cart(self, data: Cart) -> None:
        schema = self._fill_cart_schema(self._cart_schema, data)
        try:
            response = requests.post(self._endpoint, data=schema, auth=self._auth)
            if response.status_code != 200:
                logging.error(f"Error: {response.status_code}")
            else:
                logging.info("Successfully added to cart")

            return response
        except Exception as e:
            logging.error(f"Error while adding data to cart: {e}")

    def get_cart_secure_key(self, cart_id: int) -> str:
        response = requests.get(f"{self._endpoint}/api/carts/{cart_id}", auth=self._auth)
        schema = ET.fromstring(response.content)
        secure_key = schema.find(".//cart/secure_key")
        return secure_key.text

    def get_redirect_link(self, id_cart: str, secure_key: str) -> str:
        return f"{self._endpoint}/restore_cart.php?id_cart={id_cart}&token={secure_key}"







if __name__ == "__main__":
    ps = PrestaShopManager()
    # b = Cart(
    #     id_lang="en",
    #     id_currency="USD",
    #     id_shop="USD",
    #     id_address_delivery="USD",
    #     id_address_invoice="USD",
    #     cart_row="USD",
    #     id_product="USD",
    #     id_product_attribute="USD",
    #     id_shop_group="d",
    #     quantity=2,
    #     id_customer="USD",
    # )
    #
    # res = ps.get_cart_secure_key(11)
    response = requests.get(f"http://localhost:8080/api/carts/7", auth=ps._auth)
    print(response)
