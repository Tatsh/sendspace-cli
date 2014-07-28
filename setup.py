from distutils.core import setup

setup(
    name='sendspace-cli',
    scripts=['bin/sendspace'],
    version='0.1.1',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=['sendspace'],
    url='https://github.com/Tatsh/sendspace-cli',
    license='LICENSE.txt',
    description='For uploading files to SendSpace from command line.',
    long_description=open('README.txt').read(),
    install_requires=[
        'pycurl>=7.19.0',
        'PyYAML>=3.10',
    ],
)
