from setuptools import setup

setup(
    name='anyrest',
    version='0.1.4',
    py_modules=['anyrest', 'validator'],
    install_requires=[
        'flask',
        'firebase-admin',
        'AuthLib',
        'flask-cors'
    ],
)
