import os
from contextlib import asynccontextmanager

import pymssql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import connect, connect_with_retry

SCHEMA = """
IF OBJECT_ID('products', 'U') IS NULL
    CREATE TABLE products (
        id INT IDENTITY PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        price DECIMAL(8, 2) NOT NULL
    )
"""
SEED = """
IF NOT EXISTS (SELECT 1 FROM products)
    INSERT INTO products (name, price) VALUES
        (N'Refactoring', 45.90), (N'Clean Code', 39.50), (N'The Pragmatic Programmer', 42.00)
"""


@asynccontextmanager
async def lifespan(app):
    conn = connect_with_retry()
    with conn:
        cursor = conn.cursor()
        cursor.execute(SCHEMA)
        cursor.execute(SEED)
        conn.commit()
    yield


app = FastAPI(title="catalog", lifespan=lifespan)

# The browser calls this service from the UI's address, so that address must be allowed (CORS).
# Locally compose sets CORS_ORIGINS; on Azure the Container Apps ingress sets the CORS policy instead.
_origins = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]
if _origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"]
    )


@app.get("/health")
def health():
    """Reports only this service's own state: can it reach its own database?"""
    try:
        with connect() as conn:
            conn.cursor().execute("SELECT 1")
    except (pymssql.Error, KeyError):
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return {"status": "ok"}


@app.get("/products")
def list_products():
    with connect() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT id, name, CAST(price AS FLOAT) AS price FROM products ORDER BY id")
        return cursor.fetchall()


@app.get("/products/{product_id}")
def get_product(product_id: int):
    with connect() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "SELECT id, name, CAST(price AS FLOAT) AS price FROM products WHERE id = %s", (product_id,)
        )
        row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="product not found")
    return row
