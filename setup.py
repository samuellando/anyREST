from setuptools import setup

setup(
    name='anyrest',
    version='0.2.1',
    py_modules=['anyrest', 'validator', 'firestore', 'mongodb', 'anyrestHandlers'],
    install_requires=[
        'flask',
        'firebase-admin',
        'AuthLib',
        'flask-cors',
        'pymongo'
    ],
)
