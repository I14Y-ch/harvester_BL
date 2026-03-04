import os

# OGD canton Basel-Landschaft API
API_BL_URL = "https://data.bl.ch/api/explore/v2.1/catalog/exports/dcat"

# I14Y API configuration
API_BASE_URL_DEV = "https://iop-partner-d.app.cfap02.atlantica.admin.ch/api"
API_BASE_URL = "https://api.i14y.admin.ch/api/partner/v1"
API_BASE_URL_ABN = "https://api-a.i14y.admin.ch/api/partner/v1"

GET_TOKEN_URL_DEV = "https://identity-eiam-r.eiam.admin.ch/realms/edi_bfs-i14y"
GET_TOKEN_URL_ABN = "https://identity.i14y.a.c.bfs.admin.ch/realms/bfs-sis-a/protocol/openid-connect/token"
GET_TOKEN_URL_PROD = "https://identity.i14y.c.bfs.admin.ch/realms/bfs-sis-p/protocol/openid-connect/token"


# Organization settings

# Organization settings
ORGANIZATION_ID = "CH_KT_BL"
DEFAULT_PUBLISHER = {"identifier": ORGANIZATION_ID}

# Constants
SUPPORTED_LANGUAGES = ["de", "en", "fr", "it", "rm"]
DEFAULT_TITLE = {"de": "Datenexport"}
DEFAULT_DESCRIPTION = {"de": "Export der Daten"}
EXCLUDED_MEDIA_TYPES = ["application/pdf"]
EXCLUDED_FORMAT_CODES = ["PDF"]


# File format (.xml and .rdf -> "xml", .ttl -> "ttl")
FILE_FORMAT = "xml"

I14Y_USER_AGENT = "I14Y BL Harvester (contact: i14y@bfs.admin.ch)"

# Useful when running from admin network
DEBUG_LOCAL_TEST = os.environ.get("DEBUG_LOCAL_TEST", "false") == "true"
PROXIES = {"http": "http://proxy-bvcol.admin.ch:8080", "https": "http://proxy-bvcol.admin.ch:8080"}

# Useful when e.g. we have to change the parsing of the description, becausae the source of truth is on data.bl.ch, we can delete everything from i14y and reimport later
DELETE_ALL = os.environ.get("DELETE_ALL", "false") == "true"

# TODO Sergiy: increase max_workers from 1 once we have fixed Lucene index write lock issues in iop-core
MAX_WORKERS = 1
