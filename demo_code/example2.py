<<<<<<< HEAD
def multiply(a, b):
    return a * b

def test_multiply():
    assert multiply(2,3) == 6
=======
"""Demo: simple utility functions (viable code)."""
from __future__ import annotations


def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def is_prime(n: int) -> bool:
    """Check if n is a prime number."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def chunk_list(items: list, size: int) -> list[list]:
    """Split a list into chunks of given size."""
    if size <= 0:
        raise ValueError("chunk size must be > 0")
    # TODO: optimize for large lists with generator
    return [items[i : i + size] for i in range(0, len(items), size)]
>>>>>>> 91142c2 (refactor: full rewrite v1.0.0 — modular agent architecture)
