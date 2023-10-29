import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cleantimer",
    version="0.0.2",
    license="GPLv3",
    author="Alec Ostrander",
    url="https://github.com/alecglen/cleantimer",
    description="Track progress of long-running scripts, without cluttering your code with log statements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords=["time", "timer", "progress"],
    python_requires=">=3.6",
    py_modules=["cleantimer"],
    # package_dir={"": "cleantimer"},
    install_requires=["contexttimer", "tqdm", "pandas"],
)
