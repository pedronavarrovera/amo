from setuptools import setup, find_packages

setup(
    name="profofconcept10000",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    author="Pedro Juan Navarro Vera",
    description="Research app to compute transaction routes in social networks using Dijkstra's algorithm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.7",
)
