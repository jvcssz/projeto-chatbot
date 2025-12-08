flowchart TD
    %% Estilos
    classDef user fill:#ffffff,stroke:#333,stroke-width:2px;
    classDef app fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef ai fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef api fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef storage fill:#e2e3e5,stroke:#383d41,stroke-width:2px;

    %% Nós - REMOVI OS PARENTESES PARA EVITAR ERROS
    User([👤 Usuário]):::user
    Interface[💻 App Streamlit - Visual]:::app
    
    subgraph Inteligencia [🧠 Inteligência Artificial]
        GeminiNLP[Gemini 2.5 - Interpretar]:::ai
        GeminiGen[Gemini 2.5 - Gerar]:::ai
    end

    subgraph DadosExternos [☁️ APIs Externas]
        GeoAPI((OpenMeteo - Local)):::api
        WeatherAPI((OpenMeteo - Clima)):::api
    end
    
    Decisao{📍 Local Encontrado?}
    Log[(📂 Arquivo CSV Log)]:::storage

    %% O Fluxo
    User -->|1. Envia Pergunta| Interface
    Interface -->|2. Envia Texto| GeminiNLP
    GeminiNLP -->|3. Retorna Cidade| GeoAPI
    GeoAPI -->|4. Retorna Lat/Lon| Decisao
    
    Decisao -- Sim --> WeatherAPI
    Decisao -- Não --> Interface
    
    WeatherAPI -->|5. Dados de 7 dias| GeminiGen
    GeminiGen -->|6. Resposta Final| Interface
    Interface -.->|7. Salva Log| Log
