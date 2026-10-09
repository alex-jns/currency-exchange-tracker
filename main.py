import requests
from database import save_rates, get_today_rates, save_currencies, get_currency_codes, ExchangeRate
from graph import show_graph

url = "https://api.frankfurter.dev/v2/rates"
cached_rates = get_today_rates()
valid_currencies = get_currency_codes()

# Prints a user friendly table using formatting
def print_header():

    print(f"\n{'Date':<12} {'Base':<6} {'Quote':<6} {'Rate':>14}")

    # Prints 41 dashes
    print("-" * 41)

def print_rate(rate):

    print(
        # Date on the left, 12 characters
        f"{rate.date:<12} "

        # Base on the left, 6 characters
        f"{rate.base:<6} "

        # Quote on the left, 6 characters
        f"{rate.quote:<6} "

        # Rate to the right, 14 characters, add comma for thousands, up to 6 decimal places
        f"{rate.rate:>14,.6f}"
    )

# Attempt to show today's rates; show all if no parameters given
def show_rates():

    # Check if database has today's rates, and if it does use them
    if cached_rates:
        print("Using database")

        for rate in cached_rates:
            print_rate(rate)

    # In this case, the database doesn't have today's rates and must call the endpoint
    else:
        print("Calling API")

        response = requests.get(
            url,
            params={"base": "USD"},
            timeout=10
        )

        response.raise_for_status()
        today_rates = response.json()
        save_rates(today_rates)
        database_rates = get_today_rates()
        print_header()

        for rate in database_rates:
            print_rate(rate)

def process_rates():
    # Loop until valid currency or user exits
    while True:
        print("\nTo show all rates, hit enter and leave entry blank.")
        print("Type 'exit' to go back to the main menu.")
        print("Please enter currencies in correct ISO format (e.g.: USD, EUR).\n")

        base = input("From currency (base): ").strip().upper()

        # Meets the conditions to break from loop
        if base == "EXIT" or not base or base in valid_currencies:
            break

        print("Invalid currency code. Please try again.")

    # User wants to exit this menu
    if base == "EXIT": return

    # Input is empty, therefore user wants to see all rates
    if not base:
        show_rates()
        return

    # We now have a applicable base currency in ISO format.
    while True:
        quote = input("To currency (quote): ").strip().upper()

        if quote == "EXIT" or not quote or quote in valid_currencies:
            break

        print("Invalid currency code. Please try again.")

    if quote == "EXIT": return

    if not quote:
        show_rates()
        return

    # We now have a valid base and quote, so we can call the function now
    show_pair(base, quote)

def get_usd_rates():
    usd_rates = {"USD": 1.0}

    for rate in get_today_rates():
        usd_rates[rate.quote] = rate.rate

    return usd_rates

def show_pair(base, quote):
    base = base.upper()
    quote = quote.upper()
    usd_rates = get_usd_rates()

    if base not in usd_rates or quote not in usd_rates:
        print("Calling API")

        try:
            response = requests.get(
                url,
                params={"base": "USD"},
                timeout=10
            )
            response.raise_for_status()
            save_rates(response.json())
        except requests.RequestException as error:
            print(f"Could not retrieve rates: {error}")
            return

        usd_rates = get_usd_rates()
    else:
        print("Using database")

    if base not in usd_rates or quote not in usd_rates:
        print("No rate available for this currency pair.")
        return

    # Create an ExchangeRate object
    converted_rate = ExchangeRate(
        date="Calculated",
        base=base,
        quote=quote,
        rate=usd_rates[quote] / usd_rates[base]
    )

    print_header()
    print_rate(converted_rate)

def main():

    while True:
        print("\nCurrency Exchange Tracker")
        print("1. Show today's exchange rates")
        print("2. Show a graph of exchange rates over time")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        match choice:
            case "1":
                process_rates()
            case "2":
                base = input("From currency: ").strip().upper()
                quote = input("To currency: ").strip().upper()
                start = input("Start date (YYYY-MM-DD): ").strip()
                end = input("End date (YYYY-MM-DD): ").strip()

                show_graph(base, quote, start, end)
            case "3":
                break
            case _:
                print("Invalid option (Please enter 1, 2, or 3).")

if __name__ == "__main__":
    main()