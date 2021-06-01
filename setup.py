"""Setup script."""

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zoom_kurokesu',
    version='1.1.0',
    packages=find_packages(exclude=['tests']),

    install_requires=['pyserial'],

    extra_requires={
        'test': ['pytest'],
    },

    author='Pollen Robotics',
    author_email='contact@pollen-robotics.com',
    url='https://github.com/pollen-robotics/zoom_kurokesu',

    description="Python Package for controlling the zoom of Kurokesu's camera.",
    long_description=long_description,
    long_description_content_type='text/markdown',
)
