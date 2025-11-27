# Convert OFCO_thesaurus.owl to CSV file, with ICF mappings
# Marc Hanauer @Orphanet 2025
# pip install rdflib if needed

from rdflib import Graph, RDFS, Namespace, URIRef, Literal
import csv

# local files
OWL_FILE = "OFCO_thesaurus.owl"
CSV_FILE = "OFCO_thesaurus_ICF.csv"

# Namespaces
OFCO = Namespace("https://w3id.org/ofco/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

HAS_ICF_URI = OFCO.hasICFuri
HAS_ICF_CODE = OFCO.hasICFcode
ECO_0000218 = OBO.ECO_0000218

g = Graph()
g.parse(OWL_FILE, format="xml")

def get_axiom_mappings(source):
    """
    Get all mappings annoted via owl:Axiom with hasICFuri
    Get list dicts : {'uri':, 'code':, 'manual':}
    """
    mappings = []
    for axiom in g.subjects(RDF.type, OWL.Axiom):
        ann_source = g.value(axiom, OWL.annotatedSource)
        ann_prop = g.value(axiom, OWL.annotatedProperty)
        if ann_source != source or ann_prop != HAS_ICF_URI:
            continue

        target = g.value(axiom, OWL.annotatedTarget)
        code = g.value(axiom, HAS_ICF_CODE)
        manual = g.value(axiom, ECO_0000218)

        mappings.append({
            'uri': str(target) if target else "",
            'code': str(code) if code else "",
            'manual': str(manual) if manual else ""
        })
    return mappings

data = []

for s in g.subjects(RDFS.label, None):
    iri = str(s)
    label = str(g.value(s, RDFS.label))

    # Parents
    parents = [str(p) for p in g.objects(s, RDFS.subClassOf)] or [""]

    # 1. Get first mappings annoted (priority)
    axiom_mappings = get_axiom_mappings(s)

    # 2. If at least one mapping annotated, use this one
    if axiom_mappings:
        mappings_to_use = axiom_mappings
    else:
        # Else, fallback on triplets (less frequent case)
        uris = [str(o) for o in g.objects(s, HAS_ICF_URI)]
        codes = [str(o) for o in g.objects(s, HAS_ICF_CODE)] or [""]
        mappings_to_use = [
            {'uri': u, 'code': c, 'manual': ''} 
            for u in uris for c in codes
        ]
        if not mappings_to_use:
            mappings_to_use = [{'uri': '', 'code': '', 'manual': ''}]

    # Generate lines by parents x mappings
    for parent in parents:
        for m in mappings_to_use:
            data.append([
                iri,
                label,
                parent,
                m['uri'],
                m['code'],
                m['manual']
            ])

# Export
with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["IRI", "Label", "Parent", "hasICFuri", "hasICFcode", "ManualAssertion"])
    writer.writerows(data)

print(f"CSV done : {CSV_FILE} ({len(data)} lignes)")