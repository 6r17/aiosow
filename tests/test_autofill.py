import pytest

from stims.bindings import delay
from stims.autofill import *

def my_func(__a__, __b__=2, __c__=3):
    '''__ is used to prevent linter error'''

def test_prototype():
    proto = prototype(my_func)
    assert len(proto) == 3
    assert proto[0] == ('__a__', None)
    assert proto[1] == ('__b__', 2)
    assert proto[2] == ('__c__', 3)

@pytest.mark.asyncio
async def test_alias():
    assert len(get_aliases()) == 0
    def test():
        return 'bar'
    alias('foo')(test)
    assert len(get_aliases()) == 1
    assert get_aliases()['foo'] == test

@pytest.mark.asyncio
async def test_await_autofill():
    reset_aliases()
    # Test 1: Call a simple function with positional arguments
    def my_function(a, b, c):
        return a + b + c

    args = (1, 2)
    kwargs = {'c': 3}

    assert await autofill(my_function, args=args, kwargs=kwargs) == 6

    # Test 2: Call a function with positional and keyword arguments
    def my_function2(a, b, c=0, d=0):
        return a + b + c + d

    args = (1, 2)
    kwargs = {'c': 3}

    assert await autofill(my_function2, args=args, kwargs=kwargs) == 6

    args = (1, 2)
    kwargs = {'c': 3, 'd': 4}

    assert await autofill(my_function2, args=args, kwargs=kwargs) == 10

    # Test 3: Call a function with keyword arguments
    def my_function3(a, b=0, c=0):
        return a + b + c

    kwargs = {'a': 1, 'b': 2, 'c': 3}

    assert await autofill(my_function3, kwargs=kwargs) == 6

    kwargs = {'a': 1}

    assert await autofill(my_function3, kwargs=kwargs) == 1

    kwargs = {'a': 1, 'c': 3}

    assert await autofill(my_function3, kwargs=kwargs) == 4

    # Test 4: Call a function with a mix of positional and keyword arguments
    def my_function4(a, b, c=0, d=0):
        return a + b + c + d

    args = (1,)
    kwargs = {'b': 2, 'c': 3}

    assert await autofill(my_function4, args=args, kwargs=kwargs) == 6

    args = (1, 2, 3)
    kwargs = {'d': 4}

    assert await autofill(my_function4, args=args, kwargs=kwargs) == 10

    # Test 5: Call a function without arguments
    def my_function5():
        return 42

    assert await autofill(my_function5) == 42

    # Test 6: Call a function with arbitrary arguments
    def my_function6(*args, **kwargs):
        return args, kwargs

    args = (1, 2)
    kwargs = {'a': 3, 'b': 4}

    assert await autofill(my_function6, args=args, kwargs=kwargs) == ((1, 2), {'a': 3, 'b': 4})

    # Test 7: On a decorated function
    decorated_function = delay(0.05)(my_function6)
    assert await autofill(decorated_function, args=args, kwargs=kwargs) == ((1, 2), {'a': 3, 'b': 4})

    # Test 8: With an alias
    def my_function7(test):
        return test

    kwargs = { 'test': 'error' }
    def test():
        return 'correct'
    alias('test')(test)
    assert await autofill(my_function7, args=args, kwargs=kwargs) == 'correct'
