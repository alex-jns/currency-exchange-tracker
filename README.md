# Currency Exchange Tracker

A CLI currency exchange tracker made in Python that uses the [Frankfurter API](https://frankfurter.dev/).

## Features

- View the latest available exchange rates.
- Look up rates between supported currencies.
- Cache downloaded rates in a local SQLite database.
- Plot historical exchange rates over a selected date range using pandas and matplotlib.

## Requirements

- Python 3.10 or newer
- An internet connection to download uncached data via API

## Setup

From the project folder, create a virtual environment:

```powershell
python -m venv .venv
```

Install the dependencies into that environment:

```powershell
.\.venv\Scripts\python.exe -m pip install requests sqlalchemy pandas matplotlib
```

## Usage

Start the application:

```powershell
.\.venv\Scripts\python.exe main.py
```

The main menu provides three options:

```text
Currency Exchange Tracker
1. Show today's exchange rates
2. Show a graph of exchange rates over time
3. Exit
```

### Exchange Rates

- Enter a base and quote currency using codes such as `USD`, `EUR`, or `GBP`.
- Leave the base input blank to display all cached rates.
- Enter `exit` at a currency prompt to return to the menu.

Each rate represents the amount of the quote currency equal to one unit of the base currency.

### Historical Graphs

Enter a base currency, quote currency, and date range.

Dates must use `YYYY-MM-DD` format, such as `2026-09-01`.
Future dates are rejected, and the end date cannot precede the start date.

Close the graph window to return to the CLI.

## How It Works

Latest rate lookups use locally cached USD-based rates. Rates between
other currencies are calculated from those reference rates.

Historical graphs request the chosen currency pair and date range
directly from the API, then use pandas and Matplotlib to display the results.

The database stores both the API's rate date and the download date
because the latest available rate may have an earlier publication date.

## Project Structure

| File            | Purpose                                                 |
| --------------- | ------------------------------------------------------- |
| `main.py`       | Main menu and application entry point                   |
| `processing.py` | Exchange-rate input, calculations, and table output     |
| `database.py`   | Database models, storage, and currency-code lookup      |
| `graph.py`      | Historical data requests, date validation, and plotting |

## Issues

- Lookup date is based on the local machine and may not necessarily be the most up-to-date information when close to a date change.
- Requesting a historical graph is not cached and each lookup requires an API call and an internet connection.
- May not add new currencies if the API updates. Requires deleting the database.
- Does not fall back to rates in an older date if API request fails due to bad status, timeout, etc.

## License

This project is licensed under the [MIT License](LICENSE).
