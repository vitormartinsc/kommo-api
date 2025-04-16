import requests
import os

# === CONFIGURAÇÕES ===
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def coletar_primeira_mensagem(lead_id):
    """Coleta a primeira mensagem de um lead."""
    url = f"{BASE_URL}/api/v4/leads/{lead_id}/notes"
    params = {'limit': 1, 'order': 'asc'}  # Ordena por data crescente para pegar a primeira mensagem
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    notas = resp.json()['_embedded']['notes']
    if notas:
        return notas[0]['params']['text']  # Retorna o texto da primeira mensagem
    return None

def atualizar_campo_lead(lead_id, valor_campo):
    """Atualiza o campo personalizado de um lead."""
    url = f"{BASE_URL}/api/v4/leads"
    payload = {
        "update": [
            {
                "id": lead_id,
                "custom_fields_values": [
                    {
                        "field_id": 1057048,  # ID do campo personalizado
                        "values": [{"value": valor_campo}]
                    }
                ]
            }
        ]
    }
    resp = requests.patch(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    
    
def coletar_todos_leads():
    """Coleta todos os IDs de leads."""
    url = f"{BASE_URL}/api/v4/leads"
    params = {'limit': 250}  # Limite máximo por página
    leads = []

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        leads.extend(data['_embedded']['leads'])  # Adiciona os leads à lista
        url = data.get('_links', {}).get('next', {}).get('href')  # Próxima página
        params = None  # Limpa os parâmetros para as próximas páginas

    return [lead['id'] for lead in leads]  # Retorna apenas os IDs dos leads

# === EXECUÇÃO PRINCIPAL ===
print("🔄 Coletando todos os leads...")
lead_ids = coletar_todos_leads()

print("📌 Processando leads...")
for lead_id in lead_ids:
    try:
        primeira_mensagem = coletar_primeira_mensagem(lead_id)
        if primeira_mensagem:
            if "Vim através do site" in primeira_mensagem:
                atualizar_campo_lead(lead_id, "Google")
            else:
                atualizar_campo_lead(lead_id, "Meta")
    except Exception as e:
        print(f"Erro ao processar lead {lead_id}: {e}")