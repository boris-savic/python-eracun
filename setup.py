from setuptools import setup

setup(
    name='eracun',
    packages=['eracun'],
    version='0.1.0',
    description='e-SLOG e-Racun v1.6.1 XML generator',
    author='Boris Savic',
    author_email='boris70@gmail.com',
    url='https://github.com/boris-savic/python-eracun',
    download_url='https://github.com/boris-savic/python-eracun/tarball/0.1.0',
    keywords=['python eracun', 'e-racun', 'e-slog'],
    classifiers=[],
    install_requires=[
        'lxml>=4.4.1',
    ]
)
