from setuptools import setup

setup(
    name='anyrest',
    version='0.2.2',
    py_modules=['anyrest', 'validator', 'firestore', 'mongodb', 'testing','anyrestHandlers'],
    install_requires=[
        'flask',
        'firebase-admin',
        'AuthLib',
        'flask-cors',
        'pymongo',
        'mongomock'
    ],
)
