import json
import os

# OGD canton Basel-Landschaft API
API_BL_URL = "https://data.bl.ch/api/explore/v2.1/catalog/exports/dcat"

# I14Y API configuration
API_BASE_URL = "https://api-a.i14y.admin.ch/api/partner/v1"
API_TOKEN = f"{os.environ['ACCESS_TOKEN']}" 

#IDS_I14Y = json.loads(os.environ['IDS_I14Y'])

# Organization settings
ORGANIZATION_ID = "CH_KT_BL"
DEFAULT_PUBLISHER = {
    "identifier": ORGANIZATION_ID
}

# File format (.xml and .rdf -> "xml", .ttl -> "ttl")
FILE_FORMAT = "xml"

# Proxies
PROXIES = {
    "http": "http://proxy-bvcol.admin.ch:8080",
    "https": "http://proxy-bvcol.admin.ch:8080"
}
