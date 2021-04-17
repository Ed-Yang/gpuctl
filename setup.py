#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages

with open('README.md') as f:
    readme = f.read()

exec(open('gpuctl/version.py').read())

# VERSION = '0.3.6'
URL = 'https://github.com/Ed-Yang/gpuctl/archive/refs/tags/' + __version__ + '.tar.gz'

setup(
    name='gpuctl',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/Ed-Yang/gpuctl',
    download_url=URL,
    license='MIT',
    author='Edward Yang',
    author_email='edwardyangyang@hotmail.com',
    description='GPU contorl and failure notification/recovery',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='gpu amd nvidia ai pytorch tensorflow torch mining ethereum bitcoin cryptocurrency ethminer nsfminer phoenixminer',
    python_requires='>=3',
    install_requires=[
        'setuptools',
        'wheel',
        'pynvml'
    ],
    entry_points={
        'console_scripts': [
        'gpuctl=gpuctl.gpu_main:run',
        'ethctl=gpuctl.eth_main:run',]
    },
)

entry_points={
        'console_scripts': [
            'somefunc=yourscript:somefunc',
            'morefunc=yourscript:morefunc',
        ],
    },
