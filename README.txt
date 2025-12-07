
Este projeto é um assistente virtual que utiliza a API do Open-Meteo e a inteligência do Google Gemini para fornecer previsões do tempo detalhadas e objetivas.

## Pré-requisitos
Certifique-se de ter o Python instalado.

## Instalação
1. Abra o terminal na pasta do projeto.
2. Instale as dependências
   pip install -r requisitos.txt

## Como Executar
No terminal, execute o comando
streamlit run app.py

## Funcionalidades
- Histórico de conversa.
- Análise de dados de até 5 dias (incluindo antes de ontem).
- Log automático das conversas em arquivo CSV local.


flowchart TD
    %% Estilos (Cores para diferenciar as etapas)
    classDef user fill:#ffffff,stroke:#333,stroke-width:2px;
    classDef app fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef ai fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef api fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef storage fill:#e2e3e5,stroke:#383d41,stroke-width:2px;

    %% Nós (Os passos do processo)
    User([👤 Usuário]):::user
    Interface[💻 Streamlit App\n(Frontend)]:::app
    
    subgraph Inteligencia ["🧠 Processamento Inteligente"]
        GeminiNLP[Gemini 2.5 Flash\n(Extrair Local)]:::ai
        GeminiGen[Gemini 2.5 Flash\n(Gerar Resposta)]:::ai
    end

    subgraph DadosExternos ["☁️ APIs Externas"]
        GeoAPI((Open-Meteo\nGeocoding)):::api
        WeatherAPI((Open-Meteo\nForecast)):::api
    end
    
    Decisao{📍 Local\nEncontrado?}
    Log[(📂 Log CSV)]:::storage

    %% O Fluxo (As setas)
    User -->|1. Pergunta| Interface
    Interface -->|2. Envia Texto| GeminiNLP
    GeminiNLP -->|3. Retorna 'Cidade'| GeoAPI
    GeoAPI -->|4. Retorna Lat/Lon| Decisao
    
    Decisao -- Sim --> WeatherAPI
    Decisao -- Não --> Interface
    
    WeatherAPI -->|5. Dados Brutos (7 dias)| GeminiGen
    GeminiGen -->|6. Resposta Jornalística| Interface
    Interface -.->|7. Salva Histórico| Log