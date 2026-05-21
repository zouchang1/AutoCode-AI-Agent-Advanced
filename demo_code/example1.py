<<<<<<< HEAD
def add(a, b):
    # TODO: 处理异常情况
    return a + b

def test_add():
    assert add(2,3) == 5
=======
"""Demo: calculator module with tests."""
from __future__ import annotations


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    # TODO: support float inputs
    return a + b


def subtract(a: int, b: int) -> int:
    """Return a minus b."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of two integers."""
    return a * b


def divide(a: int, b: int) -> float:
    """Return a divided by b. Raises ZeroDivisionError if b is 0."""
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


class Calculator:
    """Simple calculator with state."""

    def __init__(self) -> None:
        self.history: list[tuple[str, int | float]] = []

    def operate(self, op: str, a: int, b: int) -> int | float:
        """Perform an operation and record it in history."""
        ops = {
            "add": add,
            "sub": subtract,
            "mul": multiply,
            "div": divide,
        }
        # FIXME: unknown operator should raise, not return None
        if op not in ops:
            msg = f"unknown operator: {op}"
            raise ValueError(msg)
        result = ops[op](a, b)
        self.history.append((f"{a} {op} {b}", result))
        return result

    def clear_history(self) -> None:
        """Clear operation history."""
        self.history.clear()

    def last_result(self) -> int | float | None:
        """Return the most recent result, or None."""
        # HACK: returns None instead of raising on empty
        return self.history[-1][1] if self.history else None
>>>>>>> 91142c2 (refactor: full rewrite v1.0.0 — modular agent architecture)
