import pytest
from src.prog import add, multiply, subtract, divide, hello

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 0) == 0

def test_subtract():
    assert subtract(2, 3) == -1
    assert subtract(-1, 1) == -2
    assert subtract(0, 0) == 0

def test_divide():
    assert divide(1, 1) == 1
    assert divide(-1, 1) == -1

def test_hello():
    assert hello() == "Hello, World!"