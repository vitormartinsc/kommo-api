# Arquivo renomeado para reactivate_lost_leads.py e movido para a pasta automation.

import os
import requests

# Configurações iniciais
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}
LOSS_STATUS_ID = 143
SEM_CONTATO_LOSS_REASON_ID = 28218043
SALESBOT_ID = 123456  # Substitua pelo ID do salesbot específico

# Adicionando IDs dos status permitidos
LINK_PAGAMENTO_STATUS_ID = 83584915
LINK_CADASTRO_STATUS_ID = 83584911

STATUS_NAMES = {
    83088599: "Incoming leads",
    83088607: "Possui Limite",
    83236763: "Simulação",
    83311583: "PóS - SimulAÇÃO",
    83584911: "LINK CADASTRO",
    83584915: "LINK PAGAMENTO",
    83584919: "TRaNSFERÊNCIA efetuada",
    142: "Venda ganha",
    143: "Venda perdida"
}

# Função para buscar todos os leads perdidos com motivo específico
def buscar_leads_perdidos():
    url = f"{BASE_URL}/api/v4/leads"
    all_leads = []
    page = 1

    while True:
        params = {
            "page": page,
            "limit": 250,
            "filter[statuses][0][pipeline_id]": LOSS_STATUS_ID
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

        # Filtrar os leads pelo motivo de perda "Sem contato"
        leads_filtrados = [
            lead for lead in leads
            if lead.get('loss_reason_id') == SEM_CONTATO_LOSS_REASON_ID
        ]

        all_leads.extend(leads_filtrados)
        page += 1

    return all_leads

# Função para buscar eventos de um lead (ajustada para seguir o padrão correto)
def buscar_eventos_lead(lead_id):
    url = f"{BASE_URL}/api/v4/events"
    all_events = []
    page = 1

    while True:
        params = {
            "filter[entity_id]": lead_id,  # ID do lead
            "filter[entity]": "leads",  # Tipo da entidade (lead)
            "limit": 250,
            'filter[type]': 'lead_status_changed',  # Tipo de evento específico
            "page": page
        }
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 204:  # Sem conteúdo, interrompe o loop
            break
        elif response.status_code != 200:
            print(f"Erro ao buscar eventos do lead {lead_id}: {response.status_code} - {response.text}")
            response.raise_for_status()

        data = response.json()
        events = data.get('_embedded', {}).get('events', [])
        if not events:
            break

        all_events.extend(events)
        page += 1

    return all_events

# Função para ativar o salesbot em um lead
def ativar_salesbot(lead_id):
    url = f"{BASE_URL}/api/v2/salesbot/run"  # Endpoint correto para ativar o Salesbot
    payload = {
        "bot_id": 41994,  # ID do Salesbot
        "entity_id": lead_id,  # ID do lead
        "entity_type": "2"  # Tipo da entidade (2 = lead)
    }
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"Erro ao ativar o salesbot no lead {lead_id}: {response.status_code} - {response.text}")
        response.raise_for_status()

    print(f"Salesbot ativado com sucesso no lead {lead_id}.")
    return response.json()

# Função para adicionar uma tag ao lead
def adicionar_tag_ao_lead(lead_id, tag_id):
    """
    Adiciona uma tag ao lead especificado usando o formato correto da API.
    """
    url = f"{BASE_URL}/api/v4/leads"
    payload = [
        {
            "id": lead_id,
            "_embedded": {
                "tags": [
                    {"id": tag_id}
                ]
            }
        }
    ]
    response = requests.patch(url, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"Erro ao adicionar a tag ao lead {lead_id}: {response.status_code} - {response.text}")
        response.raise_for_status()

    print(f"Tag {tag_id} adicionada com sucesso ao lead {lead_id}.")
    return response.json()

# Função principal
def main():
    print("Buscando leads perdidos com motivo 'Sem contato'...")
    leads = buscar_leads_perdidos()

    print(f"{len(leads)} leads encontrados. Verificando eventos e adicionando tag...")
    for lead in leads:
        lead_id = lead.get('id')
        eventos = buscar_eventos_lead(lead_id)

        if not eventos:
            print(f"Nenhum evento encontrado para o lead {lead_id}. Pulando...")
            continue

        # Pegar o primeiro evento (mais recente)
        ultimo_evento_valido = eventos[0] if eventos[0].get('type') == 'lead_status_changed' and 'value_before' in eventos[0] else None

        if not ultimo_evento_valido:
            print(f"Nenhum evento válido encontrado para o lead {lead_id}. Pulando...")
            continue

        # Verificar o status anterior no evento
        status_anterior_id = ultimo_evento_valido.get('value_before', [{}])[0].get('lead_status', {}).get('id')
        if status_anterior_id in [LINK_PAGAMENTO_STATUS_ID, LINK_CADASTRO_STATUS_ID]:
            adicionar_tag_ao_lead(lead_id, 120582)  # Substitua pelo ID da tag
        else:
            status_anterior_nome = STATUS_NAMES.get(status_anterior_id, "Desconhecido")
            print(f"Lead {lead_id} não possui status anterior permitido. Status anterior: {status_anterior_nome} (ID: {status_anterior_id}). Pulando...")

    print("Processo concluído.")
    
if __name__ == "__main__":
    main()