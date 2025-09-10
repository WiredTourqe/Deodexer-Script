from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="deodexer-pro",
    version="2.0.0",
    author="WiredTourqe",
    author_email="",
    description="Advanced Android Deodexer with GUI and comprehensive analysis tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WiredTourqe/Deodexer-Script",
    project_urls={
        "Bug Tracker": "https://github.com/WiredTourqe/Deodexer-Script/issues",
        "Documentation": "https://github.com/WiredTourqe/Deodexer-Script/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Operating System",
        "Topic :: Utilities",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "ml": [
            "tensorflow>=2.13.0",
            "torch>=2.0.0",
            "transformers>=4.30.0",
        ],
        "api": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "redis>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deodexer-pro=deodexer_pro.main:main",
            "deodexer-cli=deodexer_pro.cli:main",
            "deodexer-gui=deodexer_pro.gui.main:main",
            "deodexer-api=deodexer_pro.api.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "deodexer_pro": [
            "data/templates/*.json",
            "data/samples/*.odex",
            "config/*.yaml",
            "gui/assets/*.png",
            "gui/assets/*.ico",
        ],
    },
)