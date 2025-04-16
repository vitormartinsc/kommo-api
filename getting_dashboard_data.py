import os
import requests
from datetime import datetime
from collections import Counter
import pandas as pd

# === CONFIGURAÇÃO ===
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}
PIPELINE_ID = 10835227

# === FUNÇÃO: converter data para timestamp
def to_timestamp(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())

# === PARÂMETROS DE FILTRO
DATA_INICIAL = '2024-03-01'
DATA_FINAL = '2024-03-31'
ts_inicial = to_timestamp(DATA_INICIAL)
ts_final = to_timestamp(DATA_FINAL)

# === FUNÇÃO: coletar eventos com paginação
def coletar_eventos_status_changed():
    eventos = []
    url = f"{BASE_URL}/api/v4/events"
    params = {
        'filter[type]': 'lead_status_changed',
        'filter[created_at][from]': ts_inicial,
        'filter[created_at][to]': ts_final,
        'limit': 250
    }

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        eventos.extend(data['_embedded']['events'])
        url = data.get('_links', {}).get('next', {}).get('href')
        params = None  # limpa para próximas páginas

    return eventos

# === FUNÇÃO: obter nome dos status (etapas) da pipeline
def get_status_por_pipeline(pipeline_id):
    url = f"{BASE_URL}/api/v4/leads/pipelines"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()

    pipelines = resp.json()['_embedded']['pipelines']
    for pipeline in pipelines:
        if pipeline['id'] == pipeline_id:
            return {
                status['id']: status['name']
                for status in pipeline['_embedded']['statuses']
            }

    return {}

# === EXECUÇÃO PRINCIPAL ===
print("🔄 Coletando eventos de movimentação...")
eventos = coletar_eventos_status_changed()

print("📌 Carregando etapas do funil...")
mapa_status = get_status_por_pipeline(PIPELINE_ID)

print("📊 Contando entradas por etapa...")
contagem_etapas = Counter()

for event in eventos:
    try:
        etapa_id = event['value_after'][0]['lead_status']['id']
        contagem_etapas[etapa_id] += 1
    except (KeyError, IndexError, TypeError):
        continue

# === ORGANIZAÇÃO EM TABELA
df_resultado = pd.DataFrame(contagem_etapas.items(), columns=['ID_Etapa', 'Quantidade'])
df_resultado['Nome_Etapa'] = df_resultado['ID_Etapa'].map(mapa_status)
df_resultado = df_resultado.sort_values(by='Quantidade', ascending=False)

# === EXPORTAÇÃO
nome_arquivo = f"entradas_por_etapa_{DATA_INICIAL}_a_{DATA_FINAL}.xlsx"
df_resultado.to_excel(nome_arquivo, index=False)

print(f"\n✅ Dados exportados para '{nome_arquivo}'")
print(df_resultado)
