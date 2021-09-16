from setuptools import setup
import io
import os
import re

MODULE_NAME = 'restyle'
README_PATH = 'README.md'


def _read(*parts, **kwargs):
    filepath = os.path.join(os.path.dirname(__file__), *parts)
    encoding = kwargs.pop('encoding', 'utf-8')
    with io.open(filepath, encoding=encoding) as fh:
        text = fh.read()
    return text


def get_version():
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        _read('{}.py'.format(MODULE_NAME)),
        re.MULTILINE).group(1)
    return version


def get_long_description():
    return _read(README_PATH)


def get_requirements(path):
    content = _read(path)
    return [
        req
        for req in content.split("\n")
        if req != '' and not req.startswith('#')
    ]


setup(
    name=MODULE_NAME.replace('_', '-'),
    py_modules=[MODULE_NAME],
    version=get_version(),
    license='MIT',
    author='Aman Berry',
    author_email='aman.berry725@gmail.com',
    description='Pandas dataframe styler based on pandas_jupyter_paginate by @nvictus',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/am-berry/pandas-restyler',
    keywords=['pandas', 'jupyter', 'paginator', 'restyler'],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    install_requires=get_requirements('requirements.txt'),
    # tests_require=tests_require,
    # extras_require=extras_require,
)
