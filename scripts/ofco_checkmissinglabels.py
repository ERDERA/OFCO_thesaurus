# Check if a label always exists for classes and annotations properties in OFCO_thesaurus.owl
# pip install rdflib if needed
# Marc Hanauer @Orphanet 2025
# Generate output file as list of IRI (without label)


import logging
from rdflib import Graph, RDF, RDFS, OWL, URIRef

# Configuration
OWL_FILE = "OFCO_thesaurus.owl"
OUTPUT_FILE = "missing_english_labels.txt"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_missing_en_labels():
    """
    Parses the OWL file and identifies Classes and Annotation Properties
    that lack an rdfs:label with an English language tag.
    """
    logging.info(f"Loading OWL file: {OWL_FILE}...")
    g = Graph()
    try:
        g.parse(OWL_FILE, format="xml")
    except FileNotFoundError:
        logging.error(f"File not found: {OWL_FILE}")
        return
    except Exception as e:
        logging.error(f"Error parsing file: {e}")
        return

    logging.info(f"Graph loaded successfully. Total triples: {len(g)}")

    # Set to store entities (URIs) to check (using set to avoid duplicates)
    entities_to_check = set()
    
    # We are interested in owl:Class and owl:AnnotationProperty
    target_types = [OWL.Class, OWL.AnnotationProperty]

    logging.info("Collecting Classes and Annotation Properties...")
    for rdf_type in target_types:
        for subject in g.subjects(RDF.type, rdf_type):
            # We only check URIs (ignoring Blank Nodes)
            if isinstance(subject, URIRef):
                entities_to_check.add(subject)

    logging.info(f"Total entities to verify: {len(entities_to_check)}")

    missing_labels = []

    for entity in entities_to_check:
        has_en_label = False
        
        # Iterate over all rdfs:label values for this entity
        for label in g.objects(entity, RDFS.label):
            # Check if language tag exists and starts with 'en' (case insensitive)
            # This covers 'en', 'en-US', 'en-GB', etc.
            if label.language and label.language.lower().startswith('en'):
                has_en_label = True
                break
        
        if not has_en_label:
            # Determine type for reporting purposes
            entity_type = "Class"
            if (entity, RDF.type, OWL.AnnotationProperty) in g:
                entity_type = "AnnotationProperty"
            
            missing_labels.append(f"{entity} [{entity_type}]")

    # Sort results for better readability
    missing_labels.sort()

    # Write results to the output file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"Report: Entities missing English rdfs:label\n")
            f.write(f"Source file: {OWL_FILE}\n")
            f.write(f"Total found: {len(missing_labels)}\n")
            f.write("=" * 60 + "\n\n")
            
            if missing_labels:
                for item in missing_labels:
                    f.write(f"{item}\n")
            else:
                f.write("No entities found missing English labels.\n")
        
        logging.info(f"Analysis complete. Found {len(missing_labels)} entities missing English labels.")
        logging.info(f"Results written to: {OUTPUT_FILE}")

    except IOError as e:
        logging.error(f"Error writing to output file: {e}")

if __name__ == "__main__":
    check_missing_en_labels()