from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-activepieces",
    version="1.0.0",
    description="CLI-Anything harness for Activepieces — control your automation platform from the command line",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-activepieces=cli_anything.activepieces.activepieces_cli:main",
        ],
    },
    package_data={
        "cli_anything.activepieces": ["skills/*.md"],
    },
    python_requires=">=3.10",
)
