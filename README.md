# djbourse

This django app helps me monitor some stocks. It is using [AlphaVantage](https://rapidapi.com/alphavantage/api/alpha-vantage) API to get prices history for monitored stocks. It needs an api_key from AlphaVantage. When you have it, you can add it to the table AlphaVantageApiKey via django admin. If you use the batch file below, you have to put the api_key as parameter in order to update prices.

## .BAT Example for prices update (run each day)
I have created a scheduled task running this batch file each day. It downloads json files for each stocks having the flag **monitored** or **is_favorite** set. It adds open and close prices to database. If task has not run for one or several days, it automatically adds the prices that are not in the database.

```
echo off

call djbourse\venv\Scripts\activate.bat
call python djbourse\update_prices.py --api_key "xxx" --folder_data djbourse\data
call djbourse\venv\Scripts\deactivate.bat
```
Below is an example of the page which show percentage diff by period for all stocks. Stocks can be put in *favorite table*, in *monitored table*, or in *not monitored table*.
Each cell has a color depending on level of difference between current price and previous price.

![](images/get_diff_for_all_periods_and_all_stocks.png)
![](images/actions_non_suivies.png)

Some improvement to be done : 
* showing a flag in cell for stocks that have been splitted (AAPL in picture above)
* Manage wallet and make some report on performance
* Manage transactions
