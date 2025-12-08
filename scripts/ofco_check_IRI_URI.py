# Marc Hanauer @Orphanet 2025
# Check if thesaurus classes with ICF URI Exact mapping are unique
# Check classes without ICF URI (could be legit, not systematic errors)
# NB: input/ouput files defined at the end of script
# TODO : use filename as argument
import csv
from collections import defaultdict
from datetime import datetime

def analyze_ofco_icf_mappings(filename, output_filename):
    """
    Analyze the OFCO-ICF thesaurus file and perform two checks:
    1. Identify IRIs without hasICFuri
    2. Identify duplicate hasICFuri for exact mappings (E)
    """
    
    # Data structures for analysis
    iri_to_icf = defaultdict(list)  # IRI -> list of (hasICFuri, ManualAssertion)
    icf_to_iris = defaultdict(list)  # hasICFuri -> list of IRIs with exact mapping
    all_iris = set()  # All unique OFCO IRIs
    
    # Read the file
    with open(filename, 'r', encoding='utf-8') as f:
        # Detect separator (tab or semicolon)
        first_line = f.readline()
        separator = '\t' if '\t' in first_line else ';'
        f.seek(0)
        
        reader = csv.DictReader(f, delimiter=separator)
        
        for row in reader:
            iri = row['IRI'].strip()
            has_icf_uri = row.get('hasICFuri', '').strip()
            manual_assertion = row.get('ManualAssertion', '').strip()
            
            # Collect all OFCO IRIs (exclude ECO IRIs)
            if iri and not iri.startswith('http://purl.obolibrary.org'):
                all_iris.add(iri)
            
            # Record all ICF mappings for this IRI
            if has_icf_uri:
                iri_to_icf[iri].append((has_icf_uri, manual_assertion))
                
                # If it's an exact mapping, record for duplicate checking
                if manual_assertion.startswith('E (Exact mapping'):
                    icf_to_iris[has_icf_uri].append(iri)
    
    # === CHECK 1: IRIs without hasICFuri ===
    print("=" * 80)
    print("CHECK 1: IRIs without hasICFuri")
    print("=" * 80)
    
    iris_without_icf = sorted([iri for iri in all_iris if not iri_to_icf.get(iri)])
    
    if iris_without_icf:
        print(f"\n{len(iris_without_icf)} IRI(s) without hasICFuri found:\n")
        for iri in iris_without_icf:
            # Extract readable name from IRI
            label = iri.split('/')[-1]
            print(f"  - {label}")
            print(f"    {iri}")
    else:
        print("\n✓ All IRIs have at least one hasICFuri")
    
    # === CHECK 2: Duplicate hasICFuri for exact mappings ===
    print("\n" + "=" * 80)
    print("CHECK 2: Shared hasICFuri for exact mappings (E)")
    print("=" * 80)
    
    duplicated_icf = {icf: iris for icf, iris in icf_to_iris.items() if len(iris) > 1}
    
    if duplicated_icf:
        print(f"\n{len(duplicated_icf)} shared hasICFuri found:\n")
        for icf_uri, iris in sorted(duplicated_icf.items()):
            print(f"  hasICFuri: {icf_uri}")
            print(f"  Shared between {len(iris)} IRIs:")
            for iri in sorted(iris):
                label = iri.split('/')[-1]
                print(f"    - {label}")
                print(f"      {iri}")
            print()
    else:
        print("\n✓ All hasICFuri with exact mapping (E) are unique")
    
    # === SUMMARY ===
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total OFCO IRIs analyzed: {len(all_iris)}")
    print(f"IRIs without hasICFuri: {len(iris_without_icf)}")
    print(f"Duplicated hasICFuri (E mappings): {len(duplicated_icf)}")
    print("=" * 80)
    
    # === WRITE OUTPUT FILE ===
    write_output_file(output_filename, all_iris, iris_without_icf, duplicated_icf)
    print(f"\n✓ Results written to: {output_filename}")
    
    return {
        'total_iris': len(all_iris),
        'iris_without_icf': iris_without_icf,
        'duplicated_icf': duplicated_icf
    }


def write_output_file(filename, all_iris, iris_without_icf, duplicated_icf):
    """
    Write analysis results to an output file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("OFCO-ICF MAPPING VALIDATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Check n1: IRIs without hasICFuri
        f.write("=" * 80 + "\n")
        f.write("CHECK 1: IRIs without hasICFuri\n")
        f.write("=" * 80 + "\n\n")
        
        if iris_without_icf:
            f.write(f"Found {len(iris_without_icf)} IRI(s) without hasICFuri:\n\n")
            for iri in iris_without_icf:
                label = iri.split('/')[-1]
                f.write(f"  - {label}\n")
                f.write(f"    {iri}\n\n")
        else:
            f.write("✓ All IRIs have at least one hasICFuri\n\n")
        
        # Check n2: Duplicate hasICFuri
        f.write("\n" + "=" * 80 + "\n")
        f.write("CHECK 2: Shared hasICFuri for exact mappings (E)\n")
        f.write("=" * 80 + "\n\n")
        
        if duplicated_icf:
            f.write(f"Found {len(duplicated_icf)} shared hasICFuri:\n\n")
            for icf_uri, iris in sorted(duplicated_icf.items()):
                f.write(f"  hasICFuri: {icf_uri}\n")
                f.write(f"  Shared between {len(iris)} IRIs:\n")
                for iri in sorted(iris):
                    label = iri.split('/')[-1]
                    f.write(f"    - {label}\n")
                    f.write(f"      {iri}\n")
                f.write("\n")
        else:
            f.write("✓ All hasICFuri with exact mapping (E) are unique\n\n")
        
        # Summary
        f.write("\n" + "=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total OFCO IRIs analyzed: {len(all_iris)}\n")
        f.write(f"IRIs without hasICFuri: {len(iris_without_icf)}\n")
        f.write(f"Duplicated hasICFuri (E mappings): {len(duplicated_icf)}\n")
        f.write("=" * 80 + "\n")


if __name__ == "__main__":
    # Input and output filenames
    input_filename = "OFCO_thesaurus_ICF.csv"
    output_filename = "OFCO_ICF_validation_report.txt"
    
    try:
        results = analyze_ofco_icf_mappings(input_filename, output_filename)
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
        print("Please check the file path.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
