from fastapi import FastAPI
app = FastAPI()
products = [
    {"id":1,"name":"Smartphone","price":15000,"category":"Electronics","in_stock":True},
    {"id":2,"name":"Headphones","price":2000,"category":"Electronics","in_stock":True},
    {"id":3,"name":"TShirt","price":500,"category":"Clothing","in_stock":True},
    {"id":4,"name":"Shoes","price":1200,"category":"FootWear","in_stock":False},
    # New Products added
    {"id":5,"name":"Laptop","price":50000,"category":"Electronics","in_stock":True},
    {"id":6,"name":"Watch","price":3000,"category":"Accessories","in_stock":True},
    {"id":7,"name":"Backpack","price":2500,"category":"Accessories","in_stock":False}
]
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }
@app.get("/products/{product_id}")
def get_by_category(category_name:str):
    result=[p for p in products if p["category"].lower()==category_name]
    if not result:
        return {"message": "No products found in this category"}
    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }