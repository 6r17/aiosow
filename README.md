
a high-level Python framework that help write and structure low coupled code.

- [Github](https://github.com/exorde-labs/aiosow) 

## Streamline your Python Data Pipeline in one package
Building a customizable all-in-one package that does api, scraping and integrate ia toolkits is hard.

`Aiosow` simplifies the development of complex data pipelines for your team. 
With procedural programming, large codebases can quickly become unmanageable, 
leading to bugs and errors. Event-based programming helps you focus on the desired outcome 
rather than every single step.


## Efficient, Event-Driven, Modular
`Aiosow` is designed with high modularity and customizability in mind.
Our asynchronous base provides unparalleled performance for Python, and the separation of concerns approach 
allows each part of the codebase to be developed independently.


## Enforced Separation of Concerns 

`Compositions` are [Python](https://www.python.org/) packages that separates the implementation from the 
set of rules for defining their behavior. This enforced structure provides defined boundaries for different
parts of the codebase, making it easier to maintain and scale. As a result, `aiosow` can provide a set 
of tools that let developers interconnect and customize multiple compositions with ease.

## Customizable Asynchronous Python Scripts
`Aiosow` provides decorators and utilities for easy and efficient event triggering implementations.
This means you can re-write the program's behavior without having to re-write it's technical aspect.
Express **when** the code should run. `aiosow` enables you to customize your code and build complex
data pipelines with ease.

- `aiosow.bindings` helps you express configurability, further data-piping, time-constraints, and more... 
- `aiosow.routines` helps you schedule code to flow trough time 
- `aiosow.aiohttp` to build an API with [aiohttp](https://docs.aiohttp.org/en/stable/)

## Installation

```
pip install aiosow
```

## Command

```
aiosow <composition>
```

- You can run the `aiosow -h` to display all the possible options.
- Options change based on the composition you are using

Using `aiosow 'composition_name' -h` will load it's options and display them in 
the help menu. Those are defined using the `aiosow.options` decorator.

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
