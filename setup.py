from setuptools import setup, find_packages

setup(
    name="watch-podcast-download",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],  # Ajoutez les dépendances ici si nécessaire
)
