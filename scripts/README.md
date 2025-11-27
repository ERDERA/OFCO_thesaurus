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
