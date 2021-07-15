from setuptools import find_packages, setup

setup(
    name='taggr',
    version='0.1.10',
    description='Tag creator for Square.',
    author='Jeremy Bywater',
    author_email='jeremy@bywater.me',
    license='Apache Software License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'squareup',
        'treepoem',
        'pillow'
    ],
)