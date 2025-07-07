from setuptools import setup, find_packages

setup(
    name="profofconcept10000",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "igraph",            # High-performance graph library
        "matplotlib",        # For graph visualization
        "networkx",          # Optional, for interoperability and testing
        "scipy",             # Useful for scientific computations
        "cryptography",      # For AES-256 encryption
        "pqcrypto",          # For post-quantum ML-KEM encryption
        "tqdm",              # Progress bars for batch processing
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

