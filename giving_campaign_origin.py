# Este script será usado para gerenciar a origem de campanhas no sistema Kommo.

# Importações necessárias
import requests
import os

# Configurações iniciais
ACCESS_TOKEN = os.getenv('KOMMO_ACCESS_TOKEN')
BASE_URL = 'https://vitorcarvalho.kommo.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}


# Função para buscar o lead ID de cada talking_id
def buscar_lead_id(talking_id):
    url = f"{BASE_URL}/api/v4/talks/{talking_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    # Acessar _embedded, leads e retornar o valor do key id
    leads = data.get('_embedded', {}).get('leads', [])
    if leads:
        return leads[0].get('id')
    raise ValueError("Lead ID não encontrado para o Talking ID fornecido.")


# Função para buscar o lead ID de cada talking_id (Google leads)
def buscar_google_lead_id(talking_id):
    url = f"{BASE_URL}/api/v4/talks/{talking_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    # Acessar _embedded, leads e retornar o valor do key id
    leads = data.get('_embedded', {}).get('leads', [])
    if leads:
        return leads[0].get('id')
    raise ValueError("Lead ID não encontrado para o Talking ID fornecido.")


# Função para buscar todos os lead IDs do Kommo com paginação
def buscar_todos_lead_ids():
    url = f"{BASE_URL}/api/v4/leads"
    all_lead_ids = []
    page = 1

    while True:
        params = {"page": page, "limit": 250}  # Define o limite por página
        response = requests.get(url, headers=HEADERS, params=params)

        # Verificar se a resposta é válida
        if response.status_code == 204:  # Sem conteúdo, interrompe o loop
            break
        elif response.status_code != 200:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
            response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            print(f"Resposta inválida da API: {response.text}")
            raise ValueError("A resposta da API não é um JSON válido.")

        # Extrair os lead IDs da página atual
        leads = data.get('_embedded', {}).get('leads', [])
        if not leads:  # Se não houver mais leads, interrompe o loop
            break

        all_lead_ids.extend([lead.get('id') for lead in leads])
        page += 1  # Avança para a próxima página

    return all_lead_ids


# Função para atualizar um campo personalizado de um lead
def atualizar_campo_personalizado_lead(lead_id, custom_field_id, valor):
    url = f"{BASE_URL}/api/v4/leads/{lead_id}"
    payload = {
        "custom_fields_values": [
            {
                "field_id": custom_field_id,
                "values": [
                    {"value": valor}
                ]
            }
        ]
    }
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


# Loop para processar os talking_ids e atualizar os campos personalizados
def processar_talking_ids(talking_ids, nome_campanha_google, nome_campanha_meta):
    google_lead_ids = []

    # Buscar Google leads e atualizar o campo personalizado para "Google"
    for talking_id in talking_ids:
        try:
            lead_id = buscar_google_lead_id(talking_id)
            google_lead_ids.append(lead_id)
            print(f"Lead ID encontrado para Talking ID {talking_id}: {lead_id}")

            # Atualizar campo personalizado para "Google"
            #resultado_campo = atualizar_campo_personalizado_lead(lead_id, 1057048, nome_campanha_google)
            print(f"Campo personalizado do lead atualizado para 'Google' para Talking ID {talking_id}: {resultado_campo}")

        except Exception as e:
            print(f"Erro ao processar Talking ID {talking_id}: {e}")

    # Buscar todos os leads do Kommo
    try:
        todos_lead_ids = buscar_todos_lead_ids()
        print(f"Todos os Lead IDs do Kommo: {todos_lead_ids}")

        # Identificar Meta leads (os que não estão em google_lead_ids)
        meta_lead_ids = [lead_id for lead_id in todos_lead_ids if lead_id not in google_lead_ids]
        print(f"Meta Lead IDs: {meta_lead_ids}")

        # Atualizar campo personalizado para "Meta"
        for lead_id in meta_lead_ids:
            try:
                resultado_campo = atualizar_campo_personalizado_lead(lead_id, 1057048, nome_campanha_meta)
                print(f"Campo personalizado do lead atualizado para 'Meta' para Lead ID {lead_id}: {resultado_campo}")
            except Exception as e:
                print(f"Erro ao atualizar Lead ID {lead_id} para 'Meta': {e}")

    except Exception as e:
        print(f"Erro ao buscar todos os Lead IDs do Kommo: {e}")


# Exemplo de uso atualizado no main
def main():
    nome_campanha_google = "Google"
    nome_campanha_meta = "Meta"

    # Lista de talking_ids fornecida
    talking_ids = [
        1199, 1216, 1220, 1222, 1223, 1224, 1225, 1251, 1252, 1255,
        1256, 1257, 1264, 1265, 1266, 1272, 1277, 1280, 1283, 1284,
        1285, 1301, 1314, 1321, 1331, 1332, 1345, 1349, 1360, 1365,
        1394, 1403, 1412, 1414, 1418, 1423, 1424, 1427, 1437, 1443,
        1445, 1446, 1449, 1450, 1454, 1458, 1459, 1460, 1462, 1464,
        1468, 1476, 1477, 1478, 1479, 1480, 1482, 1483, 1485, 1486,
        1487, 1488, 1490, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1502
    ]

    processar_talking_ids(talking_ids, nome_campanha_google, nome_campanha_meta)


if __name__ == "__main__":
    main()