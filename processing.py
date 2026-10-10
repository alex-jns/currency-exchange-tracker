import requests

from database import ExchangeRate, get_today_rates, get_currency_codes, save_rates

url = "https://api.frankfurter.dev/v2/rates"
cached_rates = get_today_rates()
valid_currencies = get_currency_codes()

# Prints a user friendly table using formatting
def print_header():

    print(f"\n{'Date':<12} {'Base':<6} {'Quote':<6} {'Rate':>14}")

    # Prints 41 dashes
    print("-" * 41)

# Separates the table contents from the header
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

        # Saves the rates to the database then queries it
        save_rates(today_rates)
        database_rates = get_today_rates()

        # Prints to the user
        print_header()
        for rate in database_rates:
            print_rate(rate)

# Starts user processing for currency rates; called in main
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

# Instead of having every combination of currency, uses USD to calculate exchange rate
def get_usd_rates():
    usd_rates = {"USD": 1.0}

    for rate in get_today_rates():
        usd_rates[rate.quote] = rate.rate

    return usd_rates

# Shows the rate between two currencies using USD rates
def show_pair(base, quote):

    usd_rates = get_usd_rates()

    # If the needed currency is not in the database, call the API
    if base not in usd_rates or quote not in usd_rates:
        print("Calling API")

        # Try to call the API
        try:
            response = requests.get(
                url,
                params={"base": "USD"},
                timeout=30
            )
            response.raise_for_status()
            save_rates(response.json())

        # Upon HTTP error or timeout:
        except requests.RequestException as error:
            print(f"Could not retrieve rates: {error}")
            return

        usd_rates = get_usd_rates()
    else:
        print("Using database")

    # If for some reason the currency is not available
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

    # Print to end user
    print_header()
    print_rate(converted_rate)