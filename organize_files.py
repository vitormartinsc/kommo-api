import os
import shutil

# Define the folder structure
folders = {
    "automation": [
        "analisar_leads.py",
        "changing_campaign_origin.py",
        "giving_campaign_origin.py",
        "giving-lost-no-contact.py",
        "giving-lost-no-limit.py",
        "list_loss_reasons.py",
        "reactivating_lost_leads.py",
        "recover-script.py",
        "scraping_leads.py",
        "updating_price_leads.py",
    ],
    "data": [
        "leads_database.csv",
        "equipment_data.csv",
        "entradas_por_etapa_2025-04-01_a_2025-04-10.xlsx",
    ],
    "notebooks": [
        "getting_google_talking_ids.ipynb",
    ],
    "analysis": [
        "data_analysis.R",
        "getting_dashboard_data.py",
    ],
}

# Move files to their respective folders
for folder, files in folders.items():
    if not os.path.exists(folder):
        os.makedirs(folder)
    for file in files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(folder, file))
            print(f"Moved {file} to {folder}/")
        else:
            print(f"File {file} not found.")