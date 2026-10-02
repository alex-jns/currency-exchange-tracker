from sqlalchemy import create_engine, String, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import date

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

engine = create_engine("sqlite:///currency.db")

Base.metadata.create_all(engine)

# Store the API's json response in the database
def save_rates(data):
    with Session(engine) as session:
        rates = []

        for item in data:
            rate = ExchangeRate(
                date=item["date"],
                base=item["base"],
                quote=item["quote"],
                rate=item["rate"]
            )

            rates.append(rate)

        session.add_all(rates)
        session.commit()

# Find out if today's date matches the database's date
def get_today_rates():
    today = date.today().isoformat()

    with Session(engine) as session:
        statement = select(ExchangeRate).where(
            ExchangeRate.date == today
        )

        return session.scalars(statement).all()