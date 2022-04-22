from setuptools import setup, find_packages

setup(
    name='epsn',
    version='0.1',
    license="Apache 2.0",
    author="Collin J. Kovacs",
    author_email="collin.graduate@gmail.com",
    packages=find_packages("epsn"),
    package_dir={'':'epsn'},
    url="https://github.com/cjk5642/EPSN",
    keywords='epsn',
    install_requires=[
        'sportsipy',
        'pandas',
        'itertools',
        'datetime',
        'tqdm'
    ]
)