import os

# OGD canton Basel-Landschaft API
API_BL_URL = "https://data.bl.ch/api/explore/v2.1/catalog/exports/dcat"

# I14Y API configuration
API_BASE_URL = "https://api-a.i14y.admin.ch/api/partner/v1"
API_TOKEN = f"{os.environ['ACCESS_TOKEN']}" 

#IDS_I14Y = json.loads(os.environ['IDS_I14Y'])

# Organization settings
ORGANIZATION_ID =  f"{os.environ['ORGANIZATION_ID']}" 
DEFAULT_PUBLISHER = {
    "identifier": ORGANIZATION_ID
}

# Constants
SUPPORTED_LANGUAGES = ["de", "en", "fr", "it", "rm"]
DEFAULT_TITLE = {'de': 'Datenexport'}
DEFAULT_DESCRIPTION = {'de': 'Export der Daten'}
EXCLUDED_MEDIA_TYPES = ['application/pdf']
EXCLUDED_FORMAT_CODES = ['PDF']


# File format (.xml and .rdf -> "xml", .ttl -> "ttl")
FILE_FORMAT = "xml"

# Proxies if necessary 
PROXIES = {
    "http": "http://proxy...",
    "https": "http://proxy..."
}
