from pathlib import Path
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

def glob_fix(package_name, glob):
    # this assumes setup.py lives in the folder that contains the package
    package_path = Path(f'./{package_name}').resolve()
    return [str(path.relative_to(package_path)) 
            for path in package_path.glob(glob)]

setuptools.setup(
    name='paideia_contracts',  
    version='1.0.1',
    my_packages=['paideia_contracts'],
    author="Robert Pieter van Leeuwen",
    author_email="luivatra@gmail.com",
    description="ErgoScript and Python wrappers for Paideia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ergo-pad/paideia-contracts",
    package_data={'paideia_contracts': [*glob_fix('paideia_contracts', '**/*.es')]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'ergo_python_appkit>=0.1.0',
        'requests>=2.27.1'
    ]
 )