# test_example.py

def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0

def subtract(a, b):
    return a - b

def test_subtract():
    assert subtract(3, 2) == 1
    assert subtract(0, 0) == 0
    assert subtract(-1, -1) == 0

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])