from solution import fix_off_by_one

def test_basic():
    assert fix_off_by_one([1, 2, 3]) == [2, 3, 4]

def test_empty():
    assert fix_off_by_one([]) == []

def test_negative():
    assert fix_off_by_one([-1, 0, 1]) == [0, 1, 2]