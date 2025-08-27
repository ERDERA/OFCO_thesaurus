# dummy XML disabilities parser mixed with OFCO thesaurus
# Auteur: Marc Hanauer @Orphanet
# powershell. windows 11
# Date: 2025
# PYTHON VERSION WILL BE DONE

# todo : add files as arguments instead full path
$ofcoFile   = 'G:\Mon Drive\ORPHANET\ERDERA\thesaurus owl\scripts\OFCO_thesaurus.owl'
$xmlFile    = 'G:\Mon Drive\ORPHANET\ERDERA\thesaurus owl\scripts\Disability_adapted_ontology.xml'
$outputFile = 'G:\Mon Drive\ORPHANET\ERDERA\thesaurus owl\scripts\Diseases_annotated_with_OFCO.owl'

Write-Host '🔄 loading OFCO...' -ForegroundColor Yellow

# load ofco. utf8 (need to check that actually)
[xml]$owl = Get-Content $ofcoFile -Encoding UTF8

# XmlNamespaceManager
$nsManager = New-Object System.Xml.XmlNamespaceManager($owl.NameTable)
$nsManager.AddNamespace('rdf',  'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
$nsManager.AddNamespace('owl',  'http://www.w3.org/2002/07/owl#')
$nsManager.AddNamespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
$nsManager.AddNamespace('ofco', 'https://w3id.org/ofco/')
$nsManager.AddNamespace('xsd',  'http://www.w3.org/2001/XMLSchema#')

# Extract Thesaurus OFCO concepts (RDF parsing)
function Get-OntologyMappings {
    param($owlDoc, $nsManager)
    
    $disabilityMapping  = @{}
    $orphaNumberMapping = @{}
    
    Write-Host '🔍 Extract concepts from OFCO thesaurus...' -ForegroundColor Cyan
    
    foreach ($cls in $owlDoc.SelectNodes('//owl:Class', $nsManager)) {
        $clsAbout = $cls.GetAttribute('about', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        if ($clsAbout) {
            $equiv = $cls.SelectSingleNode('owl:equivalentClass', $nsManager)
            if ($equiv) {
                $intersectionOf = $equiv.SelectSingleNode('.//owl:intersectionOf', $nsManager)
                if ($intersectionOf) {
                    $restrictions = $intersectionOf.SelectNodes('.//owl:Restriction', $nsManager)
                } else {
                    $restrictions = $equiv.SelectNodes('.//owl:Restriction', $nsManager)
                }
                foreach ($restriction in $restrictions) {
                    $propNode = $restriction.SelectSingleNode('owl:onProperty', $nsManager)
                    $valNode  = $restriction.SelectSingleNode('owl:hasValue',  $nsManager)
                    if ($propNode -and $valNode) {
                        $prop = $propNode.GetAttribute('resource', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
                        $val  = $valNode.InnerText
                        if ($prop -eq 'https://w3id.org/ofco#hasORPHANETDBInternalReference') {
                            $disabilityMapping[$val] = $clsAbout
                        }
                        elseif ($prop -eq 'https://w3id.org/ofco/hasORPHAnumber') {
                            $orphaNumberMapping[$val] = $clsAbout
                        }
                    }
                }
            }
        }
    }
    
    Write-Host '✅ Mappings extracted from OFCO :' -ForegroundColor Green
    Write-Host ('   - Disabilities: ' + $disabilityMapping.Count + ' entries') -ForegroundColor White
    Write-Host ('   - OrphaNumbers: ' + $orphaNumberMapping.Count + ' entries') -ForegroundColor White
    
    return @{
        'Disabilities' = $disabilityMapping
        'OrphaNumbers' = $orphaNumberMapping
    }
}

# DisabilitiesXML parsing
$mappings = Get-OntologyMappings $owl $nsManager

Write-Host '🔄 loading XML dataset...' -ForegroundColor Yellow

# load XML
[xml]$xmlData = Get-Content $xmlFile -Encoding UTF8

# convert LossOfAbility
function Convert-LossOfAbility {
    param($value)
    switch ($value) {
        'y' { return 'true' }
        'n' { return 'false' }
        'u' { return 'unknown' }
        default { return 'unknown' }
    }
}

Write-Host '🔄 RDF generation...' -ForegroundColor Yellow

# RDF output
$output = New-Object System.Collections.ArrayList

# headers RDF/XML
[void]$output.Add('<?xml version="1.0" encoding="UTF-8"?>')
[void]$output.Add('<rdf:RDF')
[void]$output.Add('    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"')
[void]$output.Add('    xmlns:owl="http://www.w3.org/2002/07/owl#"')
[void]$output.Add('    xmlns:ordo="http://www.orpha.net/ORDO/"')
[void]$output.Add('    xmlns:ofco="https://w3id.org/ofco/"')
[void]$output.Add('    xmlns:icf="http://id.who.int/icf/"')
[void]$output.Add('    xmlns:xsd="http://www.w3.org/2001/XMLSchema#">')

$processedDisorders = 0

# parsing DisorderDisabilityRelevance
foreach ($relevance in $xmlData.SelectNodes('//DisorderDisabilityRelevance')) {
    $disorder = $relevance.SelectSingleNode('Disorder')
    if ($disorder) {
        $orphaCode    = $disorder.SelectSingleNode('OrphaCode').InnerText
        $disorderName = $disorder.SelectSingleNode('Name[@lang="en"]').InnerText
        
        [void]$output.Add('')
        [void]$output.Add('  <!-- Disorder: ' + $disorderName + ' (Orphanet_' + $orphaCode + ') -->')
        [void]$output.Add('  <owl:Class rdf:about="http://www.orpha.net/ORDO/Orphanet_' + $orphaCode + '">')
        
        $associations = $disorder.SelectNodes('DisabilityDisorderAssociationList/DisabilityDisorderAssociation')
        foreach ($association in $associations) {
            $disability = $association.SelectSingleNode('Disability')
            if ($disability) {
                $disabilityId   = $disability.GetAttribute('id')
                $disabilityName = $disability.SelectSingleNode('Name[@lang="en"]').InnerText
                
                [void]$output.Add('')
                [void]$output.Add('    <!-- Disability: ' + $disabilityName + ' -->')
                [void]$output.Add('    <ofco:hasDisabilityAnnotation rdf:parseType="Resource">')
                
                if ($mappings.Disabilities.ContainsKey($disabilityId)) {
                    $disabilityUri = $mappings.Disabilities[$disabilityId]
                    [void]$output.Add('      <ofco:concernsDisability rdf:resource="' + $disabilityUri + '"/>')
                } else {
                    Write-Warning ('⚠️  Disability ID ' + $disabilityId + ' non trouvée dans l''ontologie')
                }
                
                # Frequency
                $frequency = $association.SelectSingleNode('FrequenceDisability')
                if ($frequency -and $frequency.HasChildNodes) {
                    $orphaNumberNode = $frequency.SelectSingleNode('OrphaNumber')
                    if ($orphaNumberNode) {
                        $orphaNumber = $orphaNumberNode.InnerText
                        if ($mappings.OrphaNumbers.ContainsKey($orphaNumber)) {
                            $frequencyUri = $mappings.OrphaNumbers[$orphaNumber]
                            [void]$output.Add('      <ofco:hasFrequency rdf:resource="' + $frequencyUri + '"/>')
                        }
                    }
                }
                
                # Temporality
                $temporality = $association.SelectSingleNode('TemporalityDisability')
                if ($temporality -and $temporality.HasChildNodes) {
                    $orphaNumberNode = $temporality.SelectSingleNode('OrphaNumber')
                    if ($orphaNumberNode) {
                        $orphaNumber = $orphaNumberNode.InnerText
                        if ($mappings.OrphaNumbers.ContainsKey($orphaNumber)) {
                            $temporalityUri = $mappings.OrphaNumbers[$orphaNumber]
                            [void]$output.Add('      <ofco:hasTemporality rdf:resource="' + $temporalityUri + '"/>')
                        }
                    }
                }
                
                # Severity
                $severity = $association.SelectSingleNode('SeverityDisability')
                if ($severity -and $severity.HasChildNodes) {
                    $orphaNumberNode = $severity.SelectSingleNode('OrphaNumber')
                    if ($orphaNumberNode) {
                        $orphaNumber = $orphaNumberNode.InnerText
                        if ($mappings.OrphaNumbers.ContainsKey($orphaNumber)) {
                            $severityUri = $mappings.OrphaNumbers[$orphaNumber]
                            [void]$output.Add('      <ofco:hasSeverity rdf:resource="' + $severityUri + '"/>')
                        }
                    }
                }
                
                # Loss of Ability
                $lossOfAbility = $association.SelectSingleNode('LossOfAbility')
                if ($lossOfAbility) {
                    $lossValue = Convert-LossOfAbility $lossOfAbility.InnerText
                    if ($lossValue -eq 'true' -or $lossValue -eq 'false') {
                        [void]$output.Add('      <ofco:lossOfAbility rdf:datatype="xsd:boolean">' + $lossValue + '</ofco:lossOfAbility>')
                    } else {
                        [void]$output.Add('      <ofco:lossOfAbility>' + $lossValue + '</ofco:lossOfAbility>')
                    }
                }
                
                [void]$output.Add('    </ofco:hasDisabilityAnnotation>')
            }
        }
        
        [void]$output.Add('  </owl:Class>')
        $processedDisorders++
    }
}

[void]$output.Add('')
[void]$output.Add('</rdf:RDF>')

# Output file
$output | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host '✅ RDF disabilities conversion done !' -ForegroundColor Green
Write-Host ('   - Diseases done: ' + $processedDisorders) -ForegroundColor White
Write-Host ('   - Output file: ' + $outputFile) -ForegroundColor White

# result sampling display
Write-Host '📄 show results (few first lines):' -ForegroundColor Cyan
Get-Content $outputFile -TotalCount 20 | ForEach-Object { Write-Host ('   ' + $_) -ForegroundColor Gray }
