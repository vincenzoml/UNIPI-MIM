"""
Setup configuration for Markdown Slides Generator.

Professional Python package setup with proper metadata, dependencies,
and entry points for CLI installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-')
        ]

# Extract only production dependencies (exclude dev dependencies)
production_requirements = [
    req for req in requirements 
    if not any(dev_pkg in req for dev_pkg in ['pytest', 'black', 'flake8', 'mypy', 'sphinx', 'isort'])
]

setup(
    name="markdown-slides-generator",
    version="0.1.0",
    author="Markdown Slides Generator Team",
    author_email="contact@example.com",
    description="Convert academic markdown into beautiful slides and comprehensive notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/markdown-slides-generator",
    project_urls={
        "Bug Reports": "https://github.com/example/markdown-slides-generator/issues",
        "Source": "https://github.com/example/markdown-slides-generator",
        "Documentation": "https://markdown-slides-generator.readthedocs.io/",
    },
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    
    # Dependencies
    install_requires=production_requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-click>=4.4.0",
        ],
        "rich": [
            "rich>=13.0.0",
            "colorama>=0.4.6",
            "tqdm>=4.64.0",
        ]
    },
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "markdown-slides=markdown_slides_generator.cli:main",
            "mdslides=markdown_slides_generator.cli:main",  # Short alias
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research", 
        "Topic :: Education",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business :: Office Suites",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="markdown slides presentation academic lecture notes quarto reveal.js",
    python_requires=">=3.8",
    
    # Additional metadata
    zip_safe=False,
    platforms=["any"],
)