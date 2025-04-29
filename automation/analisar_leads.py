import requests
import pandas as pd
import os
from datetime import datetime

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

# Função para buscar os nomes dos status do funil
def buscar_statuses():
    url = f"{BASE_URL}/api/v4/leads/pipelines"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    # Criar um dicionário com o ID do status como chave e o nome como valor
    statuses = {}
    pipelines = data.get('_embedded', {}).get('pipelines', [])
    for pipeline in pipelines:
        for status in pipeline.get('_embedded', {}).get('statuses', []):
            statuses[status['id']] = status['name']

    return statuses

# Função para filtrar leads a partir de uma data
def filtrar_leads_por_data(leads, data_inicio):
    data_inicio_timestamp = int(datetime.strptime(data_inicio, "%Y-%m-%d").timestamp())
    return [lead for lead in leads if lead.get('created_at', 0) >= data_inicio_timestamp]

# Função para montar o banco de dados com o status do lead
def montar_banco_de_dados(leads, statuses):
    dados = []
    for lead in leads:
        lead_id = lead.get('id')
        custom_fields = lead.get('custom_fields_values', [])
        valor_campo_1057048 = None

        for field in custom_fields:
            if field.get('field_id') == 1057048:
                valor_campo_1057048 = field.get('values', [{}])[0].get('value')
                break

        # Obter o ID do status e buscar o nome do status no dicionário
        status_id = lead.get('status_id')
        nome_status = statuses.get(status_id, "Desconhecido")

        dados.append({
            'lead_id': lead_id,
            'custom_field_1057048': valor_campo_1057048,
            'status': nome_status
        })

    return pd.DataFrame(dados)

# Função principal
def main():
    data_inicio = "2025-04-07"

    print("Buscando todos os leads...")
    todos_leads = buscar_todos_leads()

    print("Buscando nomes dos status...")
    statuses = buscar_statuses()

    print(f"Filtrando leads a partir da data {data_inicio}...")
    leads_filtrados = filtrar_leads_por_data(todos_leads, data_inicio)

    print("Montando banco de dados...")
    banco_de_dados = montar_banco_de_dados(leads_filtrados, statuses)

    print("Salvando banco de dados em 'leads_database.csv'...")
    banco_de_dados.to_csv('leads_database.csv', index=False)

    print("Análise concluída. Banco de dados salvo com sucesso.")

if __name__ == "__main__":
    main()