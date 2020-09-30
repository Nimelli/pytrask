import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytrask-Nimelli", # Replace with your own username
    version="0.0.1",
    author="Nimelli",
    author_email="",
    description="Minimalist Kanban task management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nimelli/pytrask",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)