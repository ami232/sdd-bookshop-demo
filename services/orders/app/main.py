import os
from contextlib import asynccontextmanager

import httpx
import pymssql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.db import connect, connect_with_retry

SCHEMA = """
IF OBJECT_ID('orders', 'U') IS NULL
    CREATE TABLE orders (
        id INT IDENTITY PRIMARY KEY,
        product_id INT NOT NULL,
        quantity INT NOT NULL
    )
"""


@asynccontextmanager
async def lifespan(app):
    conn = connect_with_retry()
    with conn:
        conn.cursor().execute(SCHEMA)
        conn.commit()
    yield


app = FastAPI(title="orders", lifespan=lifespan)

# The browser calls this service from the UI's address, so that address must be allowed (CORS).
# Locally compose sets CORS_ORIGINS; on Azure the Container Apps ingress sets the CORS policy instead.
_origins = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]
if _origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=_origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"]
    )


class NewOrder(BaseModel):
    product_id: int
    quantity: int = 1


@app.get("/health")
def health():
    """Reports only this service's own state. A catalog outage does not make orders unhealthy."""
    try:
        with connect() as conn:
            conn.cursor().execute("SELECT 1")
    except (pymssql.Error, KeyError):
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return {"status": "ok"}


@app.get("/orders")
def list_orders():
    with connect() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT id, product_id, quantity FROM orders ORDER BY id")
        return cursor.fetchall()


@app.post("/orders", status_code=201)
def create_order(order: NewOrder):
    """The call that crosses the seam: the product must exist in the catalog service."""
    catalog_url = os.environ["CATALOG_URL"]
    try:
        response = httpx.get(f"{catalog_url}/products/{order.product_id}", timeout=2.0)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="catalog service unavailable, try again later")
    if response.status_code == 404:
        raise HTTPException(status_code=422, detail="unknown product")
    response.raise_for_status()
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (product_id, quantity) OUTPUT INSERTED.id VALUES (%s, %s)",
            (order.product_id, order.quantity),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
    return {"id": new_id, "product_id": order.product_id, "quantity": order.quantity}
