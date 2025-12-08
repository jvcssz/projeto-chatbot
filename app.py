import streamlit as st
import google.generativeai as genai
import requests
import csv
import os
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO ---
API_KEY = "INSIRA SUA CHAVE AQUI"

# CONFIGURAÇÃO DE CAMINHO RELATIVO (PORTÁTIL)
# Isto cria uma pasta 'Log' no mesmo local onde este arquivo app.py estiver salvo.
CAMINHO_LOG_DIR = 'Log'
CAMINHO_LOG_ARQUIVO = os.path.join(CAMINHO_LOG_DIR, 'historico_logs.csv')

genai.configure(api_key=API_KEY)
modelo = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.2})

MAPA_CLIMA = {
    0: "Céu limpo", 1: "Claro", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Nevoeiro", 48: "Nevoeiro com geada", 51: "Garoa leve", 53: "Garoa moderada",
    55: "Garoa densa", 56: "Garoa congelante leve", 57: "Garoa congelante densa", 61: "Chuva fraca",
    63: "Chuva moderada", 65: "Chuva forte", 66: "Chuva congelante leve", 67: "Chuva congelante forte",
    71: "Neve fraca", 73: "Neve moderada", 75: "Neve forte", 77: "Grãos de neve",
    80: "Pancadas de chuva leves", 81: "Moderadas", 82: "Violentas",
    85: "Pancadas de neve leves", 86: "Fortes", 95: "Tempestade",
    96: "Tempestade com granizo leve", 99: "Tempestade com granizo forte"
}

# --- FUNÇÕES ---

def registrar_log(msg_usuario, msg_bot, coords, dados_clima):
    # Cria a pasta 'Log' automaticamente se ela não existir
    os.makedirs(CAMINHO_LOG_DIR, exist_ok=True)
    arquivo_existe = os.path.isfile(CAMINHO_LOG_ARQUIVO)
    
    fuso_br = timezone(timedelta(hours=-3))
    timestamp = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")
    hoje_iso = datetime.now(fuso_br).strftime('%Y-%m-%d')
    
    local_str, coords_str = "Desconhecido", "N/A"
    cod_hoje, desc_hoje = "N/A", "N/A"

    if coords:
        coords_str = f"{coords['lat']}, {coords['lon']}"
        local_str = f"{coords['nome_real']} - {coords['estado']}"

    if dados_clima and 'daily' in dados_clima:
        try:
            idx = dados_clima['daily']['time'].index(hoje_iso)
            cod_hoje = dados_clima['daily']['weathercode'][idx]
            desc_hoje = MAPA_CLIMA.get(cod_hoje, "Desconhecido")
        except (ValueError, KeyError): pass

    try:
        with open(CAMINHO_LOG_ARQUIVO, mode='a', newline='', encoding='utf-8-sig') as f:
            escritor = csv.writer(f, delimiter=';')
            if not arquivo_existe:
                escritor.writerow(['Data', 'Usuario', 'Bot', 'Local', 'Coords', 'Cod', 'Desc'])
            escritor.writerow([timestamp, msg_usuario, msg_bot, local_str, coords_str, cod_hoje, desc_hoje])
    except Exception: pass

def extrair_dados_dia(dados, data_str):
    try:
        idx = dados['daily']['time'].index(data_str)
        d = dados['daily']
        condicao = MAPA_CLIMA.get(d['weathercode'][idx], f"Cód {d['weathercode'][idx]}")
        return (f"Max {d['temperature_2m_max'][idx]}°C / Min {d['temperature_2m_min'][idx]}°C. "
                f"Precip: {d['precipitation_sum'][idx]}mm. Cond: {condicao}.")
    except (ValueError, KeyError): return "N/A"

def resumir_chuva(dados_horarios, data_str):
    if not dados_horarios: return "Sem dados."
    tempos, precip = dados_horarios.get('time', []), dados_horarios.get('precipitation', [])
    chuva = []
    for t, p in zip(tempos, precip):
        if data_str in t and p > 0:
            intensidade = "fraca" if p <= 2.5 else "moderada" if p <= 7.6 else "forte"
            chuva.append(f"{t.split('T')[1]} ({intensidade})")
    return "Horários de chuva: " + ", ".join(chuva) if chuva else "Sem chuva prevista."

def obter_previsao(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
           f"&hourly=precipitation&forecast_days=5&past_days=2&timezone=America%2FSao_Paulo")
    try:
        resp = requests.get(url)
        return resp.json() if resp.status_code == 200 else None
    except: return None

def obter_coordenadas(nome_local):
    termo, filtro = nome_local, None
    if "," in nome_local:
        termo, filtro = map(str.strip, nome_local.split(",", 1))
    
    try:
        resp = requests.get("https://geocoding-api.open-meteo.com/v1/search", 
                            params={"name": termo, "count": 5, "language": "pt", "format": "json"})
        if resp.status_code == 200 and 'results' in resp.json():
            resultados = resp.json()['results']
            for item in resultados:
                estado = item.get('admin1', '') or item.get('country', '') or ''
                if filtro and filtro.lower() in estado.lower():
                    return {"lat": item['latitude'], "lon": item['longitude'], "nome_real": item['name'], "estado": estado}
            primeiro = resultados[0]
            return {"lat": primeiro['latitude'], "lon": primeiro['longitude'], "nome_real": primeiro['name'], "estado": primeiro.get('admin1', '')}
    except: pass
    return None

def extrair_local_nlp(texto):
    try:
        prompt = f"""Extraia local (Bairro, Cidade) de: "{texto}". Apenas o local ou 'Nenhuma'."""
        return modelo.generate_content(prompt).text.strip().replace('"', '').replace('.', '')
    except: return "Nenhuma"

def gerar_resposta_nlp(entrada_usuario, dados_clima, info_local):
    fuso = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso)
    
    # --- AQUI ESTAVA O ERRO ---
    # Certifique-se que todas as linhas terminam com aspas e vírgula
    datas_mapa = {
        (agora - timedelta(days=2)).strftime('%Y-%m-%d'): "[ANTES DE ONTEM]",
        (agora - timedelta(days=1)).strftime('%Y-%m-%d'): "[ONTEM]",
        agora.strftime('%Y-%m-%d'): "[HOJE]",
        (agora + timedelta(days=1)).strftime('%Y-%m-%d'): "[AMANHÃ]",
        (agora + timedelta(days=2)).strftime('%Y-%m-%d'): "[DEPOIS DE AMANHÃ]"
    }
    
    linhas_previsao = []
    if dados_clima.get('daily'):
        for d in dados_clima['daily']['time']:
            if d in datas_mapa:
                info = extrair_dados_dia(dados_clima, d)
                linhas_previsao.append(f"{datas_mapa[d]} {d}: {info}")

    relatorio_completo = "\n".join(linhas_previsao)
    chuva_hoje = resumir_chuva(dados_clima.get('hourly', {}), agora.strftime('%Y-%m-%d'))
    
    local_formatado = info_local['nome_real']
    if info_local['nome_real'].lower() != info_local['estado'].lower():
        local_formatado += f", em {info_local['estado']}"

    prompt = f"""
    Atue como sistema meteorológico OBJETIVO.
    Input: "{entrada_usuario}" | Local: "{local_formatado}" | Hoje: {agora.strftime('%Y-%m-%d')}
    Dados:
    {relatorio_completo}
    - Chuva Hoje: {chuva_hoje}
    
    REGRAS:
    1. Zero saudações ou frases de enchimento.
    2. Comece frases DIRETAMENTE com DATA ou LOCAL.
    3. Texto corrido e jornalístico.
    """
    return modelo.generate_content(prompt).text

# --- APP STREAMLIT ---

st.set_page_config(page_title="Chatbot Meteorológico", page_icon="🌦️")
st.title("🌦️ Chatbot Meteorológico")

if "messages" not in st.session_state: st.session_state.messages = []
if "contexto_local" not in st.session_state: st.session_state.contexto_local = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if entrada := st.chat_input("Digite sua pergunta..."):
    st.chat_message("user").markdown(entrada)
    st.session_state.messages.append({"role": "user", "content": entrada})

    local_detectado = extrair_local_nlp(entrada)
    coords = None
    resposta = ""

    if local_detectado and local_detectado != "Nenhuma":
        coords = obter_coordenadas(local_detectado)
        if coords: st.session_state.contexto_local = coords
        else: resposta = f"Local '{local_detectado}' não encontrado."
    elif st.session_state.contexto_local:
        coords = st.session_state.contexto_local
    else:
        resposta = "Informe o local."

    if coords and not resposta:
        with st.spinner('...'):
            dados = obter_previsao(coords['lat'], coords['lon'])
            if dados:
                resposta = gerar_resposta_nlp(entrada, dados, coords)
                registrar_log(entrada, resposta, coords, dados)
            else:
                resposta = "Erro na API."

    st.chat_message("assistant").markdown(resposta)
    st.session_state.messages.append({"role": "assistant", "content": resposta})