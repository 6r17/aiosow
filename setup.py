from setuptools import setup, find_packages

setup(
    name='stims',
    version='0.1.0',
    packages=find_packages(include=['stims']),
    license='MIT',
    entry_points={
        'console_scripts': [
            'stims = stims.command:run',
        ],
    },
    install_requires=[
        'aiohttp',
        'aiojobs',
        'aiohttp-devtools',
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
            "pytest-asyncio",
            "pytest-coverage"
        ]
    }
)
