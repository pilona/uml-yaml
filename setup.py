from setuptools import setup, find_packages
from glob import glob


setup(
    name='uml-yaml',
    version='0.1',
    author='Alex Pilon',
    description='WYSIWYM YAML to UML/dot diagram generator.',
    url='https://github.com/pilona/uml-yaml',
    author_email='alp@alexpilon.ca',
    license='ISC',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
    ],
    scripts=glob('bin/*'),
)
