import __version__
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SPmodelling",
    version=__version__.__version__,
    author="Penelope Faulkner Rainford",
    author_email="faulknerrainford@gmail.com",
    description="Socio-Physical Modelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faulknerrainford/SPmodelling",
    packages=['SPmodelling'],
    nstall_requires=[
        'neo4j',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
