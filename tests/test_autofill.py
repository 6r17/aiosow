import pytest

from aiosow.bindings import delay
from aiosow.autofill import (
    get_aliases,
    reset_aliases,
    autofill,
    alias,
    get_function_representation,
)


def my_func(__a__, __b__=2, __c__=3):
    """__ is used to prevent linter error"""


@pytest.mark.asyncio
async def test_alias():
    assert len(get_aliases()) == 0

    def test():
        return "bar"

    alias("foo")(test)
    assert len(get_aliases()) == 1
    assert get_aliases()["foo"] == test


@pytest.mark.asyncio
async def test_autofill_positional():
    # Test 1: Call a simple function with positional arguments
    def my_function(a, b, c):
        return a + b + c

    args = (1, 2)
    memory = {"c": 3}

    assert await autofill(my_function, args=args, memory=memory) == 6


@pytest.mark.asyncio
async def test_autofill_positional_and_keywords():
    # Test 2: Call a function with positional and keyword arguments
    def my_function2(a, b, c=0, d=0):
        return a + b + c + d

    args = (1, 2)
    memory = {"c": 3}

    assert await autofill(my_function2, args=args, memory=memory) == 6

    args = (1, 2)
    memory = {"c": 3, "d": 4}

    assert await autofill(my_function2, args=args, memory=memory) == 10


@pytest.mark.asyncio
async def test_autofill_keywords():
    # Test 3: Call a function with keyword arguments
    def my_function3(a, b=0, c=0):
        return a + b + c

    memory = {"a": 1, "b": 2, "c": 3}

    assert await autofill(my_function3, memory=memory) == 6

    memory = {"a": 1}

    assert await autofill(my_function3, memory=memory) == 1

    memory = {"a": 1, "c": 3}

    assert await autofill(my_function3, memory=memory) == 4


@pytest.mark.asyncio
async def test_autofill_mixxed():
    # Test 4: Call a function with a mix of positional and keyword arguments
    def my_function4(a, b, c=0, d=0):
        return a + b + c + d

    args = (1,)
    memory = {"b": 2, "c": 3}

    assert await autofill(my_function4, args=args, memory=memory) == 6

    args = (1, 2, 3)
    memory = {"d": 4}

    assert await autofill(my_function4, args=args, memory=memory) == 10


@pytest.mark.asyncio
async def test_autofill_no_arg():
    # Test 5: Call a function without arguments
    def my_function5():
        return 42

    assert await autofill(my_function5) == 42


@pytest.mark.asyncio
async def test_autofill_arbitrary():
    # Test 6: Call a function with arbitrary arguments
    def my_function6(memory, *args):
        return args, memory

    args = (1, 2)
    memory = {"a": 3, "b": 4}
    assert await autofill(my_function6, args=args, memory=memory) == (
        (1, 2),
        {"a": 3, "b": 4},
    )


@pytest.mark.asyncio
async def test_autofill_decorated():
    def my_function6(memory):
        return memory

    memory = {"a": 3, "b": 4}
    # Test 7: On a decorated function
    decorated_function = delay(0.05)(my_function6)
    assert await autofill(decorated_function, memory=memory) == ({"a": 3, "b": 4})


@pytest.mark.asyncio
async def test_autofill_aliased():
    reset_aliases()

    # Test 8: With an alias
    def my_function7(test):
        return test

    args = (1, 2)
    memory = {"test": "error"}

    def test():
        return "correct"

    alias("test")(test)
    assert await autofill(my_function7, args=args, memory=memory) == "correct"


def test_get_function_representation():
    # Test case 1: Test with a named function
    def named_function():
        pass

    assert get_function_representation(named_function) == "named_function"

    # Test case 2: Test with a lambda function
    lambda_function = lambda x: x**2
    expected_result = "lambda_function = lambda x: x**2"
    assert get_function_representation(lambda_function) == expected_result

    # Test case 3: Test with a lambda function with whitespace
    lambda_function = lambda x: x**2
    expected_result = "lambda_function = lambda x: x**2"
    assert get_function_representation(lambda_function) == expected_result
