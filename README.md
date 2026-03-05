# I14Y Harvester - OGD Basel-Landschaft Catalogue (ABN)

The harvesting of the OGD Basel Landschaft catalogue was done via Github actions in ABN. Synchronisation takes place automatically every day at midnight. Synchronisation can also be triggered manually if necessary. A log file is saved after each synchronisation.

## Features

- Import DCAT datasets from xml/rdf or ttl files to I14Y API
- Supported properties for dcat.Dataset:

| Property                                                                                                                                         | Requirement level |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| **dct:title**                                                                                                                                    | mandatory         |
| **dct:description**                                                                                                                              | mandatory         |
| **dct:accessRight** (chosen from: [PUBLIC, NON_PUBLIC, CONFIDENTIAL, RESTRICTED](http://publications.europa.eu/resource/authority/access-right)) | mandatory         |
| **dct:publisher** (stated in config.py)                                                                                                          | mandatory         |
| **dct:identifier**                                                                                                                               | mandatory         |
| **dct:issued**                                                                                                                                   | optional          |
| **dct:modified**                                                                                                                                 | optional          |
| **dcat:landingPage**                                                                                                                             | optional          |
| **dcat:keyword**                                                                                                                                 | optional          |
| **dct:language**                                                                                                                                 | optional          |
| **dcat:contactPoint**                                                                                                                            | optional          |
| **documentation (foaf:page)**                                                                                                                    | optional          |
| **schema:image**                                                                                                                                 | optional          |
| **dct:temporal**                                                                                                                                 | optional          |
| **dcat:temporalResolution**                                                                                                                      | optional          |
| **frequency (dct:accrualPeriodicity)**                                                                                                           | optional          |
| **dct:isReferencedBy**                                                                                                                           | optional          |
| **dct:relation**                                                                                                                                 | optional          |
| **spatial/geographical coverage (dct:spatial)**                                                                                                  | optional          |
| **dct:conformsTo**                                                                                                                               | optional          |
| **dcat:theme**                                                                                                                                   | optional          |
| **dcat:version**                                                                                                                                 | optional          |
| **adms:versionNotes**                                                                                                                            | optional          |

prov.qualifiedAttribution and prov.qualifiedRelation are not supported automatically, you can add those informations manually on I14Y.

- Supported properties for dcat.Distribution:

| Property                                                                     | Requirement level |
| ---------------------------------------------------------------------------- | ----------------- | --- |
| **dct:title** (if not stated, set automatically to 'Datenexport')            | mandatory         |
| **dct:description** (if not stated, set automatically to 'Export der Daten') | mandatory         |
| **dcat:accessURL**                                                           | mandatory         |
| **dcat:downloadURL**                                                         | optional          |
| **dct:license**                                                              | optional          |
| **dct:issued**                                                               | optional          |
| **dct:modified**                                                             | optional          |
| **dct:rights**                                                               | optional          |
| **dct:language**                                                             | optional          |
| **schema:image**                                                             | optional          |
| **dcat:spatialResolutionInMeters**                                           | optional          |
| **dcat:temporalResolution**                                                  | optional          |     |
| **dct:conformsTo**                                                           | optional          |
| **dcat:mediaType**                                                           | optional          |
| **dct:format**                                                               | optional          |
| **dct:packageFormat**                                                        | optional          |
| **spdx:checksum**                                                            | optional          |
| **dcat:byteSize**                                                            | optional          |

## Process Overview

In detail, the process works as follows:

### 1. Authentication Process

- Obtains access token using client credentials
- Uses secrets `CLIENT_ID` and `CLIENT_SECRET` stored securely

### 2. Data Harvesting Process

- **Loads previous state**: Reads stored dataset IDs from `dataset_ids.json`
- **Fetches current datasets**: Retrieves DCAT metadata from Basel-Landschaft API ( `data.bl.ch/api/explore/v2.1/catalog/exports/dcat`)
- **Processes each dataset**:
  - Compares with previous version
  - Identifies new, updated, unchanged or deleted datasets
  - Creates appropriate payload for I14Y API

### 3. Dataset Processing Logic

- **For new/updated datasets**:
  - Checks if the dataset is valid:
    - At least one description for the dataset
    - PDF distribution is discarded
  - Creates proper API payload
  - Submits to I14Y API (`api-a.i14y.admin.ch`)
  - For new datasets, automatically sets:
    - Status: "Recorded"
    - Level: "Public"

### 4. Output and Logging

_(Logs retention: 2 days, configurable)_

- **Artifacts**:

  - `dataset_ids.json`: Current state of all processed datasets
  - `harvest_log.txt`: Detailed operation log

- **Log includes**:

  - Timestamp of operation
  - List of created datasets
  - List of updated datasets
  - List of unchanged datasets

- **Error notification**: Failures will appear in GitHub Actions logs

## Technical Implementation Details

### Dataset Identifiers

For technical reasons we added a new identifier to each dataset as follows:

- Format: `{publisherIdentifier}_datasets_{datasetNumber}`
- Example: `CH_KT_BL_dataset_10140`
- The original URI of the dataset is stored:
  - as the second identifier
  - In the field "relation" as "original"

### Theme Mapping

We mapped the BL themes to our themes:

```python
THEME_MAPPING = {
    "102": ("Bevölkerung und Gesellschaft"),
    "103": ("Bildung, Kultur und Sport"),
    "106": ("Bevölkerung und Gesellschaft"),
    "107": ("Regierung und öffentlicher Sektor"),
    "108": ("Bildung, Kultur und Sport"),
    "109": ("Landwirtschaft, Fischerei, Forstwirtschaft und Nahrungsmittel"),
    "111": ("Justiz, Rechtssystem und öffentliche Sicherheit"),
    "112": ("Wirtschaft und Finanzen"),
    "113": ("Umwelt"),
    "114": ("Gesundheit"),
    "115": ("Wirtschaft und Finanzen"),
    "116": ("Verkehr"),
    "117": ("Bevölkerung und Gesellschaft"),
    "118": ("Wirtschaft und Finanzen"),
    "119": ("Wirtschaft und Finanzen"),
    "121": ("Landwirtschaft, Fischerei, Forstwirtschaft und Nahrungsmittel"),
    "122": ("Regionen und Städte"),
    "124": ("Energie"),
    "126": ("Bevölkerung und Gesellschaft"),
}
```

**Note**: All these manipulations can be modified and adapted before the official harvesting on PROD.
