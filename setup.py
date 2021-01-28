from setuptools import setup, find_packages

setup(
    name='duplicate-finder', # does not need to be anything related to actual name
    version='0.1.0',
    license='MIT',
    description='A program that intakes a list of directories, and will search them for duplicate videos.',
    author='James Scheiber',
    author_email='jscheiber22@gmail.com',
    url="https://www.scheibertech.com",
    packages=find_packages(include=['duplicatefinder', 'duplicatefinder.*']),  # Not top-most folder, the one with the actual python files should go here
    install_requires=[ # min version not required
        'PyYAML',
        'pandas==0.23.3',
        'numpy>=1.14.5',
        'matplotlib>=2.2.0,,
        'jupyter'
    ]
)
