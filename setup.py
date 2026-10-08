import os
from setuptools import setup, find_packages

# Read the README file for the long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sanskrypt-lang', # Unique name on PyPI
    version='3.0.0',
    description='A root-based, order-agnostic programming language inspired by Paninian grammar.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/sanskrypt', # Update with your repo
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
