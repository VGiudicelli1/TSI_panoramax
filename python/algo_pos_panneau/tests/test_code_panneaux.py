import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_pos_panneau.code_panneaux import is_code_back, is_code_face, get_code_back

def test_code():
    code = "B14"
    assert is_code_face(code)
    assert not is_code_back(code)
    assert get_code_back(code) == "A00"

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
