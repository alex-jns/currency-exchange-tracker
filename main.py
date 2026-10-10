from graph import graph_processing
from processing import process_rates

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
                graph_processing()
            case "3":
                break
            case _:
                print("Invalid option (Please enter 1, 2, or 3).")

if __name__ == "__main__":
    main()