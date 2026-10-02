import requests
from database import save_rates, get_today_rates

url = "https://api.frankfurter.dev/v2/rates"
cached_rates = get_today_rates()

if cached_rates:
    print("Using database")

    for rate in cached_rates:
        print(rate.base, rate.quote, rate.rate)

else:
    print("Calling API")

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    save_rates(data)