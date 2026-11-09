"""Validation rules applied before a transaction is stored."""
from .config import MAX_DESCRIPTION_LENGTH
from .currency import EXPONENTS
from .models import Transaction


def validate_transaction(tx: Transaction) -> list[str]:
    errors: list[str] = []
    if not tx.id:
        errors.append("missing id")
    if not tx.description or len(tx.description) > MAX_DESCRIPTION_LENGTH:
        errors.append("description missing or too long")
    if not isinstance(tx.amount_minor, int):
        errors.append("amount_minor must be an int (minor units)")
    if tx.currency.upper() not in EXPONENTS:
        errors.append(f"unknown currency {tx.currency}")
    if tx.amount_minor == 0:
        errors.append("zero amount")
    return errors


def validate_all(transactions: list[Transaction]) -> dict[str, list[str]]:
    return {tx.id: errs for tx in transactions if (errs := validate_transaction(tx))}
