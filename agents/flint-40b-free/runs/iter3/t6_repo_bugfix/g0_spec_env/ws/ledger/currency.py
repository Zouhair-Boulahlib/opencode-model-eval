"""Currency helpers. The number of minor-unit digits differs per currency (ISO 4217)."""
from decimal import Decimal, ROUND_HALF_UP

EXPONENTS: dict[str, int] = {
    "USD": 2, "EUR": 2, "GBP": 2, "CHF": 2, "CAD": 2, "AUD": 2,
    "JPY": 0, "KRW": 0, "ISK": 0,
    "KWD": 3, "BHD": 3, "JOD": 3, "TND": 3,
}


def exponent(currency: str) -> int:
    return EXPONENTS.get(currency.upper(), 2)


def to_minor_units(amount: Decimal, currency: str) -> int:
    """Decimal major-unit amount -> int minor units, e.g. Decimal('12.34') USD -> 1234, Decimal('1500') JPY -> 1500."""
    scale = Decimal(10) ** exponent(currency)
    return int((Decimal(amount) * scale).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def to_major_units(amount_minor: int, currency: str) -> Decimal:
    """int minor units -> Decimal major units with the currency's precision."""
    exp = exponent(currency)
    return (Decimal(amount_minor) / (Decimal(10) ** exp)).quantize(Decimal(1).scaleb(-exp))


def format_amount(amount_minor: int, currency: str) -> str:
    return f"{to_major_units(amount_minor, currency)} {currency.upper()}"
