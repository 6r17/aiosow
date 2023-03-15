from aiosow.utils import get_value_by_path

def test_get_value_by_path():
    data = {
        'a': {
            'b': {
                'c': 42
            }
        }
    }

    assert get_value_by_path(data, "a__b__c") == 42
    assert get_value_by_path(data, "a.b.c", separator=".") == 42

    assert get_value_by_path(data, "a__b__d") is None
    assert get_value_by_path(data, "a.b.d", separator=".") is None

    data = {
        'a': {
            'b': [
                {'c': 42},
                {'c': 43}
            ]
        }
    }
    assert get_value_by_path(data, "a__b__0__c") == 42
    assert get_value_by_path(data, "a.b.1.c", separator=".") == 43
    assert get_value_by_path(data, "a__b__2__c") is None
