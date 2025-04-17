import requests
import os

# Configurações da API
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def coletar_todos_contatos():
    """Coleta todos os contatos."""
    url = f"{BASE_URL}/api/v4/contacts"
    params = {"limit": 250}  # Limite máximo por página
    contatos = []

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        contatos.extend(data["_embedded"]["contacts"])  # Adiciona os contatos à lista
        url = data.get("_links", {}).get("next", {}).get("href")  # Próxima página
        params = None  # Limpa os parâmetros para as próximas páginas

    return [contato["id"] for contato in contatos]  # Retorna apenas os IDs dos contatos

def coletar_eventos_por_contato(contact_id):
    """Coleta os eventos associados a um contato."""
    url = f"{BASE_URL}/api/v4/events"
    params = {
        "filter[entity_id]": contact_id,
        "filter[entity]": "contacts",  # Tipo de entidade: contatos
        "limit": 250,  # Limite máximo por página
        "order": "asc"  # Ordena por data crescente
    }
    eventos = []

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        eventos.extend(data["_embedded"]["events"])  # Adiciona os eventos à lista
        url = data.get("_links", {}).get("next", {}).get("href")  # Próxima página
        params = None  # Limpa os parâmetros para as próximas páginas

    return eventos

def coletar_conversa_por_talking_id(talking_id):
    """Coleta a conversa associada a um talking_id."""
    url = f"{BASE_URL}/api/v4/talks/{talking_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# === EXECUÇÃO PRINCIPAL ===
#print("🔄 Coletando todos os contatos...")
#contact_ids = coletar_todos_contatos()
#print(f"📋 IDs dos contatos coletados: {contact_ids}")

#print("🔄 Coletando eventos para cada contato...")
#for contact_id in contact_ids:
#    eventos = coletar_eventos_por_contato(contact_id)
#    print(f"📋 Eventos do contato {contact_id}: {eventos}")

print("🔄 Coletando conversa para o talking_id 1314...")
conversa = coletar_conversa_por_talking_id(1314)
print(f"📋 Conversa coletada: {conversa}")