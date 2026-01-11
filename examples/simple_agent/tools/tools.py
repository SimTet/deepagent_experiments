"""Basic tools for the simple agent demonstration."""

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_todays_date() -> str:
    """Get today's date in YYYY-MM-DD format.

    Returns:
        str: Today's date formatted as YYYY-MM-DD
    """
    return datetime.now().strftime("%Y-%m-%d")


@tool
def multiply_floats(a: float, b: float) -> float:
    """Multiply two floating point numbers.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        float: The product of a and b
    """
    return a * b


@tool
def divide_floats(a: float, b: float) -> str:
    """Divide two floating point numbers.

    Args:
        a: Numerator (number to be divided)
        b: Denominator (number to divide by, must be non-zero)

    Returns:
        str: The quotient of a / b, or an error message if b is zero
    """
    if b == 0:
        return "Error: Division by zero is not allowed. The denominator must be non-zero."

    result = a / b
    return str(result)
