"""Tests for demo_code.example1 and demo_code.example2."""
from __future__ import annotations

import pytest
from demo_code.example1 import add, subtract, divide, Calculator
from demo_code.example2 import fibonacci, is_prime, chunk_list


class TestCalculator:
    def test_add(self) -> None:
        assert add(2, 3) == 5
        assert add(-1, 1) == 0

    def test_subtract(self) -> None:
        assert subtract(5, 3) == 2
        assert subtract(0, 5) == -5

    def test_divide(self) -> None:
        assert divide(10, 2) == 5.0
        with pytest.raises(ZeroDivisionError):
            divide(1, 0)

    def test_calculator_operate(self) -> None:
        calc = Calculator()
        assert calc.operate("add", 1, 2) == 3
        assert calc.operate("mul", 3, 4) == 12
        assert len(calc.history) == 2

    def test_calculator_unknown_op(self) -> None:
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.operate("pow", 2, 3)


class TestFibPrimeChunk:
    def test_fibonacci(self) -> None:
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
        assert fibonacci(10) == 55

    def test_fibonacci_negative(self) -> None:
        with pytest.raises(ValueError):
            fibonacci(-1)

    def test_is_prime(self) -> None:
        assert not is_prime(1)
        assert is_prime(2)
        assert is_prime(17)
        assert not is_prime(100)

    def test_chunk_list(self) -> None:
        assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
        with pytest.raises(ValueError):
            chunk_list([1], 0)