# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="E-Commerce Cart API")

# ==============================
# PRODUCTS DATABASE
# ==============================
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# ==============================
# CART & ORDERS
# ==============================
cart = []
orders = []

# ==============================
# HELPER FUNCTIONS
# ==============================
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def calculate_total(product, qty):
    return product["price"] * qty

# ==============================
# HOME
# ==============================
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}

# ==============================
# ADD TO CART
# ==============================
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if product already in cart → update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    # If not in cart → add new item
    subtotal = calculate_total(product, quantity)

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}

# ==============================
# VIEW CART
# ==============================
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

# ==============================
# REMOVE ITEM FROM CART
# ==============================
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")

# ==============================
# CHECKOUT MODEL
# ==============================
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# ==============================
# CHECKOUT
# ==============================
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    # Hint — The empty cart check in checkout()
    # This check should be at the TOP of checkout():
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    # if not cart: = True when cart list is empty []
    # 400 Bad Request = valid request format, but invalid action
    # No order is created because raise stops the function immediately

    order_list = []

    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        order_list.append(order)

    cart.clear()

    grand_total = sum(o["total_price"] for o in order_list)

    return {
        "message": "Checkout successful",
        "orders_placed": order_list,
        "grand_total": grand_total
    }

# ==============================
# VIEW ORDERS
# ==============================
@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}
