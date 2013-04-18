from distutils.core import setup

# Read the version number
with open("Cpyx/_version.py") as f:
    exec(f.read())

setup(
    name='Cpyx',
    version=__version__, # use the same version that's in _version.py
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
