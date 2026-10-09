import requests
import pandas as pd
import matplotlib.pyplot as plt


def show_graph(base, quote, start_date, end_date):
    base = base.strip().upper()
    quote = quote.strip().upper()

    # Request historical rates
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v2/rates",
            params={
                "base": base,
                "quotes": quote,
                "from": start_date,
                "to": end_date
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        print(f"Could not retrieve historical rates: {error}")
        return

    # Create a table from the response
    df = pd.DataFrame(data)

    if df.empty:
        print("No rates available for that pair and date range.")
        return

    # Convert date strings and put rows in date order
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Plot dates against exchange rates
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["rate"])

    ax.set_title(f"{base} to {quote}: {start_date} to {end_date}")
    ax.set_xlabel("Rate date")
    ax.set_ylabel(f"{quote} per 1 {base}")
    ax.grid(True, alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()
    plt.show()

    return df