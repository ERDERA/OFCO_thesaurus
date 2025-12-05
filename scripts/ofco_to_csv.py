# Convert OFCO_thesaurus.owl to CSV file, with ICF mappings
# Marc Hanauer @Orphanet 2025
# pip install rdflib if needed
# Modified for Excel compatibility (semicolon separator, utf-8-sig)
# Adding Definition and annotation properties section at the end
# NB: the output file is used to run ofco_check_IRI_URI.py
# TODO : use filename as argument


from rdflib import Graph, RDFS, Namespace, URIRef, RDF, OWL
import csv

# Local files
OWL_FILE = "OFCO_thesaurus.owl"
CSV_FILE = "OFCO_thesaurus_ICF.csv"

# Namespaces
OFCO = Namespace("https://w3id.org/ofco/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
# Note: EFO definition URI is http://www.ebi.ac.uk/efo/definition
# We use the base namespace to construct it
EFO = Namespace("http://www.ebi.ac.uk/efo/") 

HAS_ICF_URI = OFCO.hasICFuri
HAS_ICF_CODE = OFCO.hasICFcode
ECO_0000218 = OBO.ECO_0000218

print("Loading OWL graph...")
g = Graph()
g.parse(OWL_FILE, format="xml")
print(f"Graph loaded with {len(g)} triples.")

def get_axiom_mappings(source):
    """
    Retrieve mappings annotated via owl:Axiom (hasICFuri)
    Returns a list of dicts: {'uri':, 'code':, 'manual':}
    """
    mappings = []
    # Search for axioms having 'source' as the subject
    for axiom in g.subjects(OWL.annotatedSource, source):
        # Check if it is indeed an annotation on hasICFuri
        if (axiom, OWL.annotatedProperty, HAS_ICF_URI) in g:
             target_uri = g.value(axiom, OWL.annotatedTarget)
             
             # Retrieve the code (if present)
             code_val = g.value(axiom, HAS_ICF_CODE)
             code = str(code_val) if code_val else ""
             
             # Retrieve manual assertion (ECO_0000218)
             manual_val = g.value(axiom, ECO_0000218)
             manual = str(manual_val) if manual_val else ""

             mappings.append({
                 'uri': str(target_uri),
                 'code': code,
                 'manual': manual
             })
    return mappings

data = []

# --- 1. Concept Extraction (Classes) ---
print("Extracting concepts...")
for s in g.subjects(RDFS.label, None):
    # Exclude Annotation Properties from the main list (processed separately)
    if (s, RDF.type, OWL.AnnotationProperty) in g:
        continue

    iri = str(s)
    label = str(g.value(s, RDFS.label))

    # Definition retrieval (efo:definition)
    # Look for the value associated with property http://www.ebi.ac.uk/efo/definition
    definition_val = g.value(s, EFO.definition)
    # Replace newlines with spaces to ensure CSV integrity
    definition = str(definition_val).replace('\n', ' ') if definition_val else ""

    # Parents
    parents = [str(p) for p in g.objects(s, RDFS.subClassOf) if isinstance(p, URIRef)] 
    if not parents:
        parents = [""]

    # 1. Annotated mappings (priority)
    axiom_mappings = get_axiom_mappings(s)

    # 2. Otherwise, direct mappings
    if axiom_mappings:
        mappings_to_use = axiom_mappings
    else:
        uris = [str(o) for o in g.objects(s, HAS_ICF_URI)]
        codes = [str(o) for o in g.objects(s, HAS_ICF_CODE)]
        
        # Ensure lists are not empty for the loop
        if not codes: codes = [""]
        if not uris: uris = [""]

        mappings_to_use = [
            {'uri': u, 'code': c, 'manual': ''} 
            for u in uris for c in codes
            if u != "" or c != ""
        ]
        if not mappings_to_use:
             mappings_to_use = [{'uri': '', 'code': '', 'manual': ''}]

    # Generate CSV lines
    for parent in parents:
        for m in mappings_to_use:
            data.append([
                iri,
                label,
                definition, # Definition column
                parent,
                m['uri'],
                m['code'],
                m['manual']
            ])

# --- 2. Annotation Properties Extraction ---
print("Extracting Annotation Properties...")
annotation_properties_data = []

# Search for everything typed as owl:AnnotationProperty
for s in g.subjects(RDF.type, OWL.AnnotationProperty):
    iri = str(s)
    
    # Label
    label_val = g.value(s, RDFS.label)
    label = str(label_val) if label_val else ""
    
    # Definition
    definition_val = g.value(s, EFO.definition)
    definition = str(definition_val).replace('\n', ' ') if definition_val else ""
    
    rdf_type = "owl:AnnotationProperty"
    
    annotation_properties_data.append([iri, label, definition, rdf_type])


# --- 3. Writing CSV File ---
# 'utf-8-sig' allows Excel to recognize special characters (BOM)
with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
    # Use semicolon as separator for Excel compatibility
    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Headers for concepts
    writer.writerow(["IRI", "Label", "Definition", "Parent", "ICF URI", "ICF Code", "Manual Mapping"])
    writer.writerows(data)
    
    # Visual separation
    writer.writerow([])
    writer.writerow([])
    
    # Annotation Properties Section
    writer.writerow(["--- SECTION ANNOTATION PROPERTIES ---", "", "", ""])
    writer.writerow(["IRI", "Label", "Definition", "Type"])
    writer.writerows(annotation_properties_data)

print(f"Extraction complete: {len(data)} concept lines and {len(annotation_properties_data)} annotation properties.")
print(f"File generated: {CSV_FILE}")