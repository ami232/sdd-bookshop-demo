import os
import time
from urllib.parse import unquote, urlparse

import pymssql


def connect():
    """Open a connection using DATABASE_URL: mssql://user:password@host:port/database"""
    url = urlparse(os.environ["DATABASE_URL"])
    return pymssql.connect(
        server=url.hostname,
        port=url.port or 1433,
        user=unquote(url.username),
        password=unquote(url.password),
        database=url.path.lstrip("/"),
        login_timeout=5,
        timeout=5,
    )


def connect_with_retry(attempts=30, delay=2.0):
    """SQL Server needs about 20 s to accept connections; Azure SQL serverless can need as long to resume."""
    for attempt in range(1, attempts + 1):
        try:
            return connect()
        except pymssql.Error as error:
            if attempt == attempts:
                raise
            print(f"database not ready ({attempt}/{attempts}): {error}", flush=True)
            time.sleep(delay)
