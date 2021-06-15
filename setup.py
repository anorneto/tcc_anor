from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tcc_anor',

    version='0.0.1',

    description='Api para Scrapping de Websites',
    long_description_content_type="text/markdown",
    long_description=long_description,

    url='https://github.com/anorneto/tcc_anor',

    author='Anor Neto',
    author_email='anornetoo@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 1- Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='scraping - scraper - api',

    packages=find_packages(
        include=['aplicacao', 'aplicacao.*'], exclude=['contrib', 'docs', 'tests']),

    python_requires='>=3.6',
    install_requires=['requests-html', 'pyppeteer',
                      'fastapi', 'uvicorn', 'pydantic'],
    entry_points={
        'console_scripts': ['tcc-anor=aplicacao.__main__:main']
    },
)
