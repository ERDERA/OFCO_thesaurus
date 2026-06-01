```mermaid
graph TD
    %% Core Categories
    Root((owl:Thing))
    ActPart[ActivitiesAndParticipation]
    EnvFact[EnvironmentalFactors]
    Edu[Education]
    Learn[Learning]
    Temp[temporality]
    Und[Understanding]
    
    %% Specific Classes examples
    Root --> ActPart
    Root --> EnvFact
    Root --> Edu
    Root --> Learn
    Root --> Temp
    Root --> Und
    
    Edu --> AccHighEdu[AccessingHigherEducation]
    Edu --> AttAdaptSch[AttendingAdaptedSchool]
    Learn --> AcqLang[AcquiringLanguage]
    Temp --> AcqDel[AcquisitionDelay]
    EnvFact --> AirQual[AirQuality]
    Und --> AppKnow[ApplyingKnowledge]

    %% Object Properties
    Root -. "hasPart\ninvolves" .-> Root

    %% Data Properties Mapping
    DataProps[<b>Data Properties</b><br/>hasORPHANETDBInternalReference: integer<br/>hasORPHAnumber: integer]
    Root -.- DataProps
    
    %% External ICF Annotations
    AnnProps[<b>Key Annotation Properties</b><br/>hasICFcode<br/>hasICFuri<br/>hasSeverity<br/>hasFrequency<br/>hasSpecificManagement]
    Root -.- AnnProps
    
    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef rootNode fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef dataNode fill:#fff3e0,stroke:#f57c00,stroke-width:1px,stroke-dasharray: 5 5;
    
    class Root rootNode;
    class DataProps,AnnProps dataNode;
    ```
