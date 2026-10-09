from sqlalchemy import create_engine, String, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import date
import requests

class Base(DeclarativeBase):
    pass

# Maps the exchange_rates table in currency.db
class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

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

engine = create_engine("sqlite:///currency.db")

Base.metadata.create_all(engine)

# Store the API's json response in the database
def save_rates(data):

    with Session(engine) as session:

        # We need today's date in the same ISO format as the API
        fetched_on = date.today().isoformat()

        rates = []

        for item in data:
            rate = ExchangeRate(
                date=item["date"],
                base=item["base"],
                quote=item["quote"],
                rate=item["rate"],
                fetched_on=fetched_on
            )

            rates.append(rate)

        session.add_all(rates)
        session.commit()

# Find out if today's date matches the database's date
def get_today_rates():
    today = date.today().isoformat()

    with Session(engine) as session:
        statement = select(ExchangeRate).where(
            ExchangeRate.fetched_on == today
        )

        return session.scalars(statement).all()

def save_currencies(data):

    with Session(engine) as session:

        for item in data:
            session.merge(
                Currency(
                    code=item["iso_code"],
                    name=item["name"]
                )
            )

        session.commit()

def get_currency_codes():

    with Session(engine) as session:
        statement = select(Currency.code)
        codes = set(session.scalars(statement).all())

    if codes:
        return codes
    
    response = requests.get(
        "https://api.frankfurter.dev/v2/currencies",
        timeout=10
    )

    response.raise_for_status()
    currencies = response.json()
    save_currencies(currencies)

    with Session(engine) as session:
        return session.scalars(statement).all()