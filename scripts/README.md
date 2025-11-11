# OFCO thesaurus

dummy powershell script to convert orphanet diseases disabilities XML annotation to a full OFCO annotated version in OWL

## SSSOM Mapping
The [generate_sssom.py](./generate_sssom.py) script generates a SSSOM-compliant TSV from the Excel mappings.
The produced file follows the SSSOM specification [(SSSOM standard)](https://mapping-commons.github.io/sssom/).

### It includes key information such as:
- **subject_id** and **subject_label**: source concept ID and label
- **predicate_id**: relation type (skos:exactMatch, skos:broadMatch, skos:narrowMatch)
- **object_id**: target concept ID or URI
- **mapping_date** and **mapping_type**
- **author_id**: ORCID(s) of mapping authors
- **author_label**: readable name(s) for authors without ORCID

### Optional fields to define or discuss:
- **curator_id**: person generating the file in SSSOM.
- **subject_source** / **object_source**: source vocabulary and version URIs
- **comments**, **license**, **confidence**: additional SSSOM metadata