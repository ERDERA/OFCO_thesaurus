#!/usr/bin/env python3
"""
XML disabilities parser mixed with OFCO thesaurus
Author: Marc Hanauer @Orphanet
Updated: 2025-11 (uses blank nodes with rdf:type for associations)
Option: --quiet  → hides warnings for missing DisabilityCategory mappings
"""

import xml.etree.ElementTree as ET
import sys
import html  # for safe XML escaping

# Configuration
OFCO_FILE = 'OFCO_thesaurus.owl'
XML_FILE = 'Disability_Orphanet_annotations.xml'
OUTPUT_FILE = 'Diseases_annotated_with_OFCO.owl'

# XML Namespaces
NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'ofco': 'https://w3id.org/ofco/',
    'xsd': 'http://www.w3.org/2001/XMLSchema#'
}


def xml_escape(text):
    """Escape XML special characters (&, <, >, ', ")"""
    if text is None:
        return ""
    return html.escape(text.strip(), quote=True)


def convert_loss_of_ability(value):
    """Convert LossOfAbility value to proper format"""
    conversion = {'y': 'true', 'n': 'false', 'u': 'unknown'}
    return conversion.get(value, 'unknown')


def get_ontology_mappings(owl_tree):
    """Extract Thesaurus OFCO concepts (RDF parsing)"""
    disability_mapping = {}
    orpha_number_mapping = {}
    
    print('\033[96m Extract concepts from OFCO thesaurus...\033[0m')
    root = owl_tree.getroot()
    
    for cls in root.findall('.//owl:Class', NAMESPACES):
        cls_about = cls.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
        if not cls_about:
            continue
        equiv = cls.find('owl:equivalentClass', NAMESPACES)
        if equiv is None:
            continue

        intersection_of = equiv.find('.//owl:intersectionOf', NAMESPACES)
        restrictions = intersection_of.findall('.//owl:Restriction', NAMESPACES) if intersection_of is not None else equiv.findall('.//owl:Restriction', NAMESPACES)

        for restriction in restrictions:
            prop_node = restriction.find('owl:onProperty', NAMESPACES)
            val_node = restriction.find('owl:hasValue', NAMESPACES)
            if prop_node is not None and val_node is not None:
                prop = prop_node.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                val = val_node.text
                if prop == 'https://w3id.org/ofco/hasORPHANETDBInternalReference':
                    disability_mapping[val] = cls_about
                elif prop == 'https://w3id.org/ofco/hasORPHAnumber':
                    orpha_number_mapping[val] = cls_about
    
    print('\033[92m Mappings extracted from OFCO:\033[0m')
    print(f'\033[97m   - Disabilities: {len(disability_mapping)} entries\033[0m')
    print(f'\033[97m   - OrphaNumbers: {len(orpha_number_mapping)} entries\033[0m')
    
    return {
        'Disabilities': disability_mapping,
        'OrphaNumbers': orpha_number_mapping
    }


def main():
    """Main processing function"""
    quiet_mode = "--quiet" in sys.argv

    print('\033[93m Loading OFCO...\033[0m')
    
    try:
        owl_tree = ET.parse(OFCO_FILE)
    except FileNotFoundError:
        print(f'\033[91m Error: {OFCO_FILE} not found\033[0m')
        sys.exit(1)
    
    mappings = get_ontology_mappings(owl_tree)
    
    print('\033[93m Loading XML dataset...\033[0m')
    try:
        xml_tree = ET.parse(XML_FILE)
        xml_root = xml_tree.getroot()
    except FileNotFoundError:
        print(f'\033[91m Error: {XML_FILE} not found\033[0m')
        sys.exit(1)
    
    print('\033[93m RDF generation...\033[0m')
    output_lines = []
    
    output_lines.extend([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rdf:RDF',
        '    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
        '    xmlns:owl="http://www.w3.org/2002/07/owl#"',
        '    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
        '    xmlns:ordo="http://www.orpha.net/ORDO/"',
        '    xmlns:ofco="https://w3id.org/ofco/"',
        '    xmlns:icf="http://id.who.int/icf/"',
        '    xmlns:xsd="http://www.w3.org/2001/XMLSchema#">'
    ])
    
    processed_disorders = 0
    
    for relevance in xml_root.findall('.//DisorderDisabilityRelevance'):
        disorder = relevance.find('Disorder')
        if disorder is None:
            continue
        
        orpha_code_elem = disorder.find('OrphaCode')
        disorder_name_elem = disorder.find("Name[@lang='en']")
        if orpha_code_elem is None or disorder_name_elem is None:
            continue
        
        orpha_code = orpha_code_elem.text
        disorder_name = xml_escape(disorder_name_elem.text)
        
        output_lines.extend([
            '',
            f'  <!-- Disorder: {disorder_name} (Orphanet_{orpha_code}) -->',
            f'  <owl:Class rdf:about="http://www.orpha.net/ORDO/Orphanet_{orpha_code}">'
        ])
        
        # hasSpecificManagement stays on the disorder
        specific_management = relevance.find('SpecificManagement')
        if specific_management is not None and specific_management.text:
            bool_val = 'true' if specific_management.text.lower().startswith('y') else 'false'
            output_lines.append(
                f'    <ofco:hasSpecificManagement rdf:datatype="xsd:boolean">{bool_val}</ofco:hasSpecificManagement>'
            )
        
        # DisabilityCategory (always include if mapped)
        disability_category = relevance.find('DisabilityCategory')
        if disability_category is not None:
            orpha_number_node = disability_category.find('OrphaNumber')
            name_node = disability_category.find("Name[@lang='en']")
            if orpha_number_node is not None and orpha_number_node.text:
                orpha_number = orpha_number_node.text.strip()
                category_uri = mappings['OrphaNumbers'].get(orpha_number)
                if category_uri:
                    output_lines.extend([
                        f'    <!-- Disability category: {xml_escape(name_node.text) if name_node is not None else orpha_number} -->',
                        f'    <ofco:hasDisabilityCategory rdf:resource="{category_uri}"/>'
                    ])
                elif not quiet_mode:
                    print(f'\033[93m Warning: DisabilityCategory OrphaNumber {orpha_number} not found in ontology\033[0m')
        
        # DisabilityDisorderAssociationList - using blank nodes
        associations = disorder.findall('DisabilityDisorderAssociationList/DisabilityDisorderAssociation')
        for association in associations:
            disability = association.find('Disability')
            if disability is None:
                continue
            disability_id = disability.get('id')
            disability_name_elem = disability.find("Name[@lang='en']")
            if disability_name_elem is None:
                continue
            disability_name = xml_escape(disability_name_elem.text)
            
            output_lines.extend([
                '',
                f'    <!-- Disability: {disability_name} -->',
                '    <ofco:hasDisabilityAnnotation rdf:parseType="Resource">',
                '      <rdf:type rdf:resource="https://w3id.org/ofco/DisabilityDisorderAssociation"/>'
            ])
            
            # Check disability URI
            if disability_id in mappings['Disabilities']:
                disability_uri = mappings['Disabilities'][disability_id]
                output_lines.append(f'      <ofco:concernsDisability rdf:resource="{disability_uri}"/>')
            else:
                if not quiet_mode:
                    print(f'\033[93m  Disability ID {disability_id} not found in ontology\033[0m')
            
            # Frequency / Temporality / Severity
            for tag, predicate in [
                ('FrequenceDisability', 'hasFrequency'),
                ('TemporalityDisability', 'hasTemporality'),
                ('SeverityDisability', 'hasSeverity')
            ]:
                elem = association.find(tag)
                if elem is not None and len(elem) > 0:
                    orpha_number_node = elem.find('OrphaNumber')
                    if orpha_number_node is not None and orpha_number_node.text:
                        orpha_number = orpha_number_node.text
                        if orpha_number in mappings['OrphaNumbers']:
                            uri = mappings['OrphaNumbers'][orpha_number]
                            output_lines.append(f'      <ofco:{predicate} rdf:resource="{uri}"/>')
            
            # LossOfAbility
            loss_of_ability = association.find('LossOfAbility')
            if loss_of_ability is not None and loss_of_ability.text:
                loss_value = convert_loss_of_ability(loss_of_ability.text)
                if loss_value in ('true', 'false'):
                    output_lines.append(
                        f'      <ofco:lossOfAbility rdf:datatype="xsd:boolean">{loss_value}</ofco:lossOfAbility>'
                    )
            
            output_lines.append('    </ofco:hasDisabilityAnnotation>')
        
        output_lines.append('  </owl:Class>')
        processed_disorders += 1
    
    output_lines.extend(['', '</rdf:RDF>'])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print('\033[92m\\o/ RDF disabilities conversion done!\033[0m')
    print(f'\033[97m   - Diseases processed: {processed_disorders}\033[0m')
    print(f'\033[97m   - Output file: {OUTPUT_FILE}\033[0m')


if __name__ == '__main__':
    main()