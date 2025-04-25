import os
import requests
from datetime import datetime

# Configurações iniciais
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
LOSS_STATUS_ID = 143
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Função para buscar todos os leads

def buscar_todos_leads():
    url = f"{BASE_URL}/api/v4/leads"
    all_leads = []
    page = 1

    while True:
        params = {
            "page": page,
            "limit": 250
        }
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

# Função para atualizar o campo "price" de um lead
def atualizar_preco_lead(lead_id, novo_preco):
    url = f"{BASE_URL}/api/v4/leads/{lead_id}"
    payload = {
        "price": int(novo_preco)
    }
    response = requests.patch(url, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"Erro ao atualizar o preço do lead {lead_id}: {response.status_code} - {response.text}")
        response.raise_for_status()

    print(f"Preço do lead {lead_id} atualizado para {novo_preco} com sucesso.")
    return response.json()

# Função principal
def main():
    print("Buscando todos os leads...")
    leads = buscar_todos_leads()

    print("Atualizando preços dos leads...")
    for lead in leads:
        lead_id = lead.get('id')
        status_id = lead.get('status_id')
        custom_fields = lead.get('custom_fields_values', [])

        # Verificar se o lead não está no status de perda
        if status_id == LOSS_STATUS_ID:
            continue

        # Procurar o valor do campo customizado 1051268
        novo_preco = None
        for field in custom_fields:
            if field.get('field_id') == 1051268:
                novo_preco = field.get('values', [{}])[0].get('value')
                break

        # Atualizar o preço do lead se o valor não for nulo
        if novo_preco is not None:
            atualizar_preco_lead(lead_id, novo_preco)

    print("Processo concluído.")

if __name__ == "__main__":
    main()