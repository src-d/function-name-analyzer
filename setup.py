from importlib.machinery import SourceFileLoader

from setuptools import setup, find_packages

fna = SourceFileLoader("fna", "./fna/__init__.py").load_module()

setup(
    name="lookout-function-name",
    description="Machine learning-based assisted code review - function name analyzer.",
    version=".".join(map(str, fna.__version__)),
    license="AGPL-3.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/function-name-analyzer",
    download_url="https://github.com/src-d/function-name-analyzer",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["function-name=fna.__main__:main"],
    },
    keywords=["machine learning on source code", "babelfish"],
    install_requires=[],  # Please install dependencies with requirements.txt
    package_data={"": ["LICENSE.md", "README.md"], },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Quality Assurance"
    ]
)
