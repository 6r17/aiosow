prepare:
	rm -rf env build dist
	virtualenv env --python=python3.10
	. env/bin/activate && \
	pip3 install -e .
	pip3 install -e .[dev]

activate:
	@echo '. env/bin/activate'

test:
	env/bin/pytest --cov=stims --cov-report=term-missing
