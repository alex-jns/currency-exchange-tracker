import requests

from sqlalchemy import create_engine, String, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import date

# Parent class
class Base(DeclarativeBase): pass

# Maps the exchange_rates records in currency.db
class ExchangeRate(Base):

    # The table we're putting the records in
    __tablename__ = "exchange_rates"

    # Describes the fields and what data structure they'll use
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(String)
    base: Mapped[str] = mapped_column(String)
    quote: Mapped[str] = mapped_column(String)
    rate: Mapped[float] = mapped_column(Float)

    # In order for the cache to work, we need to know the date we added the record
    # This is because some currencies don't update every day
    fetched_on: Mapped[str] = mapped_column(String)

# Stores the information from the currency endpoint to a table
class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)

# Points to the db file in the directory
engine = create_engine("sqlite:///currency.db")

# Creates missing tables if they don't exist yet
Base.metadata.create_all(engine)

# Store the API's json response in the database
def save_rates(data):

    with Session(engine) as session:

        # We need today's date in the same ISO format as the API
        fetched_on = date.today().isoformat()
        rates = []

        # Convert each dictionary in the API call into an ExchangeRate object
        for item in data:
            rate = ExchangeRate(
                date=item["date"],
                base=item["base"],
                quote=item["quote"],
                rate=item["rate"],
                fetched_on=fetched_on
            )

            rates.append(rate)

        # Once all the objects are made, insert and commit
        session.add_all(rates)
        session.commit()

# Find out if today's date matches the database's date
def get_today_rates():

    today = date.today().isoformat()

    with Session(engine) as session:

        # Using a select statement to find any entries not refreshed yet today
        statement = select(ExchangeRate).where(
            ExchangeRate.fetched_on == today
        )

        # Execute the query and return the ExchangeRate objects
        return session.scalars(statement).all()

# Saves the currencies from the API response
def save_currencies(data):

    with Session(engine) as session:

        # This one makes Currency objects
        for item in data:
            session.merge(
                Currency(
                    code=item["iso_code"],
                    name=item["name"]
                )
            )

        session.commit()

# Returns the three letter currency codes
def get_currency_codes():

    # Attempts to find it in the database
    with Session(engine) as session:
        statement = select(Currency.code)
        codes = set(session.scalars(statement).all())

    # If it finds it in the database, return it
    if codes: return codes

    # If not, call the API for a list of currencies
    response = requests.get(
        "https://api.frankfurter.dev/v2/currencies",
        timeout=30
    )
    response.raise_for_status()
    currencies = response.json()

    # Then, save the response to the database and query again
    save_currencies(currencies)
    with Session(engine) as session:
        return session.scalars(statement).all()