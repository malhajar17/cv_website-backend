from setuptools import setup, find_packages

setup(
    name='service_utils',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'pydub',
        'flask-cors'
    ],
    entry_points={
        'console_scripts': [
            'service_utils = service_utils.app:main'
        ]
    }
)
