# mapper-base

## Overview

This project contains code and configurations that help resolve ...

- Dow Jones watch lists including: Risk and Compliance and High Risk Companies
- IJIC databases including: Panama Papers, Paradise Papers, Bahamas Leaks, and Offshore Leaks
- Dun and Bradstreet databases including: Principles, Contacts, and Beneficial owners

The [base_config_updates.json](base_config_updates.json) contains optional settings that can help resolve these data sources. Make sure to read and understand the caveats before implementing them.

The [base_mapper.py](base_mapper.py) script contains code that generates these special features.  It is called as a library by the aforementioned higher-level mappers.  

The [base_variants.json](base_variants.json) contains ISO code conversion tables to states and countries. Country and state codes are standardized by this mapper to improve matching.

Usage:

To import as a class ...

```console
from base_mapper import base_library
baseLibrary = base_library('base_variants.json')
if not baseLibrary.initialized:
    print('base library not initialized!')
```

## Contents

1. [Prerequisites](#prerequisites)
1. [Installation](#installation)
1. [Configuring Senzing](#configuring-senzing)
1. [Base library class](#base-library-class)
1. [Base variant lists](#base-variant-lists)
1. [Optional ini file parameter](#optional-ini-file-parameter)

### Prerequisites

- python 3.6 or higher
- Senzing API version 1.13 or higher

### Installation

Place the the following files on a directory of your choice ...

- [base_mapper.py](base_mapper.py)
- [base_variants.json](base_variants.json)
- [base_config_updates.json](base_config_updates.json)

*Note: Since the mapper-base project referenced above is required by higher level mapper projects, it is necessary to place them in a common directory structure like so ...*

```console
/senzing/mappers/mapper-base         <--
/senzing/mappers/mapper-ijic
/senzing/mappers/mapper-dowjones
```

### Configuring Senzing

*Note:* There are optional configuration changes you can make for getting more matches against data sources such as these watch lists.  They are all commented out and you should carefully review and test the effect of any you may choose to turn on.  Remove the "#--" before a line to turn it on.

If you do decide to use any of these settings, this script only needs to be executed once. In fact you may want to add these configuration updates to a master configuration file for all your data sources.

Then from the /opt/senzing/g2/python directory ...

```console
python3 G2ConfigTool.py <path-to-file>/base_config_updates.json
```

Optional configuration updates include:

1: Use complete name, address, and group associations for candidates
   By default, only their hashes are used for candidates.
   *Effect:* minor performance impact and improvement

2: Add additional composite keys to be used for candidates
   *Effect:* minor performance impact and improvement

3: Turn off distinct name processing
   *Effect:* potential for false positives as lower quality aka matches are also reported: If "Andy Jones" and "Alex Jones" both have an aka of "A jones", the lower quality name match is not considered when distinct is on, but is a match when distinct is off!


### Base library class

The [base_mapper.py](base_mapper.py) contains the base_library class which contains the following functions ...

- **formatDate** Formats various date formats into a yyyy-mm-dd standard.
- **isoCountryCode** Takes incoming country names or codes and converts them to the ISO 2 or 3 digit standard.
- **isoStateCode** Takes incoming state names or codes and converts them to the ISO 2 standard.
- **isCompanyName** Uses key words to determine if a name string contains a company name rather than a person name.

### Base variant lists

The [base_variants.json](base_variants.json) contains the following lists ...

- **BAD_VALUES** A list of bad values such as "null" will will be ignored when creating composite keys.
- **ORGANIZATION_TOKENS** A dictionary of tokens that indicate a company name.
- **PERSON_TOKENS** A dictionary of tokens that indicate a person name.
- **STATE_CODES** A dictionary of raw values to ISO state code.
- **COUNTRY_CODES** A dictionary of raw values to ISO state code.

*Notes:*

- These lists are meant to be extended based on data you are seeing in your data sources.  For instance ...
  - If you find a country name or code value in your data that is not contained in the country code list go ahead and add it for better matching across data sources.
  - Different industries have different keywords in company names. You will find the word "medical" in the health care industry while the word "trust" appears often in the banking idustry.  Add the tokens for your industry that help identify companies.

### Optional ini file parameter

There is also an ini file parameter that can benefit watch list matching.  Place the following entry in the pipeline section the g2 ini file you use, such as /opt/senzing/g2/python/G2Module.ini as show below...

```console
[pipeline]
 NAME_EFEAT_WATCHLIST_MODE=Y
```

WARNING! This effectively doubles the number of name hashes created which improves the chances of finding a match at the cost of significant performance loss.  Consider creating a separate g2 ini file used just for searching and include this parameter.  If you include it during the loading of data, only have it on while loading the watch list as the load time will actually more than double!
