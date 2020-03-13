#!/usr/bin/env python3
import os
class DefaultConfig:
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    COSMOSDB_SERVICE_ENDPOINT = os.environ.get("COSMOSDB_SERVICE_ENDPOINT", "")
    COSMOSDB_KEY = os.environ.get("COSMOSDB_KEY", "")
    COSMOSDB_DATABASE_ID = os.environ.get("COSMOSDB_DATABASE_ID", "")
    COSMOSDB_CONTAINER_ID = os.environ.get("COSMOSDB_CONTAINER_ID", "")