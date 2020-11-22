# djbourse

# .BAT Example for prices update (run each day)
It will download a json file for each stock and add prices in database.

echo off

call djbourse\venv\Scripts\activate.bat

call python djbourse\update_prices.py --api_key "xxx" --folder_data djbourse\data

call djbourse\venv\Scripts\deactivate.bat
