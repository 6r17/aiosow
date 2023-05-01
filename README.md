[![Pypi](https://img.shields.io/pypi/v/aiosow?color=white&style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/aiosow/)
![Downloads](https://img.shields.io/pypi/dd/aiosow?style=for-the-badge)
[![Build](https://img.shields.io/github/actions/workflow/status/exorde-labs/aiosow/test.yml?style=for-the-badge)](https://github.com/exorde-labs/aiosow) 
[![Discord](https://img.shields.io/discord/1085963894641664203?label=Discord%20&style=for-the-badge&logo=discord&logoColor=white&color=white)](https://discord.gg/XNbmN9zumv)
[![Documentation](https://img.shields.io/badge/-documentation-white?style=for-the-badge)](https://exorde-labs.github.io/aiosow)

## **A**synchronous **I**/**O** **S**oftware **O**rchestration **W**orkstation

`aiosow` is software orchestration framework on top of an asynchronous task manager.

It is meant to allow software architect shape how code should be used.

- Define your contributors boundaries without being restricted by a framework
- Allows code to live with it's problem instead of being tied to technical elements
- Allows unparalled modularity

## Enforced Separation of Concerns 

`aiosow` encourage a structure that separate implementations from the behavior.

Defined boundaries for different parts of the codebase, makes it easier to maintain and scale.
As a result, `aiosow` can provide a set of tools that let developers interconnect and 
customize multiple compositions with ease.

## Customizable Asynchronous State-Machine
`aiosow` is a programmable state-machine customizable with decorators and utilities for easy and efficient event triggering implementations.
State-machines provides a way to manage the flow of a system by storing and managing mutations in the `memory`. 

- One global `memory` represented as a `dict`
- Mutations are the changes, just return a `dict` and you got a valid mutation
- To bind this function in the state-machine you use `aiosow.bindings`

These bindings allow to program the machine and express when to call the appropriate functions in the correct order, ensuring that the system behaves as expected.
The state machine is a useful tool for managing complex systems and ensuring that behavior is well-defined and predictable.
It allows to react to changes in the system and implement logic based on those changes (see `aiosow.bindings.on` for instance).

- `aiosow.bindings` helps you express configurability, further data-piping, time-constraints, and more... 
- `aiosow.routines` helps you schedule code to flow trough time 

## Compositions

`compositions` are [Python](https://www.python.org/) packages that use `aiosow.bindings` to define `aiosow`'s behavior. 

They follow a set of rules :

##### 1. **`implementation` is strictly separate from the package's `behavior`.**
- `implementation` refers to the technical aspects of how a feature is coded and developed, such as algorithms and data structures. It focuses on the **"how"** of software development. 

Separating these two concerns helps make software more maintainable and flexible over time.

**Example of `implementation`**:
```
def get_data():
    return 'foo'

def capitalize(s: str):
    return s.capitalize()
```
##### 2. **Behaviors are defined in a `behavior.py` file using `aiosow.bindings`**
- `behavior` refers to the overall conduct and purpose of a software system, from the user's perspective. It focuses on the **"what"** and **"when"** of software development.

**Example of `behavior`**:
```
signal_data_when, on_received_data_do = wire() # build a wire for data reception
data_treated_when, on_data_ready_do = wire()   # build a wire for data that is ready

signal_data_when(get_data)                     # on data reception trigger functions registered
on_received_data_do(capitalize)                # capitalize every data that is received
data_treated_when(capitalize)                  # once data is capitalized, send it
routine(1)(get_data)                           # get some data every second
on_data_ready_do(print)                        # anytime data is ready print it
```

##### 3. **Function prototypes use a strict naming consistency**
`aiosow.bindings.autofill` is the backone of the library used trough all tools to cast a function.

It is doing so by filling missing arguments from their prototype based on `memory`.

**Example**:
```
                `args` are poped first, `on` will pass the value that changed
                  |
                  | `foo` is autofilled, value is retrieved from `memory`
                  |   |
                  v   v
do_smtg = lambda ev, foo: print(ev, foo)
on('event')(do_smtg)                           # this will trigger do_smtg when 'bar' is set
setup(lambda : { 'foo': 'bar' })               # init 'foo' to 'bar'
setup(lambda : { 'event': 'trigger' })         # triggers `do_smtg`

> 'trigger', 'bar'

```
##### 4. **Implementation is low-coupled**
Low coupled code refers to code that has minimal interdependencies between its different components or modules. In other words, changes to one component should not require extensive modifications to other components. This promotes modularity, maintainability, and flexibility in software development.

- **When you write an `implementation`, you are providing vocabulary available to the `behavior` expression.**

**Example of high-coupled code**:
```
def calculate_total_price(quantity, unit_price):
    tax_rate = 0.1
    subtotal = quantity * unit_price
    tax_amount = subtotal * tax_rate
    total_price = subtotal + tax_amount
    return total_price
```

**Example of low-coupled code**:
```
def calculate_subtotal(quantity, unit_price):
    subtotal = quantity * unit_price
    return subtotal

def calculate_tax(subtotal):
    tax_rate = 0.1
    tax_amount = subtotal * tax_rate
    return tax_amount

def calculate_total_price(quantity, unit_price):
    subtotal = calculate_subtotal(quantity, unit_price)
    tax_amount = calculate_tax(subtotal)
    total_price = subtotal + tax_amount
    return total_price
```
##### 5. **Initialization is decoupled of processing**

The principle of decoupling the setup from operation involves separating the preparation from its actual use. 

This ensures

- that changes or modifications made during setup do not interfere with the processing. 
- that the implemented vocabulary focuses on expressing `how`. 

##### 6. **Compositions should not be blocking the main execution**

`compositions` implementations should not contain synchronous code that blocks the main event loop, which could cause the entire application to freeze.

Instead, all I/O operations, heavy computations and blocking tasks should be executed asynchronously using the `aiosow.bindings.make_async` decorator. This will ensure that the event loop remains responsive and can process other tasks efficiently.


## Usage

```
aiosow <composition>
```

- You can run the `aiosow -h` to display all the possible options.
- Options change based on the composition you are using

Using `aiosow 'composition_name' -h` will load it's options and display them in 
the help menu. Those are defined using the `aiosow.options` decorator.

## Installation

```
pip install aiosow
```

## Contributing

We welcome contributions to this project from anyone. If you would like to contribute, please follow these guidelines:

- Fork the repository and create your branch from the latest main branch.
- Make your changes, and test them thoroughly.
- Submit a pull request describing your changes and explaining why they should be merged. Please ensure that your pull request adheres to our code of conduct.
- Wait for a maintainer to review your pull request, and make any requested changes.
- Once your pull request is approved, it will be merged into the main branch.

By contributing to this project, you agree to license your contribution under the project's license. If you have any questions or concerns, please reach out to us through GitHub issues.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit/)
