# **P**ython **S**oftware **O**rchestration **W**orkstation

a high-level Python framework that help write and structure low coupled code.

- [Github](https://github.com/exorde-labs/aiosow) 

## Streamline your Python Data Pipeline in one package
Aiosow simplifies the development of complex data pipelines for your team. 
With imperative programming, large codebases can quickly become unmanageable, 
leading to bugs and errors. Aiosow's separation of concerns approach 
eliminates these issues by allowing each part of the codebase to be developed independently.

## Efficient, Event-Driven, Modular
Aiosow is designed with high modularity and customizability in mind.
Our asynchronous base provides unparalleled performance for Python, while event based programming helps you focus on the desired outcome 
rather than every single step.

## Customizable Asynchronous Python Scripts
Decorators for easy and efficient event triggering implementations.
Express **when** the code should run. Aiosow enables you to customize your code
and build complex data pipelines with ease.

## Compositions

Compositions are Python packages that follow a specific structure that separates the implementation from the 
set of rules for defining their behavior. This enforced structure provides defined boundaries for different
parts of the codebase, making it easier to maintain and scale. As a result, Aiosow provides a set 
of tools that let developers interconnect and customize multiple compositions with ease.

- [Getting started]()
- [Conventions]()
- [Availables Compositions]()

## Installation

```
pip install aiosow
```

## Usage

```
aiosow <composition>
```

You can run the `aiosow -h` to display all the possible options.
Options change based on the composition you are using, so using `aiosow 'aiosow_playwright' -h`
will load it's options and display them in the help menu. 
Those are defined using the `aiosow.options` decorator.

## Contributing

We welcome contributions to this project from anyone. If you would like to contribute, please follow these guidelines:

Fork the repository and create your branch from the latest main branch.
Make your changes, and test them thoroughly.
Submit a pull request describing your changes and explaining why they should be merged. Please ensure that your pull request adheres to our code of conduct.
Wait for the maintainer to review your pull request, and make any requested changes.
Once your pull request is approved, it will be merged into the main branch.
By contributing to this project, you agree to license your contribution under the project's license. If you have any questions or concerns, please reach out to us through GitHub issues.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit/)
