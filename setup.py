from setuptools import setup, find_packages

setup(
    name="yc-ai-scraper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "scrapy>=2.11.0",
        "pandas>=1.5.0",
        "requests>=2.28.0",
        "lxml>=4.9.0",
        "cssselect>=1.2.0",
    ],
    author="YC AI Scraper",
    description="Scraper for Y Combinator AI companies",
    python_requires=">=3.8",
)