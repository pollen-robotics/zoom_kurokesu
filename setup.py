from setuptools import setup, find_packages

setup(
    name='optical_zoom',
    packages=find_packages(exclude=['tests']),

    install_requires=['pyserial'],
)
