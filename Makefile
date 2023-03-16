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
	env/bin/pytest -s --cov=aiosow --cov-report=term-missing

report:
	env/bin/coverage report

pydoc:
	cd aiosow ; ../env/bin/python3.10 -m pydoc -b -p 9000 aiosow

pdoc:
	env/bin/pdoc aiosow !aiosow.command !aiosow.utils !aiosow.options !aiosow.setup !aiosow.perpetuate !aiosow.autofill -o docs/

upload:
	env/bin/pip3 install twine
	env/bin/python3 setup.py sdist bdist_wheel
	env/bin/twine upload dist/*
