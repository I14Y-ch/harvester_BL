# i14y Code: (dcat-ap.ch URI, EU data-theme URI)
THEME_MAPPING = {
    "103": ("Bildung, Kultur und Sport"),
    "106": ("Bevölkerung und Gesellschaft"),
    "108": ( "Bildung, Kultur und Sport"),
    "113": ( "Umwelt"),
    "114": ("Gesundheit"),
    "115": ("Wirtschaft und Finanzen"),
    "116": ("Verkehr"),
    "117": ("Bevölkerung und Gesellschaft"),
    "119": ("Regierung und öffentlicher Sektor"),
    "120": ("Regionen und Städte"),
    "122": ("Regionen und Städte"),
    "124": ( "Energie")

}


MEDIA_TYPE_MAPPING = {
    "https://www.iana.org/assignments/media-types/application/geo+json": "application/geo+json",
    "https://www.iana.org/assignments/media-types/application/gzip": "application/gzip",
    "https://www.iana.org/assignments/media-types/application/json": "application/json",
    "https://www.iana.org/assignments/media-types/application/ld+json": "application/ld+json",
    "https://www.iana.org/assignments/media-types/application/pdf": "application/pdf",
    "https://www.iana.org/assignments/media-types/application/rdf+xml": "application/rdf+xml",
    "https://www.iana.org/assignments/media-types/application/sparql-query": "application/sparql-query",
    "https://www.iana.org/assignments/media-types/application/sql": "application/sql",
    "https://www.iana.org/assignments/media-types/application/vnd.gentoo.gpkg": "application/vnd.gentoo.gpkg",
    "https://www.iana.org/assignments/media-types/application/vnd.rar": "application/vnd.rar",
    "https://www.iana.org/assignments/media-types/application/vnd.shp": "application/vnd.shp",
    "https://www.iana.org/assignments/media-types/application/xml": "application/xml",
    "https://www.iana.org/assignments/media-types/application/yaml": "application/yaml",
    "https://www.iana.org/assignments/media-types/application/zip": "application/zip",
    "https://www.iana.org/assignments/media-types/text/csv": "text/csv",
    "https://www.iana.org/assignments/media-types/text/html": "text/html",
    "https://www.iana.org/assignments/media-types/text/n3": "text/n3",
    "https://www.iana.org/assignments/media-types/text/vnd.gml": "text/vnd.gml",
    "https://www.iana.org/assignments/media-types/text/xml": "text/xml"
}


FORMAT_TYPE_MAPPING =  {
    "https://www.iana.org/assignments/media-types/application/geo+json": "GEOJSON",
    "https://www.iana.org/assignments/media-types/application/gzip": "GZIP",
    "https://www.iana.org/assignments/media-types/application/json": "JSON",
    "https://www.iana.org/assignments/media-types/application/ld+json": "JSON_LD",
    "https://www.iana.org/assignments/media-types/application/pdf": "PDF",
    "https://www.iana.org/assignments/media-types/application/rdf+xml": "RDF_XML",
    "https://www.iana.org/assignments/media-types/application/sparql-query": "SPARQLQ",
    "https://www.iana.org/assignments/media-types/application/sql": "SQL",
    "https://www.iana.org/assignments/media-types/application/vnd.gentoo.gpkg": "GPKG",
    "https://www.iana.org/assignments/media-types/application/vnd.rar": "RAR",
    "https://www.iana.org/assignments/media-types/application/vnd.shp": "SHP",
    "https://www.iana.org/assignments/media-types/application/xml": "XML",
    "https://www.iana.org/assignments/media-types/application/yaml": "YAML",
    "https://www.iana.org/assignments/media-types/application/zip": "ZIP",
    "https://www.iana.org/assignments/media-types/text/csv": "CSV",
    "https://www.iana.org/assignments/media-types/text/html": "HTML",
    "https://www.iana.org/assignments/media-types/text/n3": "N3",
    "https://www.iana.org/assignments/media-types/text/vnd.gml": "GML",
    "https://www.iana.org/assignments/media-types/text/xml": "XML"
}

VALID_FORMAT_CODES = {"CSV", "DXF", "EPUB", "GDB", "GEOJSON", "GEOTIFF", "GIF", "GML", "GPKG", "GPX",
    "HTML", "INTERLIS", "JPEG", "JSON", "JSON_LD", "KML", "MP3", "N3", "ODS", "PDF",
    "PNG", "RDF", "RDF_TURTLE", "RDF_XML", "RSS", "SCHEMA_XML", "SDMX", "SHP", "SKOS_XML",
    "SPARQLQ", "SQL", "SVG", "TIFF", "TSV", "TXT", "WFS_SRVC", "WMS_SRVC", "WMTS_SRVC",
    "XLS", "XLSX", "XML", "YAML"}

VOCAB_EU_PLANNED_AVAILABILITY = {

    "AVAILABLE": ("http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE", "http://data.europa.eu/r5r/availability/available" ), 
    "EXPERIMENTAL": ("http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL", "http://data.europa.eu/r5r/availability/experimental" ),
    "STABLE": ("http://publications.europa.eu/resource/authority/planned-availability/STABLE", "http://data.europa.eu/r5r/availability/stable"),
    "TEMPORARY": ("http://publications.europa.eu/resource/authority/planned-availability/TEMPORARY", "http://data.europa.eu/r5r/availability/temporary"), 
  
}

LANGUAGES_MAPPING = {
    "de": ("de", "DE","http://publications.europa.eu/resource/authority/language/DEU", "http://id.loc.gov/vocabulary/iso639-1/de" ),
    "fr": ("fr","FR","http://publications.europa.eu/resource/authority/language/FRA", "http://id.loc.gov/vocabulary/iso639-1/fr" ),
    "it": ("it", "IT","http://publications.europa.eu/resource/authority/language/ITA", "http://id.loc.gov/vocabulary/iso639-1/it" ),
    "en": ("en", "EN", "http://publications.europa.eu/resource/authority/language/ENG", "http://id.loc.gov/vocabulary/iso639-1/en" )
}

VALID_LICENSE_CODES= {"terms_open", "terms_by", "terms_by_ask", "terms_ask"}
