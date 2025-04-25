import os
import requests
from datetime import datetime, timedelta
import time

# Configurações iniciais
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
PIPELINE_ID = 10835227
LOSS_STATUS_ID = 143
WIN_STATUS_ID = 142
BASE_URL = 'https://vitorcarvalho.kommo.com'
SEM_CONTATO_LOSS_REASON_ID = 28218043  # ID do motivo de perda "Sem contato"
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Função para buscar todos os contatos com leads associados
def buscar_todos_contatos():
    url = f"{BASE_URL}/api/v4/contacts"
    all_contacts = []
    page = 1

    while True:
        params = {
            "page": page,
            "limit": 250,
            "with": "leads"  # Adiciona informações dos leads associados ao contato
        }
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 204:  # Sem conteúdo, interrompe o loop
            break
        elif response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            response.raise_for_status()

        data = response.json()
        contacts = data.get('_embedded', {}).get('contacts', [])
        if not contacts:
            break

        all_contacts.extend(contacts)
        page += 1

    return all_contacts

# Função para buscar todos os leads com contatos associados
def buscar_todos_leads():
    url = f"{BASE_URL}/api/v4/leads"
    all_leads = []
    page = 1

    while True:
        params = {
            "page": page,
            "limit": 250,
            "with": "contacts"  # Adiciona informações dos contatos associados ao lead
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

# Função para buscar eventos por contato
def buscar_eventos_por_contato(contact_id):
    url = f"{BASE_URL}/api/v4/events"
    all_events = []
    page = 1

    while True:
        params = {
            "filter[entity_id]": contact_id,  # ID do contato
            "filter[entity]": "contacts",  # Tipo da entidade (contato)
            "filter[type]": "outgoing_chat_message",  # Filtrar apenas mensagens enviadas
            "limit": 250,
            "page": page
        }
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 204:  # Sem conteúdo, interrompe o loop
            break
        elif response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            response.raise_for_status()

        data = response.json()
        events = data.get('_embedded', {}).get('events', [])
        if not events:
            break

        all_events.extend(events)
        page += 1

    return all_events

# Função para verificar o último evento do tipo "outgoing_chat_message"
def verificar_ultimo_outgoing_chat(events):
    if not events:
        return False, None

    # Encontrar o evento com o maior "created_at"
    last_event = max(events, key=lambda x: x['created_at'])
    last_event_date = datetime.fromtimestamp(last_event['created_at'])

    # Verificar se o último evento foi há mais de 3 dias
    three_days_ago = datetime.now() - timedelta(days=4)
    if last_event_date < three_days_ago:
        # Extrair o talk_id do campo value_after
        talk_id = None
        value_after = last_event.get('value_after', [])
        if value_after and 'message' in value_after[0]:
            talk_id = value_after[0]['message'].get('talk_id')
        return True, talk_id

    return False, None

# Função para dar perda no lead
def dar_perda_no_lead(lead_id, motivo):
    url = f"{BASE_URL}/api/v4/leads/{lead_id}"
    payload = {
        "pipeline_id": PIPELINE_ID,  # ID do pipeline
        "status_id": LOSS_STATUS_ID,  # Status "Perdido"
        "closed_at": int(time.time()),  # Timestamp do fechamento
        "loss_reason_id": motivo  # ID do motivo de perda
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Erro ao dar perda no lead {lead_id}: {response.status_code} - {response.text}")
        response.raise_for_status()
    print(f"Lead {lead_id} marcado como perdido com sucesso.")
    return response.json()

# Função para fechar a conversa de um contato
def fechar_conversa(talk_id):
    url = f"{BASE_URL}/api/v4/talks/{talk_id}/close"
    payload = {"force_close": True}  # Força o fechamento da conversa
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code != 202:
        print(f"Erro ao fechar a conversa {talk_id}: {response.status_code} - {response.text}")

    print(f"Conversa {talk_id} fechada com sucesso.")
    return response

# Função principal atualizada
def main():
    print("Buscando todos os leads...")
    leads = buscar_todos_leads()

    print("Verificando leads...")
    for lead in leads:
        lead_id = lead.get('id')
        contact_id = lead.get('_embedded', {}).get('contacts', [{}])[0].get('id')  # Pega o primeiro contato associado
        status_id = lead.get('status_id')

        # Verificar se o lead já está no status de perda
        if status_id == LOSS_STATUS_ID:
            print(f"⚠️ Lead {lead_id} já está no status de perda. Nada a fazer.")
            continue
        
        if status_id == WIN_STATUS_ID:
            print(f"⚠️ Lead {lead_id} já está no status de ganho. Nada a fazer.")
            continue

        # Verificar eventos do contato associado
        if contact_id:
            eventos = buscar_eventos_por_contato(contact_id)

            # Verificar o último evento do tipo "outgoing_chat_message"
            is_old_event, talk_id = verificar_ultimo_outgoing_chat(eventos)
            if is_old_event:
                print(f"Dando perda no lead {lead_id} por motivo 'Sem contato'...")
                dar_perda_no_lead(lead_id, SEM_CONTATO_LOSS_REASON_ID)

                # Fechar a conversa associada ao contato
                if talk_id:
                    fechar_conversa(talk_id)
                    
            else:
                print(f"Lead {lead_id} tem contato recente. Não será marcada perda.")

    print("Processo concluído.")

if __name__ == "__main__":
    main()