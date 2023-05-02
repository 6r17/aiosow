[![Pypi](https://img.shields.io/pypi/v/aiosow?color=white&style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/aiosow/)
![Downloads](https://img.shields.io/pypi/dd/aiosow?style=for-the-badge)
[![Build](https://img.shields.io/github/actions/workflow/status/exorde-labs/aiosow/test.yml?style=for-the-badge)](https://github.com/exorde-labs/aiosow) 
[![Discord](https://img.shields.io/discord/1085963894641664203?label=Discord%20&style=for-the-badge&logo=discord&logoColor=white&color=white)](https://discord.gg/XNbmN9zumv)
[![Documentation](https://img.shields.io/badge/-documentation-white?style=for-the-badge)](https://exorde-labs.github.io/aiosow)

## **A**synchronous **I**/**O** **S**oftware **O**rchestration **W**orkstation

`aiosow` is functionnal framework on top of an asynchronous task manager.

> It is meant to allow software architect shape how code should be used.

- **Enforced Separation of Concerns** 

`aiosow` encourage a structure that separate implementations from the behavior.

Defined boundaries for different parts of the codebase makes it easier to reason from buisness perspective.

- **No framework friction & Unparalled modularity**

Implementation have no knoweledge of `aiosow`.

Splitting `implementation` from their usage allows one to completely rewrite how it's different
elements are used, swap them, combine them.


### Example

`implementation.py`
```python

def initialize_memory():
    return { "message": "hello world !" }

def print_message(message):
    print(message)
```

`bindings.py`
```python
setup(initialize_memory)
routine(1)(print_message)
```

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit/)
