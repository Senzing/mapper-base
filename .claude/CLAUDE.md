# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **mapper-base**, a Python library providing base utilities for Senzing data mappers. It's used as a dependency by higher-level mapper projects (mapper-ijic, mapper-dowjones, etc.) for entity resolution tasks.

The `base_library` class in `src/base_mapper.py` provides:

- Date formatting and normalization (`formatDate`)
- ISO country/state code conversion (`isoCountryCode`, `isoStateCode`)
- Company vs person name detection (`isCompanyName`)
- Statistics tracking (`updateStat`)

Lookup tables in `src/base_variants.json` contain mappings for state codes, country codes, organization tokens, and person tokens.

## Development Commands

**Install all dependencies (development, testing, linting, docs):**

```bash
python -m pip install --group all .
```

**Run pylint:**

```bash
pylint $(git ls-files '*.py' ':!:docs/source/*')
```

**Run a single Python file directly:**

```bash
python src/base_mapper.py
```

## Code Style

- **Line length**: 120 characters
- **Formatter**: Black with `line-length = 120`
- **Import sorting**: isort with "black" profile
- **Linting**: Pylint with relaxed rules (see `.pylintrc` for disabled checks including `missing-module-docstring`, `missing-function-docstring`, `invalid-name`, `line-too-long`)

## Python Version Support

Python 3.10, 3.11, 3.12, and 3.13 are supported and tested in CI.
