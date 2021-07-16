from setuptools import find_packages, setup

setup(
    name='taggr',
    version='0.2.0',
    description='Tag creator for Square.',
    author='Jeremy Bywater',
    author_email='jeremy@bywater.me',
    license='Apache Software License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-wtf',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-login',
        'squareup',
        'treepoem',
        'pillow'
    ],
)