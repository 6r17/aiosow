from setuptools import setup, find_packages

setup(
    name='aiosow',
    version='0.0.1',
    packages=find_packages(include=['aiosow']),
    license='MIT',
    entry_points={
        'console_scripts': [
            'aiosow = aiosow.command:run',
        ],
    },
    install_requires=[],
    extras_require={
        "aiohttp":[
            'aiohttp',
        ],
        "dev": [
            "pytest",
            "pytest-mock",
            "pytest-asyncio",
            "pytest-coverage",
            "pdoc"
        ]
    }
)
