
echo off
call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\activate.bat

call python C:\Users\c158492\ProjetPerso\djbourse\update_prices.py --api_key "xxx" --folder_data C:\Users\c158492\ProjetPerso\djbourse\data
call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\deactivate.bat