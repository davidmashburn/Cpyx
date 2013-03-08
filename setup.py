from distutils.core import setup

setup(
    name='Cpyx',
    version='0.1.2',
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['Cpyx'],
    scripts=[],
    url='http://pypi.python.org/pypi/Cpyx/',
    license='LICENSE.txt',
    description='gcc/distutils wrapper for auto-compiling Cython code (including inline)',
    long_description=open('README.rst').read(),
    install_requires=[],
)
