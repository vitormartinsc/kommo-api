import requests
import time
from datetime import datetime
import os

# === CONFIGURAÇÕES ===
BASE_URL = 'https://vitorcarvalho.kommo.com'
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')  # Defina a variável de ambiente com seu token
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}
PERDA_STATUS_ID = 143
NAO_POSSUI_LIMITE_ID = 83088611

# === 1. Buscar leads encerrados hoje com status de perda ===
def get_lost_leads_closed_today():
    today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    url = f'{BASE_URL}/api/v4/leads'

    all_leads = []
    page = 1
    per_page = 250

    while True:
        params = {
            'filter[closed_at][from]': today_start,
            'filter[statuses][0][status_id]': PERDA_STATUS_ID,
            'page': page,
            'limit': per_page
        }

        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"❌ Erro ao buscar leads (página {page}): {response.status_code} - {response.text}")
            break

        data = response.json().get('_embedded', {}).get('leads', [])
        if not data:
            break

        all_leads.extend(data)

        if len(data) < per_page:
            break  # última página

        page += 1

    return all_leads


# === 2. Obter o último status válido (diferente de 83088607) antes da perda ===
def get_previous_valid_status(lead_id):
    url = f"{BASE_URL}/api/v4/events"
    params = {
        "filter[entity]": "leads",
        "filter[entity_id]": lead_id,
        "filter[type]": "lead_status_changed",
        "order": "created_at"
    }

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"❌ Erro ao buscar eventos do lead {lead_id}: {response.status_code} - {response.text}")
        return None

    events = response.json().get('_embedded', {}).get('events', [])
    if not events:
        print(f"⚠️ Nenhum evento de status encontrado para lead {lead_id}.")
        return None

    last_event = events[0]
    try:
        before = last_event['value_before'][0]['lead_status']
        status_id = before['id']
        pipeline_id = before['pipeline_id']
    except (IndexError, KeyError, TypeError):
        print(f"❌ Estrutura inesperada no evento do lead {lead_id}.")
        return None

    if status_id == NAO_POSSUI_LIMITE_ID:
        print(f"🚫 Lead {lead_id} estava na etapa 'Não Possui Limite' — não será restaurado.")
        return None

    return {
        "status_id": status_id,
        "pipeline_id": pipeline_id
    }

# === 3. Restaurar o lead com o status e pipeline anteriores ===
def reopen_lead(lead, previous):
    lead_id = lead['id']
    status_id = previous['status_id']
    pipeline_id = previous['pipeline_id']

    url = f"{BASE_URL}/api/v4/leads/{lead_id}"
    payload = {
        "pipeline_id": pipeline_id,
        "status_id": status_id,
        "closed_at": None,
        "loss_reason_id": None
    }

    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 202]:
        print(f"✅ Lead {lead_id} restaurado para status {status_id}.")
    else:
        print(f"❌ Erro ao restaurar lead {lead_id}: {response.status_code} - {response.text}")

# === 4. Execução principal ===
if __name__ == "__main__":
    print("🔎 Buscando leads encerrados hoje com status de perda...")
    leads = get_lost_leads_closed_today()
    print(f"📋 {len(leads)} leads encontrados.\n")

    for lead in leads:
        lead_id = lead['id']
        previous = get_previous_valid_status(lead_id)

        if previous:
            reopen_lead(lead, previous)
        else:
            print(f"⚠️ Lead {lead_id} ignorado (sem status anterior restaurável).\n")
