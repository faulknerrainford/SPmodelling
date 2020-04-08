import __version__
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SPmodelling", # Replace with your own username
    version=__version__.__version__,
    author="Penelope Faulkner Rainford",
    author_email="faulknerrainford@gmail.com",
    description="Socio-Physical Modelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)