# OFCO thesaurus
##[deprecated] disaxml_ofco_parser.ps1

dummy powershell script to convert orphanet diseases disabilities XML annotation to a full OFCO annotated version in OWL. deprecated

## disaxml_ofco_parser.py
Python script. Input : 

OFCO_thesaurus\data\input\Disability_Orphanet_annotations.xml 

OFCO_thesaurus\OFCO_thesaurus.owl

Generate the diseases dataset annotated with OFCO thesaurus based on data from Orphanet's Knowledge base

## ofco_to_csv.py
Generate a CSV version of OFCO_thesaurus.owl with ICF mappings. Input : OFCO_thesaurus.owl

## ofco_check_IRI_URI.py
Check OFCO_thesaurus.owl : retrieve OFCO IRI without ICF URI (which could be perfectly ok). Check unicity of IRI with ICF URI Exact match. Generate a report file
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
