from setuptools import setup, find_packages

setup(
    name="spectr",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'requests==2.31.0',
        'pandas'
    ],
    author="Hussain Shah",
    author_email="hussain@getspectr.com",
    description="A python client library for the Spectr API.",
    license="MIT",
    keywords="spectr client api",
    url="https://gitlab.com/getspectr/spectr",
)
