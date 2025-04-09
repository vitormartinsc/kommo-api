import requests
import time
import os

# === CONFIGURAÇÃO ===
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')  # Configure como variável de ambiente
BASE_URL = 'https://vitorcarvalho.kommo.com'
STATUS_ID = 83088607  # Etapa "Não possui limite"
LOSS_STATUS_ID = 143
LOSS_REASON_ID = 28218035  # Motivo "Sem limite"

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# === 1. Buscar todos os leads na etapa "Não possui limite" ===
def get_leads_by_status(status_id, limit=250):
    url = f'{BASE_URL}/api/v4/leads'
    leads = []
    page = 1

    while True:
        params = {
            'filter[statuses][0][status_id]': status_id,
            'page': page,
            'limit': limit
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Erro ao buscar leads: {response.status_code} - {response.text}")
            break

        data = response.json()
        batch = data.get('_embedded', {}).get('leads', [])
        leads.extend(batch)

        if len(batch) < limit:
            break
        page += 1

    return leads

# === 2. Dar perda nos leads com motivo "Sem limite" ===
def mark_leads_as_lost(leads, loss_status_id, loss_reason_id):
    for lead in leads:
        lead_id = lead['id']
        pipeline_id = lead['pipeline_id']
        url = f'{BASE_URL}/api/v4/leads/{lead_id}'

        payload = {
            "pipeline_id": pipeline_id,
            "status_id": loss_status_id,
            "closed_at": int(time.time()),
            "loss_reason_id": loss_reason_id
        }

        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code in [200, 202]:
            print(f'✅ Lead {lead_id} marcado como perdido.')
        else:
            print(f'❌ Erro ao atualizar lead {lead_id}: {response.status_code} - {response.text}')

# === EXECUÇÃO ===
if __name__ == "__main__":
    print("🔎 Buscando leads na etapa 'Não possui limite'...")
    leads = get_leads_by_status(STATUS_ID)
    print(f'📋 Total encontrado: {len(leads)} leads.\n')

    if leads:
        print("🚩 Marcando como perdidos com motivo 'Sem limite'...")
        mark_leads_as_lost(leads, LOSS_STATUS_ID, LOSS_REASON_ID)
    else:
        print("⚠️ Nenhum lead encontrado na etapa informada.")
