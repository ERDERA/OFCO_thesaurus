import pandas as pd

input_file = 'data/input/Mapping Orphanet-ICF 1.xlsx'
output_file = 'data/input/mappings_sssom.tsv'

df = pd.read_excel(input_file)

predicate_map = {
    'E': 'skos:exactMatch',
    'BTNT': 'skos:broadMatch',
    'NTBT': 'skos:narrowMatch'
}

def get_subject_label(row):
    for i in range(5):
        val = row.iloc[i]
        if pd.notna(val) and str(val).strip() != '':
            return str(val).strip()
    return ''

sssom_df = pd.DataFrame({
    'subject_id': df.iloc[:,6],
    'subject_label': df.apply(get_subject_label, axis=1),
    'predicate_id': df.iloc[:,7].map(predicate_map).fillna(df.iloc[:,7]),
    'object_id': df.iloc[:,8],
    'mapping_date': '2025-09-03',
    'mapping_type': 'semapv:ManualMappingCuration',
    'author_id': 'orcid.org/0000-0003-4308-6337', # Ana Rath
    'author_label': 'Dr Rami Nadji',
    #'curator_id': 'orcid.org/0009-0006-1234-2915|orcid.org/0000-0001-9773-4008' # pauline lubet | Andra Waagmeester
    #'subject_source': 'http://who.int/icf' or 'icf:icf' or 'icd:icd11' TODO review 
    'subject_source_version': '2025-01'
})
# Add comments ? license ? confidence ?

sssom_df.to_csv(output_file, sep='\t', index=False)
print(f"SSSOM generated in {output_file}")
