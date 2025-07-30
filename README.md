# I14Y Harvester - OGD Basel-Landschaft Catalogue (ABN)

The harvesting of the OGD Basel Landschaft catalogue was done via Github actions in ABN. Synchronisation takes place automatically every day at midnight. Synchronisation can also be triggered manually if necessary. A log file is saved after each synchronisation.

## Process Overview

In detail, the process works as follows:

### 1. Authentication Process
- Obtains access token using client credentials
- Uses secrets `CLIENT_ID` and `CLIENT_SECRET` stored securely

### 2. Data Harvesting Process
- **Loads previous state**: Reads stored dataset IDs from `dataset_ids.json`
- **Fetches current datasets**: Retrieves DCAT metadata from Basel-Landschaft API  ( `data.bl.ch/api/explore/v2.1/catalog/exports/dcat`)
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
      -  Level: "Public"  

### 4. Output and Logging
*(Logs retention: 2 days, configurable)*  

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
    "103: Bildung": ("Bildung, Kultur und Sport"),
    "106: Gesellschaft ": ("Bevölkerung und Gesellschaft"),
    "108: Kultur": ("Bildung, Kultur und Sport"),
    "113: Umwelt": ("Umwelt"),
    "114: Gesundheit ": ("Gesundheit"),
    "115: Wirtschaft": ("Wirtschaft und Finanzen"),
    "116: Mobilität": ("Verkehr"),
    "117: Einwohner": ("Bevölkerung und Gesellschaft"),
    "119: Behörden": ("Regierung und öffentlicher Sektor"),
    "120: Gebäude und Grundstücke": ("Regionen und Städte"),
    "122: Geoinformationen": ("Regionen und Städte"),
    "124: Energie": ("Energie")
}
```
**Note**: All these manipulations can be modified and adapted before the official harvesting on PROD.
