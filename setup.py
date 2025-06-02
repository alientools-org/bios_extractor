from setuptools import setup, find_packages

setup(
    name="bios_extractor",
    version="0.1.0",
    author="hexzhen3x7",
    author_email="hexzhen3x7@blackzspace.de",
    description="BIOS Update Extraktor für ISO und EXE Dateien",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/alientools-org/bios_extractor",  # falls vorhanden
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'bios-extract=bios_extractor.cli:main',
        ],
    },
    install_requires=[
        # keine externen Anforderungen bisher
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
)
