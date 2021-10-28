from setuptools import setup

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


setup(
    name='FrontierData',
    version='1.0',
    description='Methods for extracting and analyzing Frontier data',
    author='Millissa Si Amer',
    author_email='millissa.si.amer@cern.ch',
    license='CERN',
    packages=['FrontierData', 'FrontierData.Config', 'FrontierData.DataExtraction'],
    install_requires=['elasticsearch >= 7.14.0', 'pyarrow >= 0.13.0',
                      'pandas >= 0.23.4', ],  # external packages as dependencies
    long_description="""\
    This package allows users to extract Frontier logs data and parse the extracted rows and calculate the caching efficiency. 
    """
)
