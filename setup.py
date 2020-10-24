import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read()

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="simio",
    version="0.0.1",
    author="Nikita Zavadin",
    author_email="zavadin142@gmail.com",
    description="Small, simple and with asyncIO web framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="https://github.com/RB387/Simio",
    packages=["simio"],
    requirements=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
        "Aiohttp :: Web Framework :: Asyncio"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "simio=simio.cli.selector:select_action",
        ]
    },
)
