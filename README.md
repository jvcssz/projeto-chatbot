flowchart TD
    %% Estilos
    classDef user fill:#ffffff,stroke:#333,stroke-width:2px;
    classDef app fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef ai fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef api fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef storage fill:#e2e3e5,stroke:#383d41,stroke-width:2px;

    %% Nós (REPARA NAS ASPAS ABAIXO)
    User([👤 Usuário]):::user
    Interface["💻 App Streamlit\n(Interface Visual)"]:::app
    
    subgraph Inteligencia ["🧠 Inteligência Artificial"]
        GeminiNLP["Gemini 2.5\n(Interpretar Texto)"]:::ai
        GeminiGen["Gemini 2.5\n(Gerar Resposta)"]:::ai
    end

    subgraph DadosExternos ["☁️ APIs Externas"]
        GeoAPI(("Open-Meteo\n(Geolocalização)")):::api
        WeatherAPI(("Open-Meteo\n(Previsão)")):::api
    end
    
    Decisao{"📍 Local\nEncontrado?"}
    Log[("📂 Arquivo CSV\n(Histórico)")]:::storage

    %% O Fluxo
    User -->|1. Envia Pergunta| Interface
    Interface -->|2. Envia Texto| GeminiNLP
    GeminiNLP -->|3. Retorna 'Cidade'| GeoAPI
    GeoAPI -->|4. Retorna Lat/Lon| Decisao
    
    Decisao -- Sim --> WeatherAPI
    Decisao -- Não --> Interface
    
    WeatherAPI -->|5. Dados Brutos (7 dias)| GeminiGen
    GeminiGen -->|6. Resposta Final| Interface
    Interface -.->|7. Salva Log| Log