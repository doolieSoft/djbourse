# djbourse

# .BAT Example for prices update (run each day)
Create a bat file and put the code below. It will download a json file for each stock with flag **monitored** or **is_favorite** and add prices in database.

```
echo off

call djbourse\venv\Scripts\activate.bat

call python djbourse\update_prices.py --api_key "xxx" --folder_data djbourse\data

call djbourse\venv\Scripts\deactivate.bat
```
Below is an example of the page which show percentage diff by period for all stocks. Stocks can be put in favorite table, in monitored table, or can be set to not monitored.
Each cell has a color depending on level of difference between current price and previous price.

![](images/get_diff_for_all_periods_and_all_stocks.png)
