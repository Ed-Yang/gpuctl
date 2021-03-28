from distutils.core import setup

from setuptools import find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='gpuctl',
    version='0.2',
    packages=find_packages(),
    url='https://github.com/Ed-Yang/gpuctl',
    license='MIT',
    author='Edward Yang',
    author_email='edwardyangyang@hotmail.com',
    description='GPU contorl and failure notification',
    long_description=readme,
    keywords='gpu amd nvidia ai pytorch tensorflow torch mining ethereum bitcoin cryptocurrency ethminer nsfminer phoenixminer',
    python_requires='>=3',
    install_requires=[
        'pynvml'
    ],
    entry_points="""
        [console_scripts]
        gpuctl=gpuctl.main:run
    """,
)

