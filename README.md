# Kommo API Project

## Project Overview
This project contains scripts and data for managing and analyzing leads using the Kommo API. It includes automation scripts, data analysis tools, and Jupyter notebooks for experimentation.

## Folder Structure
- `automation/`: Scripts for automating tasks such as reactivating leads, updating prices, and managing campaigns.
- `data/`: Contains data files like `.csv` and `.xlsx` used in the project.
- `notebooks/`: Jupyter notebooks for analysis and experimentation.
- `analysis/`: Scripts for data analysis and reporting.

## How to Use
1. Set up the environment by creating a `.env` file with the required API keys and configurations.
2. Run the desired script from the appropriate folder.
3. Refer to individual script comments for specific usage instructions.

## Scripts Overview
- `automation/analyze_leads.py`: Fetches and analyzes leads from the Kommo API.
- `automation/reactivate_lost_leads.py`: Reactivates lost leads based on specific criteria.
- `automation/update_price_leads.py`: Updates the price field for leads.
- `analysis/get_dashboard_data.py`: Collects and processes data for dashboard reporting.
- `notebooks/get_google_talking_ids.ipynb`: Jupyter notebook for working with Google talking IDs.

## Requirements
- Python 3.x
- Required libraries: `requests`, `pandas`, `dotenv`

## Setup
1. Install the required libraries using `pip install -r requirements.txt`.
2. Ensure the `.env` file is correctly configured with your Kommo API access token.

## License
This project is licensed under the MIT License.