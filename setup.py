from setuptools import setup
from setuptools import find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='gpuctl',
    version='0.3.5',
    packages=find_packages(),
    url='https://github.com/Ed-Yang/gpuctl',
    download_url='https://github.com/Ed-Yang/gpuctl/archive/refs/tags/v0.3.4.tar.gz',
    license='MIT',
    author='Edward Yang',
    author_email='edwardyangyang@hotmail.com',
    description='GPU contorl and failure notification',
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
