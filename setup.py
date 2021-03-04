from setuptools import setup, find_packages

setup(
    name='zoom_korokesu',
    packages=find_packages(exclude=['tests']),

    install_requires=['pyserial'],
)
