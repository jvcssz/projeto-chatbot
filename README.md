# Chatbot Meteorológico com IA



Este projeto é um assistente virtual que utiliza a API do Open-Meteo e a inteligência do Google Gemini para fornecer previsões do tempo detalhadas e objetivas.



## Pré-requisitos

Certifique-se de ter o Python instalado.



## Instalação

1. Abra o terminal na pasta do projeto.

2. Instale as dependências:

   pip install -r requirements.txt



## Como Executar

No terminal, execute o comando:

streamlit run app.py



## Funcionalidades

- Histórico de conversa.

- Análise de dados de até 5 dias (incluindo "antes de ontem").

- Log automático das conversas em arquivo CSV local.

```mermaid
flowchart TD
    %% Estilos
    classDef user fill:#ffffff,stroke:#333,stroke-width:2px;
    classDef app fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef ai fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef api fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef storage fill:#e2e3e5,stroke:#383d41,stroke-width:2px;

    %% Nós
    User([Usuario]):::user
    Interface[App Streamlit Visual]:::app
    
    subgraph Inteligencia [Inteligencia Artificial]
        GeminiNLP[Gemini Interpretar Texto]:::ai
        GeminiGen[Gemini Gerar Resposta]:::ai
    end

    subgraph DadosExternos [APIs Externas]
        GeoAPI((OpenMeteo Localizacao)):::api
        WeatherAPI((OpenMeteo Previsao)):::api
    end
    
    Decisao{Local Encontrado?}
    Log[(Arquivo CSV Historico)]:::storage

    %% Fluxo
    User -->|1. Envia Pergunta| Interface
    Interface -->|2. Envia Texto| GeminiNLP
    GeminiNLP -->|3. Retorna Cidade| GeoAPI
    GeoAPI -->|4. Retorna Coordenadas| Decisao
    
    Decisao -- Sim --> WeatherAPI
    Decisao -- Nao --> Interface
    
    WeatherAPI -->|5. Dados de 7 dias| GeminiGen
    GeminiGen -->|6. Resposta Final| Interface
    Interface -.->|7. Salva Log| Log

