import requests
import os
from dotenv import load_dotenv

# Configuração inicial
load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
print(ACCESS_TOKEN)
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Função para listar os motivos de perda
def listar_loss_reasons():
    url = f"{BASE_URL}/api/v4/leads/loss_reasons"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erro ao buscar motivos de perda: {response.status_code} - {response.text}")
        return

    data = response.json()
    loss_reasons = data.get('_embedded', {}).get('loss_reasons', [])

    print("Motivos de perda disponíveis:")
    for reason in loss_reasons:
        print(f"ID: {reason['id']}, Nome: {reason['name']}")
        

# Função para listar os status de leads
def listar_lead_statuses():
    url = f"{BASE_URL}/api/v4/leads/pipelines"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erro ao buscar status de leads: {response.status_code} - {response.text}")
        return

    data = response.json()
    pipelines = data.get('_embedded', {}).get('pipelines', [])

    print("Status de leads disponíveis:")
    for pipeline in pipelines:
        print(f"Pipeline: {pipeline['name']}")
        for status in pipeline.get('_embedded', []).get('statuses', []):
            print(f"  ID: {status['id']}, Nome: {status['name']}")
            
def listar_tags_leads():
    """
    Lista todas as tags disponíveis para leads.
    """
    url = f"{BASE_URL}/api/v4/leads/tags"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erro ao listar tags: {response.status_code} - {response.text}")
        response.raise_for_status()

    tags = response.json().get('_embedded', {}).get('tags', [])
    for tag in tags:
        print(f"ID: {tag['id']}, Nome: {tag['name']}")

    return tags

if __name__ == "__main__":
    listar_loss_reasons()
    listar_lead_statuses()
    listar_tags_leads()