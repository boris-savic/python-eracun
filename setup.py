from setuptools import setup, find_packages

setup(
    name='eracun_generator',
    packages=['eracun_generator', 'eracun_generator.envelope'],
    version='0.1.4',
    description='e-SLOG e-Racun v1.6.1 XML generator',
    author='Boris Savic',
    author_email='boris70@gmail.com',
    url='https://github.com/boris-savic/python-eracun',
    download_url='https://github.com/boris-savic/python-eracun/tarball/0.1.4',
    keywords=['python eracun', 'e-racun', 'e-slog'],
    classifiers=[],
    install_requires=[
        'lxml>=4.4.1',
        'signxml>=2.6.0'
    ]
)
