# mapper-base

## Overview

This project contains code and configurations that help resolve ... 
- Dow Jones watch lists including: Risk and Compliance and High Risk Companies
- IJIC databases including: Panama Papers, Paradise Papers, Bahamas Leaks, and Offshore Leaks
- Dun and Bradstreet databases including: Principles, Contacts, and Beneficial owners

The [base_config_updates.json](base_config_updates.json) contain features and settings that help resolve these data sources.

The [base_mapper.py](base_mapper.py) script contains code that generates these special features.  It can and is called as a library by the aforementioned higher-level mappers.   It can also be run standalone to add these special features to previously prepared json files, such as your own customer data, to help match them against these data sources.

The [base_variants.json](base_variants.json) contains ISO code conversion tables to states and countries. Country and state codes are standardized on this mapper to improve matching.

Usage:

For standalone use ...
```console
python base_mapper.py --help
usage: base_mapper.py [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [-l LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        name of a json file to standardize.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        name of file to write updated json output to.
  -l LOG_FILE, --log_file LOG_FILE
                        optional statistics filename (json format).
```
To import as a class ...
```console
from base_mapper import base_library
baseLibrary = base_library('base_variants.json')
if not baseLibrary.initialized:
    print('base library not initialized!')
```

*Both of these approaches end up executing the jsonUpdater() function which creates additional features for matching the aforementioned data sources.*

## Contents

1. [Prerequisites](#Prerequisites)
2. [Installation](#Installation)
3. [Configuring Senzing](#Configuring-Senzing)
4. [Function Library](#Base-Library-Class)
5. [Standards Lists](#Base-Variant-Lists)

### Prerequisites
- python 3.6 or higher
- Senzing API version 1.7 or higher

### Installation

Place the the following files on a directory of your choice ...
- [base_mapper.py](base_mapper.py) 
- [base_variants.json](base_variants.json)

*Note: Since the mapper-base project referenced above is required by higher level mapper projects, it is necessary to place them in a common directory structure like so ...*
/senzing/mappers/mapper-base         <--
/senzing/mappers/mapper-ijic
/senzing/mappers/mapper-dj

### Configuring Senzing

*Note:* This only needs to be performed one time! In fact you may want to add these configuration updates to a master configuration file for all your data sources.

**If you are on version G2 API version 1.10 or prior**, update the G2ConfigTool.py program file on the /opt/senzing/g2/python directory with this one ... [G2ConfigTool.py](G2ConfigTool.py)

Then from the /opt/senzing/g2/python directory ...
```console
python3 G2ConfigTool.py <path-to-file>/base_config_updates.json
```
This will step you through the process of adding the additional features, attributes and other settings needed to resolve the aforementioned data sources with your own. After each command you will see a status message saying "success" or "already exists".  For instance, if you run the script twice, the second time through they will all say "already exists" which is OK.

Configuration updates include:
- addDataSource **IJIC**
- addEntityType **PERSON**
- addEntityType **ORGANIZATION**

### Base Library Class

The [base_mapper.py](base_mapper.py) contains the base_library class which contains the following functions ...

- **formatDate** Formats various date formats into a yyyy-mm-dd standard.
- **isoCountryCode** Takes incoming country names or codes and converts them to the ISO 2 or 3 digit standard. 
- **isoStateCode** Takes incoming state names or codes and converts them to the ISO 2 standard. 
- **isCompanyName** Uses key words to determine if a name string contains a company name rather than a person name.
- **makeNameKey** Uses codes and logic to clean person or organization names into name keys for the purpose of finding candidate matches.
- **attributeCategory** Used exclusively by the json updater to identify attributes used to create composite keys.
- **jsonUpdater** Reads a json record uses the attributeCategory function to identify key attributes to standardize and use in composite keys.

### Base Variant Lists

The [base_variants.json](base_variants.json) contains the following lists ...

- **ORGANIZATION_TOKENS** A dictionary of tokens that indicate a company name. 
- **PERSON_TOKENS** A dictionary of tokens that indicate a person name.
- **STATE_CODES** A dictionary of raw values to ISO state code.
- **COUNTRY_CODES** A dictionary of raw values to ISO state code.

*Notes:*
- The organization and person tokens are also used by the makeNameKey function.  An empty value strips the token, while an included value replaces it.
- These lists are meant to be extended based on data you are seeing in your data sources.  For instance ...
    - If you find a country name or code value in your data that is not contained in the country code list go ahead and add it for better matching across data sources.
    - Different industries have different keywords in company names. You will find the word "medical" in the health care industry while the word "trust" appears often in the banking idustry.

