from distutils.core import setup
import sys


requires = [
    'pycurl>=7.19.0',
    'PyYAML>=3.10',
]

if ((sys.version_info.major == 3 and sys.version_info.minor < 3) or
        (sys.version_info.major == 2 and sys.version_info.minor < 7)):
    requires += ['argparse']

setup(
    name='sendspace-cli',
    scripts=['bin/sendspace'],
    version='0.1.2',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=['sendspace'],
    url='https://github.com/Tatsh/sendspace-cli',
    license='LICENSE.txt',
    description='For uploading files to SendSpace from command line.',
    long_description=open('README.txt').read(),
    install_requires=,
)
