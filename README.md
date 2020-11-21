# djbourse

.BAT Example for update of prices (to run each day).
It will download a json file for each stock and add prices in database.

echo off

call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\activate.bat

call python C:\Users\c158492\ProjetPerso\djbourse\update_prices.py --api_key "xxx" --folder_data C:\Users\c158492\ProjetPerso\djbourse\data

call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\deactivate.bat
