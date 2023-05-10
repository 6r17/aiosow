prepare:
	rm -rf env build dist
	virtualenv env --python=python3.10
	. env/bin/activate && \
	env/bin/pip3 install -e .
	env/bin/pip3 install -e ".[dev]"
	env/bin/pip3 install -e ".[aiohttp]"
	env/bin/pip3 install -e ".[doc]"

install:
	pip3 install -e ".[dev]"
	pip3 install -e ".[aiohttp]"
	pip3 install -e ".[doc]"

activate:
	@echo '. env/bin/activate'

test:
	env/bin/pytest -s --cov=aiosow --cov-report=term-missing --cov-fail-under=100

report:
	env/bin/coverage report

pydoc:
	cd aiosow ; ../env/bin/python3.10 -m pydoc -b -p 9000 aiosow

pdoc:
	env/bin/pdoc aiosow !aiosow.command !aiosow.utils !aiosow.options !aiosow.setup !aiosow.perpetuate !aiosow.autofill -o docs/ --logo 'logo.png' -t './doc-template' --no-show-source

pdocmd:
	env/bin/pdoc aiosow !aiosow.command !aiosow.utils !aiosow.options !aiosow.setup !aiosow.perpetuate !aiosow.autofill --no-show-source -d markdown --output-dir mkdoc

bdist:
	rm -rf dist build
	env/bin/python3 setup.py sdist bdist_wheel

upload: bdist
	env/bin/pip3 install twine
	env/bin/twine upload --skip-existing dist/* --verbose
