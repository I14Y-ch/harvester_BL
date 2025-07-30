from config import *
from utils import *
from mappings import *
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import DCTERMS, FOAF, RDFS, DCAT, RDF, SKOS
from rdflib import Namespace

# Namespaces
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
SCHEMA = Namespace("http://schema.org/")
PROV = Namespace("http://www.w3.org/ns/prov#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
SPDX = Namespace("http://spdx.org/rdf/terms#")
dcat3 = Namespace("http://www.w3.org/ns/dcat#")

from urllib.parse import urlparse
from typing import Optional, List, Dict, Set
import re



def extract_dataset(graph: Graph, dataset_uri: URIRef) -> Optional[Dict]:
    """Extracts dataset details from RDF graph."""
    distributions = extract_distributions(graph, dataset_uri)
    
    if not has_valid_distributions(distributions):
        print(f"Skipping dataset {dataset_uri} - no valid distributions")
        return None
  
    original_identifier = get_literal(graph, dataset_uri, DCTERMS.identifier)
    dataset_number = None
    if original_identifier and "/dataset/" in original_identifier:
        dataset_number = original_identifier.split("/dataset/")[-1].rstrip("/")
    
    new_identifier = f"CH_KT_BL_dataset_{dataset_number}" if dataset_number else original_identifier
    identifiers = [new_identifier, original_identifier] if dataset_number else [original_identifier]

    dataset = { 
        "identifiers": identifiers,
        "title": get_multilingual_literal(graph, dataset_uri, DCTERMS.title),
        "description": get_multilingual_literal(graph, dataset_uri, DCTERMS.description),
        "accessRights": {"code": "PUBLIC"},  
        "issued": get_literal(graph, dataset_uri, DCTERMS.issued, is_date=True),
        "modified": get_literal(graph, dataset_uri, DCTERMS.modified, is_date=True),
        "publisher": DEFAULT_PUBLISHER, 
        "landingPages": get_resource_list(graph, dataset_uri, DCAT.landingPage),
        "keywords": get_multilingual_keywords(graph, dataset_uri, DCAT.keyword),
        "distributions": [dist for dist in distributions if is_valid_distribution(dist)],
        "languages": get_languages(graph, dataset_uri, DCTERMS.language),
        "contactPoints": extract_contact_points(graph, dataset_uri),
        "documentation": get_resource_list(graph, dataset_uri, FOAF.page),
        "images": get_resource_list(graph, dataset_uri, SCHEMA.image),
        "temporalCoverage": get_temporal_coverage(graph, dataset_uri), 
        "frequency": get_frequency(graph, dataset_uri),
        "isReferencedBy": get_is_referenced_by(graph, dataset_uri),
        "relations": get_relations(graph, dataset_uri),
        "spatial": get_spatial(graph, dataset_uri),
        "version": get_literal(graph, dataset_uri, dcat3.version),
        "versionNotes": get_multilingual_literal(graph, dataset_uri, ADMS.versionNotes),
        "conformsTo": get_conforms_to(graph, dataset_uri),
        "themes": get_themes(graph, dataset_uri, DCAT.theme), 
        "qualifiedRelations": [{
            "hadRole": {"code": "original"}, 
            "relation": {"uri": get_literal(graph, dataset_uri, DCTERMS.identifier)}
        }] if get_literal(graph, dataset_uri, DCTERMS.identifier) else []
    }

    if not dataset["description"]:
        print("no description found")
        return None

    return remove_empty_fields(dataset)

def extract_distributions(graph: Graph, dataset_uri: URIRef) -> List[Dict]:
    """Extracts distributions for a dataset."""
    distributions = []
    for distribution_uri in graph.objects(dataset_uri, DCAT.distribution):
        title = get_multilingual_literal(graph, distribution_uri, DCTERMS.title) or DEFAULT_TITLE
        description = get_multilingual_literal(graph, distribution_uri, DCTERMS.description) or DEFAULT_DESCRIPTION
        media_type_uri = get_single_resource(graph, distribution_uri, DCAT.mediaType)
        format_uri = get_single_resource(graph, distribution_uri, DCTERMS.format)
        
        format_code = None
        if format_uri is not None:
            format_uri_str = str(format_uri)
            format_code = FORMAT_TYPE_MAPPING.get(format_uri_str, format_uri_str.split("/")[-1].upper())

        download_url = get_single_resource(graph, distribution_uri, DCAT.downloadURL)
        access_url = get_single_resource(graph, distribution_uri, DCAT.accessURL)
        common_url = access_url if access_url is not None else download_url
        download_title = get_multilingual_literal(graph, distribution_uri, RDFS.label)
        
        availability_uri = get_single_resource(graph, distribution_uri, URIRef("http://data.europa.eu/r5r/availability"))
        license_uri = get_single_resource(graph, distribution_uri, DCTERMS.license)
        license_code = str(license_uri) if license_uri is not None else None
        valid_license = license_code if license_code in VALID_LICENSE_CODES else None
        
        checksum_algorithm = get_literal(graph, distribution_uri, SPDX.checksumAlgorithm)
        checksum_value = get_literal(graph, distribution_uri, SPDX.checksumValue)
        packaging_format = get_literal(graph, distribution_uri, DCAT.packageFormat)

        distribution = {
            "title": title, 
            "description": description,  
            "format": {"code": format_code} if format_code and format_code in VALID_FORMAT_CODES else None,  
            "downloadUrl": {
                "label": download_title,  
                "uri": download_url if download_url is not None else common_url
            } if common_url is not None else None,
            "mediaType": {"code": get_media_type(media_type_uri)} if media_type_uri and get_media_type(media_type_uri) else None,
            "accessUrl": {
                "label": download_title,  
                "uri": common_url 
            } if common_url is not None else None,
            "license": {"code": valid_license} if valid_license is not None else None,  
            "availability": {"code": get_availability_code(availability_uri)} if availability_uri is not None else None,  
            "issued": get_literal(graph, distribution_uri, DCTERMS.issued, is_date=True),
            "modified": get_literal(graph, distribution_uri, DCTERMS.modified, is_date=True),
            "rights": get_literal(graph, distribution_uri, DCTERMS.rights),
            "accessServices": get_access_services(graph, distribution_uri),
            "byteSize": get_literal(graph, distribution_uri, DCAT.byteSize),
            "checksum": {
                "algorithm": {"code": checksum_algorithm} if checksum_algorithm is not None else None,
                "checksumValue": checksum_value
            } if checksum_algorithm is not None or checksum_value is not None else None,
            "conformsTo": get_conforms_to(graph, distribution_uri),
            "coverage": get_coverage(graph, distribution_uri),
            "documentation": get_resource_list(graph, distribution_uri, FOAF.page),
            "identifier": get_literal(graph, distribution_uri, DCTERMS.identifier),
            "images": get_resource_list(graph, distribution_uri, SCHEMA.image),
            "languages": get_languages(graph, distribution_uri, DCTERMS.language),
            "packagingFormat": {"code": packaging_format} if packaging_format is not None else None,
            "spatialResolution": get_literal(graph, distribution_uri, DCAT.spatialResolutionInMeters), 
            "temporalResolution": get_literal(graph, distribution_uri, DCAT.temporalResolution)
        }

        distributions.append(remove_empty_fields(distribution))
    return distributions

def is_valid_distribution(distribution: Dict) -> bool:
    """Check if a distribution is valid (not PDF)."""
    if distribution.get('mediaType') is None:
        return False
    
    media_code = distribution['mediaType'].get('code', '').lower()
    if media_code in EXCLUDED_MEDIA_TYPES:
        return False
    
    format_dict = distribution.get('format')
    if format_dict is not None and format_dict.get('code') in EXCLUDED_FORMAT_CODES:
        return False
    
    return True

def has_valid_distributions(distributions: List[Dict]) -> bool:
    """Check if a dataset has at least one valid distribution."""
    return any(is_valid_distribution(dist) for dist in distributions) if distributions else False


def get_languages(graph: Graph, subject: URIRef, predicate: URIRef) -> List[Dict]:
    """Retrieves a list of i14y codes for languages."""
    return [
        {"code": code}
        for lang_uri in graph.objects(subject, predicate)
        for code, uris in LANGUAGES_MAPPING.items()
        if str(lang_uri) in uris
    ]

def get_multilingual_literal(graph: Graph, subject: URIRef, predicate: URIRef) -> Dict[str, str]:
    """Retrieves multilingual literals from RDF graph."""
    values = {lang: "" for lang in SUPPORTED_LANGUAGES}
    for obj in graph.objects(subject, predicate):
        if isinstance(obj, Literal) and obj.language in values:
            values[obj.language] = remove_html_tags(str(obj))
    return {lang: value for lang, value in values.items() if value}

def get_literal(
    graph: Graph, 
    subject: URIRef, 
    predicate: URIRef, 
    is_date: bool = False
) -> Optional[str]:
    """Retrieves a single value from the RDF graph."""
    value = graph.value(subject, predicate)
    if value is None:
        return None

    value_str = str(value)
    return format_date(value_str) if is_date else value_str

def get_single_resource(graph: Graph, subject: URIRef, predicate: URIRef) -> Optional[str]:
    """Retrieves a single resource (URI) for a given predicate."""
    uri = graph.value(subject, predicate)
    return normalize_uri(str(uri)) if uri is not None else None

def get_resource_list(graph: Graph, subject: URIRef, predicate: URIRef) -> List[Dict]:
    """Retrieves a list of resources (URIs) for a given predicate."""
    return [{"uri": normalize_uri(str(uri))} for uri in graph.objects(subject, predicate)]

def get_multilingual_keywords(graph: Graph, subject: URIRef, predicate: URIRef) -> List[Dict]:
    """Retrieves only keywords with explicit language tags."""
    return [
        {str(lang): str(keyword_obj)}
        for keyword_obj in graph.objects(subject, predicate)
        if keyword_obj is not None and (lang := getattr(keyword_obj, 'language', None))
    ]


def get_media_type(media_type_uri: Optional[str]) -> Optional[str]:
    """Returns the media type code if it's a valid URI or direct code."""
    if media_type_uri is None:
        return None
    if media_type_uri in MEDIA_TYPE_MAPPING.values():
        return media_type_uri
    return MEDIA_TYPE_MAPPING.get(str(media_type_uri))

def get_access_services(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves accessServices from RDF graph."""
    return [
        {"id": normalize_uri(str(obj))} 
        for obj in graph.objects(subject, DCAT.accessService)
    ]


def get_coverage(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves temporal coverage from RDF graph, only accepting PeriodOfTime objects.
    Skips rdf:resource and other non-PeriodOfTime coverage declarations."""
    coverage_data = []
    
    for coverage_node in graph.objects(subject, DCTERMS.coverage):
        # Skip if it's an rdf:resource (URI reference)
        if isinstance(coverage_node, URIRef):
            continue
            
        # Check if this is a PeriodOfTime object
        if (coverage_node, RDF.type, DCTERMS.PeriodOfTime) in graph:
            start = get_literal(graph, coverage_node, DCTERMS.start) or get_literal(graph, coverage_node, DCAT.startDate)
            end = get_literal(graph, coverage_node, DCTERMS.end) or get_literal(graph, coverage_node, DCAT.endDate)
            
            if start is not None or end is not None:
                coverage_data.append({
                    "start": start,
                    "end": end
                })
    
    return coverage_data

def get_spatial(graph: Graph, dataset_uri: URIRef) -> List[str]:
    """Retrieves spatial values as a list of strings."""
    return [
        str(spatial)
        for spatial in graph.objects(dataset_uri, DCTERMS.spatial)
    ] or []

def get_frequency(graph: Graph, subject: URIRef) -> Optional[Dict]:
    """Retrieves frequency from RDF graph."""
    frequency_uri = get_single_resource(graph, subject, DCTERMS.accrualPeriodicity)
    return {"code": frequency_uri.split("/")[-1]} if frequency_uri is not None else None

def get_themes(graph: Graph, subject: URIRef, predicate: URIRef) -> List[Dict]:
    """Retrieves unique theme codes from RDF graph."""
    unique_codes: Set[str] = set()
    themes: List[Dict] = []
    
    for theme in graph.objects(subject, predicate):
        theme_codes = set()
        
        if isinstance(theme, Literal):
            theme_codes.add(str(theme))
        else:
            pref_label = next(graph.objects(theme, SKOS.prefLabel), None)
            if pref_label is not None:
                theme_label = str(pref_label)
                theme_codes.update(
                    code for code, labels in THEME_MAPPING.items()
                    if theme_label in labels
                )
        
        for code in theme_codes:
            if code not in unique_codes:
                unique_codes.add(code)
                themes.append({"code": code})
    
    return themes

def get_availability_code(availability_uri: Optional[str]) -> Optional[str]:
    """Maps availability URI to corresponding code."""
    if availability_uri is None:
        return None
    return next(
        (code for code, uris in VOCAB_EU_PLANNED_AVAILABILITY.items() 
         if availability_uri in uris),
        None
    )

def get_temporal_coverage(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves temporal coverage data from RDF graph."""
    return [
        {"start": get_literal(graph, obj, DCAT.startDate, is_date=True), 
         "end": get_literal(graph, obj, DCAT.endDate, is_date=True)}
        for obj in graph.objects(subject, DCTERMS.temporal)
        if (obj, RDF.type, URIRef("http://purl.org/dc/terms/PeriodOfTime")) in graph and (
            get_literal(graph, obj, DCAT.startDate, is_date=True) is not None or
            get_literal(graph, obj, DCAT.endDate, is_date=True) is not None
        )
    ]

def get_is_referenced_by(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves isReferencedBy from RDF graph."""
    return [
        {"uri": normalize_uri(str(obj))}
        for obj in graph.objects(subject, DCTERMS.isReferencedBy)
    ]

# def get_qualified_relations(graph: Graph, subject: URIRef) -> List[Dict]:
#     """Retrieves qualifiedRelations from RDF graph."""
#     return [
#         {
#             "hadRole": {"code": had_role.split("/")[-1]},
#             "relation": {
#                 "label": get_multilingual_literal(graph, relation, RDFS.label),
#                 "uri": normalize_uri(str(relation))
#             }
#         }
#         for obj in graph.objects(subject, PROV.qualifiedRelation)
#         if (had_role := get_single_resource(graph, obj, PROV.hadRole)) is not None and
#            (relation := get_single_resource(graph, obj, DCTERMS.relation)) is not None
#     ]

# def get_qualified_attributions(graph: Graph, subject: URIRef) -> List[Dict]:
#     """Retrieves qualifiedAttributions from RDF graph."""
#     return [
#         {
#             "agent": {"identifier": agent},
#             "hadRole": {"code": had_role.split("/")[-1]}
#         }
#         for obj in graph.objects(subject, PROV.qualifiedAttribution)
#         if (agent := get_single_resource(graph, obj, PROV.agent)) is not None and
#            (had_role := get_single_resource(graph, obj, PROV.hadRole)) is not None
#     ]

def get_relations(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves relations from RDF graph."""
    relations = []
    for obj in graph.objects(subject, DCTERMS.relation):
        for uri in re.split(r';\s+', str(obj).strip('; \t\n\r')):
            uri = uri.strip()
            if not uri:
                continue
            if is_valid_uri(uri):
                relations.append({
                    "label": get_multilingual_literal(graph, obj, RDFS.label),
                    "uri": normalize_uri(uri)
                })
            else:
                print(f"Skipping invalid relation URI: {uri}")
    return relations

def get_conforms_to(graph: Graph, subject: URIRef) -> List[Dict]:
    """Retrieves conformsTo from RDF graph."""
    return [
        {
            "label": get_multilingual_literal(graph, obj, RDFS.label),
            "uri": normalize_uri(str(obj))
        }
        for obj in graph.objects(subject, DCTERMS.conformsTo)
    ]

def extract_contact_points(graph: Graph, dataset_uri: URIRef) -> List[Dict]:
    """Extracts contact points from RDF."""
    DEFAULT_LANGUAGES = {lang: "" for lang in SUPPORTED_LANGUAGES}
    
    contact_points = []
    for contact_uri in graph.objects(dataset_uri, DCAT.contactPoint):
        fn = str(graph.value(contact_uri, VCARD.fn)) or get_multilingual_literal(graph, contact_uri, VCARD.fn)
        email = str(graph.value(contact_uri, VCARD.hasEmail) or "").removeprefix("mailto:")
        address = get_multilingual_literal(graph, contact_uri, VCARD.hasAddress)
        telephone = get_literal(graph, contact_uri, VCARD.hasTelephone)
        note = get_multilingual_literal(graph, contact_uri, VCARD.note)
        
        if any([fn, email, address, telephone, note]):
            contact_points.append({
                "fn": {"de": fn} if fn else DEFAULT_LANGUAGES,
                "hasAddress": {"de": address} if address else DEFAULT_LANGUAGES,
                "hasEmail": email,
                "hasTelephone": telephone,
                "kind": "Organization",
                "note": note if note else DEFAULT_LANGUAGES
            })
    return contact_points
