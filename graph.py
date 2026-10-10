import requests
import pandas as pd
import matplotlib.pyplot as plt

from datetime import date
from database import get_currency_codes

# Can be used for both "for" and "to" currency codes
def ask_currency(prompt):

    valid_currencies = get_currency_codes()

    while True:
        currency = input(prompt).strip().upper()

        if currency == "EXIT":
            return None

        if currency in valid_currencies:
            return currency

        print("Invalid currency code. Example: USD or GBP.")

# This function can be used for both the "from" date and the "to" date
# The "earliest" is used when using the "to" date as the "from" date is passed into it
def ask_date(prompt, earliest=None):

    while True:
        text = input(prompt).strip()

        if text.upper() == "EXIT":
            return None

        # Try to convert the text to ISO format; will throw exception when it fails
        try:
            entered_date = date.fromisoformat(text)
        except ValueError:
            print("Enter a valid date in YYYY-MM-DD format.")
            continue

        # Using the ISO format, we can make sure the date is not in the future
        if entered_date > date.today():
            print("The date cannot be in the future.")
            continue

        # "If earliest is not None" shows this will only be used on the "to" portion
        # This is to check if the "to" date is later than the "from" date
        if earliest is not None and entered_date < earliest:
            print("End date cannot be before the start date.")
            continue

        return entered_date

# Handles the user input for creating a graph; called in main
def graph_processing():

    print("Type 'exit' at any prompt to return to the menu.")

    base = ask_currency("From currency: ")
    if base is None: return

    quote = ask_currency("To currency: ")
    if quote is None: return

    start = ask_date("Start date (YYYY-MM-DD): ")
    if start is None: return

    end = ask_date("End date (YYYY-MM-DD): ", earliest=start)
    if end is None: return

    show_graph(base, quote, start.isoformat(), end.isoformat())

# Handles creating a data frame and displaying a line graph using pandas & matplotlib
def show_graph(base, quote, start_date, end_date):
    base = base.strip().upper()
    quote = quote.strip().upper()

    # Try to request historical rates from the API endpoint
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v2/rates",

            # Good way to add parameters to the API URL
            params={
                "base": base,
                "quotes": quote,
                "from": start_date,
                "to": end_date
            },

            # Try to connect for 30 seconds
            timeout=30
        )

        # If we get a bad HTTP error status (404, 500) this throws an error
        response.raise_for_status()
        data = response.json()

    # Just in case we get a bad response from the API
    except requests.RequestException as error:
        print(f"Could not retrieve historical rates: {error}")
        return

    # Create a table from the response
    df = pd.DataFrame(data)

    # Just in case there's nothing to show
    if df.empty:
        print("No rates available for that pair and date range.")
        return

    # Convert date strings and put rows in date order
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Plot dates against exchange rates
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["rate"])

    # Setting up the graph
    ax.set_title(f"{base} to {quote}: {start_date} to {end_date}")
    ax.set_xlabel("Rate date")
    ax.set_ylabel(f"{quote} per 1 {base}")
    ax.grid(True, alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()
    plt.show()

    return df