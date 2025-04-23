import os
import requests
from datetime import datetime, timedelta

# Configurações iniciais
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Função para buscar todos os leads com paginação
def buscar_todos_leads():
    url = f"{BASE_URL}/api/v4/leads"
    all_leads = []
    page = 1

    while True:
        params = {"page": page, "limit": 250}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 204:  # Sem conteúdo, interrompe o loop
            break
        elif response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            response.raise_for_status()

        data = response.json()
        leads = data.get('_embedded', {}).get('leads', [])
        if not leads:
            break

        all_leads.extend(leads)
        page += 1

    return all_leads

# Função para verificar a última conversa do lead
def verificar_ultima_conversa(lead):
    last_activity = lead.get('last_activity')
    if not last_activity:
        return False

    last_activity_date = datetime.strptime(last_activity, "%Y-%m-%dT%H:%M:%S%z")
    three_days_ago = datetime.now(last_activity_date.tzinfo) - timedelta(days=3)

    return last_activity_date < three_days_ago

# Função para dar perda no lead
def dar_perda_no_lead(lead_id, motivo):
    url = f"{BASE_URL}/api/v4/leads/{lead_id}"
    payload = {
        "status_id": "lost",
        "loss_reason": motivo
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

# Função principal
def main():
    print("Buscando todos os leads...")
    todos_leads = buscar_todos_leads()

    print("Verificando leads com mais de 3 dias sem contato...")
    for lead in todos_leads:
        lead_id = lead.get('id')
        if verificar_ultima_conversa(lead):
            print(f"Dando perda no lead {lead_id} por motivo 'Sem contato'...")
            dar_perda_no_lead(lead_id, "Sem contato")

    print("Processo concluído.")

if __name__ == "__main__":
    main()