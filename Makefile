prepare:
	rm -rf env build dist
	virtualenv env --python=python3.10
	. env/bin/activate && \
	env/bin/pip3 install -e .
	env/bin/pip3 install -e ".[dev]"
	env/bin/pip3 install -e ".[aiohttp]"

activate:
	@echo '. env/bin/activate'

test:
	env/bin/pytest -s --cov=stims --cov-report=term-missing

report:
	env/bin/coverage report

pydoc:
	cd stims ; ../env/bin/python3.10 -m pydoc -b -p 9000 stims

pdoc:
	env/bin/pdoc stims -o docs/
