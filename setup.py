from setuptools import setup

setup(
    name='eracun_generator',
    packages=['eracun_generator'],
    version='0.1.2',
    description='e-SLOG e-Racun v1.6.1 XML generator',
    author='Boris Savic',
    author_email='boris70@gmail.com',
    url='https://github.com/boris-savic/python-eracun',
    download_url='https://github.com/boris-savic/python-eracun/tarball/0.1.2',
    keywords=['python eracun', 'e-racun', 'e-slog'],
    classifiers=[],
    install_requires=[
        'lxml>=4.4.1',
    ]
)
