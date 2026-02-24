from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
import re
from typing import Dict

from rdflib import DCTERMS, RDF, RDFS, SH, XSD, Graph, Literal, Namespace, URIRef
import urllib3
from common import CommonI14YAPI, reauth_if_token_expired
from config import I14Y_USER_AGENT, MAX_WORKERS, ORGANIZATION_ID
from utils import remove_html_tags

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class StructureImporter(CommonI14YAPI):
    """Main structure importer that works with any format"""

    @staticmethod
    def execute(api_params: Dict, import_all: bool = False):
        """Main execution"""
        # If import_all=True we import structures for all the datasets and not only those updated and created by the harvester (useful for first run)

        importer = StructureImporter(api_params)
        datasets_to_process = {}

        if not import_all:
            datasets_to_process = importer.create_datasets_to_process()

        importer.run_import(datasets_to_process, import_all=import_all)

    def __init__(self, api_params: Dict[str, str]):
        """
        api_params must be a dict containing:
        - client_key: client key to generate token
        - client_secret: client secret to generate token
        - api_get_token_url: url to generate token
        - api_base_url: url for i14y api calls
        - organization: i14y organization
        """
        super().__init__(api_params)
        self.identifier_dataset_map = {}

    def create_datasets_to_process(self) -> Dict[str, str]:
        """
        Create a dict to process based on datasets.json file.

        Returns:
            Dict[str,str]: identifier -> i14y id map
        """
        dataset_status_identifier_id_map = self.load_data(self.datasets_file_path)

        datasets_to_process = {}

        actions = ["created", "updated"]

        for action in actions:
            for identifier, i14y_id in dataset_status_identifier_id_map[action].items():
                datasets_to_process[identifier] = i14y_id

        return datasets_to_process

    def create_shacl_graph(self, metadata: Dict) -> str:
        """Create SHACL graph from metadata (format-agnostic)"""
        g = Graph()

        # Namespaces
        SH_NS = SH
        DCTERMS_NS = DCTERMS
        RDFS_NS = RDFS
        XSD_NS = XSD
        I14Y_NS = Namespace("https://www.i14y.admin.ch/resources/datasets/structure/")

        g.bind("sh", SH_NS)
        g.bind("dcterms", DCTERMS_NS)
        g.bind("rdfs", RDFS_NS)
        g.bind("xsd", XSD_NS)
        g.bind("i14y", I14Y_NS)

        # Create main shape
        shape_name = f"{metadata['identifier']}Shape"
        shape_uri = I14Y_NS[shape_name]

        g.add((shape_uri, RDF.type, SH_NS.NodeShape))

        # Add titles
        for lang, title in metadata["title"].items():
            g.add((shape_uri, RDFS_NS.label, Literal(title, lang=lang)))

        # Add descriptions
        for lang, desc in metadata["description"].items():
            g.add((shape_uri, DCTERMS_NS.description, Literal(desc, lang=lang)))

        # Add timestamps
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        g.add((shape_uri, DCTERMS_NS.created, Literal(now, datatype=XSD_NS.dateTime)))
        g.add((shape_uri, DCTERMS_NS.modified, Literal(now, datatype=XSD_NS.dateTime)))

        g.add((shape_uri, SH_NS.closed, Literal(True)))

        # Add properties
        for i, prop in enumerate(metadata["properties"]):
            prop_uri = I14Y_NS[f"{shape_name}/{prop['name']}"]

            g.add((prop_uri, RDF.type, SH_NS.PropertyShape))
            g.add((shape_uri, SH_NS.property, prop_uri))
            g.add((prop_uri, SH_NS.path, prop_uri))
            g.add((prop_uri, SH_NS.order, Literal(i)))
            g.add((prop_uri, SH_NS.minCount, Literal(1)))
            g.add((prop_uri, SH_NS.maxCount, Literal(1)))

            # Set datatype
            datatype_map = {
                "string": XSD_NS.string,
                "integer": XSD_NS.integer,
                "decimal": XSD_NS.decimal,
                "gYear": XSD_NS.gYear,
                "date": XSD_NS.date,
                "boolean": XSD_NS.boolean,
            }
            datatype = datatype_map.get(prop["datatype"], XSD_NS.string)
            g.add((prop_uri, SH_NS.datatype, datatype))

            # Add multilingual names
            for lang, label in prop["labels"].items():
                g.add((prop_uri, SH_NS.name, Literal(label, lang=lang)))

            if prop.get("pattern"):
                g.add((prop_uri, SH_NS.pattern, Literal(prop["pattern"])))

            if prop.get("conformsTo"):
                g.add((prop_uri, DCTERMS_NS.conformsTo, URIRef(prop["conformsTo"])))

            if prop.get("description"):
                for lang, desc in prop["description"].items():
                    if desc:
                        g.add((prop_uri, SH_NS.description, Literal(desc, lang=lang)))

        return g.serialize(format="turtle")

    @reauth_if_token_expired
    def upload_structure(self, dataset_id: str, turtle_data: str) -> bool:
        """Upload SHACL structure to API"""
        headers = {
            "Authorization": self.api_token,
            "User-Agent": I14Y_USER_AGENT,
            # Remove Content-Type header; requests will set it automatically for multipart/form-data
        }

        url = f"{self.api_base_url}/datasets/{dataset_id}/structures/imports"

        # Prepare the file for multipart upload
        files = {"file": ("structure.ttl", turtle_data, "text/turtle")}

        print(f"Uploading structure to {url}...")
        response = self.session.post(url, headers=headers, files=files, verify=False, timeout=30)
        response.raise_for_status()

        if response.status_code in {200, 201, 204}:
            print(f"\tStructure uploaded: {response.text.strip()}")
            return True

    @reauth_if_token_expired
    def delete_structure(self, dataset_id: str) -> bool:
        """Delete existing structure"""
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "User-Agent": I14Y_USER_AGENT,
        }

        url = f"{self.api_base_url}/datasets/{dataset_id}/structures"

        response = self.session.delete(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        if response.status_code in {200, 204}:
            print(f"Structure for dataset {dataset_id} deleted successfully.")
            return True
        elif response.status_code == 404:
            print(f"Structure for dataset {dataset_id} not found (already deleted or does not exist).")
            return True
        else:
            print(f"Failed to delete structure for dataset {dataset_id}: {response.status_code} - {response.text}")
            return False

    def build_identifier_dataset_map(self) -> Dict:
        """Builds a id->dataset map with fetched datasets for current organization"""
        identifier_dataset_map = {}
        all_existing_datasets = self.get_all_existing_datasets(self.organization)
        for dataset in all_existing_datasets:
            identifier = dataset["identifiers"][0]
            if self.identifier_pattern.match(identifier):
                identifier_dataset_map[identifier] = dataset
        return identifier_dataset_map

    def _process_one_structure_job(self, identifier: str, dataset_id: str) -> Dict[str, str]:
        """
        Worker job: process one dataset structure import and return a standardized result.
        """
        try:
            ok = self.process_dataset(dataset_id, identifier)
            return {
                "status": "created" if ok else "skipped",
                "identifier": identifier,
                "dataset_id": dataset_id,
            }
        except Exception as e:
            return {
                "status": "error",
                "identifier": identifier,
                "dataset_id": dataset_id,
                "error": str(e),
            }

    def get_bl_metadata(self, identifier, base_url: str = "https://data.bl.ch"):
        match = self.identifier_pattern.match(identifier)
        if match:
            dataset_id = match.group(1)
            url = f"{base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            raw_metadata = response.json()

            metas_default = raw_metadata.get("metas", {}).get("default", {})
            lang = metas_default.get("language", "de")

            datatype_map = {
                "text": "string",
                "int": "integer",
                "double": "decimal",
                "float": "decimal",
                "boolean": "boolean",
                "date": "date",
                "datetime": "string",
                "timestamp": "string",
                "geo_shape": "string",
                "geo_point_2d": "string",
            }

            properties = []

            for field in raw_metadata.get("fields", []):
                ods_type = field.get("type", "").lower()

                p = {
                    "name": field["name"],
                    "datatype": datatype_map.get(ods_type, "string"),
                    "labels": {lang: remove_html_tags(field.get("label", field["name"]))},
                }

                if ods_type == "geo_shape":
                    # BL: GeoJSON "geometry" object (type + coordinates)
                    p["conformsTo"] = "https://datatracker.ietf.org/doc/html/rfc7946#section-3.1"
                    p["pattern"] = (
                        r'^\s*\{\s*"coordinates"\s*:\s*\[.*\]\s*,\s*"type"\s*:\s*"(Polygon|MultiPolygon|Point|MultiPoint|LineString|MultiLineString|GeometryCollection)"\s*\}\s*$'
                    )
                    p["description"] = {
                        "en": "GeoJSON geometry object (RFC 7946 §3.1): JSON object with 'type' and 'coordinates' array."
                    }

                elif ods_type == "geo_point_2d":
                    # BL: 2D position array (exactly 2 numbers)
                    p["conformsTo"] = "https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1"
                    p["pattern"] = r"^\s*\[\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*\]\s*$"
                    p["description"] = {"en": "2D position array (RFC 7946 §3.1.1): [number, number]."}

                properties.append(p)

            return {
                "identifier": identifier,
                "title": {lang: remove_html_tags(metas_default.get("title", ""))},
                "description": {lang: remove_html_tags(metas_default.get("description", ""))},
                "properties": properties,
            }
        else:
            return {}

    def process_dataset(self, dataset_id: str, identifier: str) -> bool:
        """Process a single dataset and create structure"""
        print(f"Processing: {identifier}")

        # Get dataset from API
        dataset_data = self.identifier_dataset_map[identifier]
        if not dataset_data:
            return False

        print(f"\tDeleting existing structure (dataset was updated)")
        self.delete_structure(dataset_id)

        metadata = self.get_bl_metadata(identifier)

        if not metadata:
            print(f"No metadata for {identifier}")
            return False

        # Create and upload SHACL
        turtle_data = self.create_shacl_graph(metadata)
        success = self.upload_structure(dataset_id, turtle_data)

        if success:
            print(f"\tStructure created successfully")
            return True
        else:
            return False

    def run_import(self, datasets_to_process: Dict[str, str], import_all: bool = False):
        """
        Main import process with harvest log awareness.

        Args:
            datasets_to_process Dict[str,str]: identifier -> i14y id map for datasets to process (those created or updated by harvester)
            import_all (bool):  if True we import structures for all the datasets and not only those updated and created by the harvester (useful for first run)
                                if False we import structures only for datasets updated or created by the harvester
        """
        # Statistics
        created_structure_datasets = []
        skipped_structure_datasets = []
        error_structure_datasets = []

        print("Starting extensible structure import...")
        self.identifier_dataset_map = self.build_identifier_dataset_map()

        dataset_to_process_identifier_data_map = {}

        if import_all:
            dataset_to_process_identifier_data_map = self.identifier_dataset_map
        else:
            for identifier, _ in datasets_to_process.items():
                dataset_to_process_identifier_data_map[identifier] = self.identifier_dataset_map[identifier]

        print(f"Datasets to process: {len(dataset_to_process_identifier_data_map)}")

        # Process datasets
        jobs = []
        for identifier, data in dataset_to_process_identifier_data_map.items():
            dataset_id = data.get("id")
            if not dataset_id:
                continue
            jobs.append((identifier, dataset_id))

        # TODO Sergiy: increase max_workers from 1 once we have fixed Lucene index write lock issues in iop-core
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = [
                executor.submit(self._process_one_structure_job, identifier, dataset_id)
                for identifier, dataset_id in jobs
            ]

            for future in as_completed(futures):
                r = future.result()
                status = r["status"]
                identifier = r["identifier"]
                dataset_id = r["dataset_id"]

                if status == "created":
                    created_structure_datasets.append(f"{identifier} : {dataset_id}")
                elif status == "skipped":
                    skipped_structure_datasets.append(f"{identifier} : {dataset_id}")
                else:
                    error_structure_datasets.append(
                        f"{identifier} : {dataset_id} -> {r.get('error', 'unknown error')}"
                    )

        created_structures = len(created_structure_datasets)
        skipped = len(skipped_structure_datasets)
        errors = len(error_structure_datasets)

        # Print summary
        print(f"\n=== Summary ===")
        print(f"Structures created: {created_structures}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")

        # Save log
        log_content = f"Structure import completed at {datetime.now()}"
        log_content += f"\nResults:\n"
        log_content += f"\nStructures created: {created_structures}"
        for x in created_structure_datasets:
            log_content += f"\n- {x}"
        log_content += f"\nSkipped: {skipped}"
        for x in skipped_structure_datasets:
            log_content += f"\n- {x}"
        log_content += f"\nErrors: {errors}"
        for x in error_structure_datasets:
            log_content += f"\n- {x}"

        with open("structure_import_log.txt", "w") as f:
            f.write(log_content)

        print("Log saved to structure_import_log.txt")

        if errors > 0:
            raise Exception("There were errors in structure import script")


if __name__ == "__main__":
    api_params = {
        "client_key": os.environ["CLIENT_KEY"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "api_get_token_url": os.environ["GET_TOKEN_URL"],
        "api_base_url": os.environ["API_BASE_URL"],
        "organization_id": ORGANIZATION_ID,
        "identifier_pattern": re.compile(r"^CH_KT_BL_dataset_(\d+)$"),
    }

    import_all = os.environ.get("IMPORT_ALL", "False") == "True"

    StructureImporter.execute(api_params, import_all=import_all)
