# Product and order service
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Request
from dotenv import load_dotenv
from functools import wraps
import os
from .auth import authenticate_user, authorize_roles

app = FastAPI()

@app.get("/products")
def get_products():
    return {"message" : "produsele toate"}  



# - `GET /products` 
# ```
# [
#   {
#     "id": 1,
#     "title": "Title of Publication 1",
#     "authors": "Author 1, Author 2",
#     "published_date": "2025-03-01",
#     "description": "Detailed description of the publication",
#     "price": 300
#   },
#   ...
# ]
# ```
# - `GET /products/search?q=<query>` 
# - `POST /orders` 
# ```
# # Request
# {
#   "user_id": 1,
#   "product_id": 2
# }
# ```
# ```
# # Response
# {
#   "order_id": 101,
#   "user_id": 1,
#   "product_id": 2,
#   "status": "created"
# }
# ```
