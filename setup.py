from setuptools import setup, find_packages

setup(
    name="unified-threat-detection",
    version="1.0.0",
    description="AI-Powered Unified Cyber Threat Detection Platform",
    author="Hakan",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        line.strip() 
        for line in open("requirements.txt").readlines()
        if not line.startswith("#")
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)