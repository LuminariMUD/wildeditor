from setuptools import setup, find_packages

setup(
    name="wildeditor-auth",
    version="2.0.0",
    description="Shared authentication package for Wildeditor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.14",
    install_requires=[
        "fastapi>=0.141.1",
        "pydantic>=2.13.4",
        "pydantic-settings>=2.14.2",
        "httpx>=0.28.1",
        "PyJWT[crypto]>=2.13.0,<3",
    ],
    extras_require={
        "dev": [
            "pytest>=9.1.1",
            "pytest-asyncio>=1.4.0",
            "httpx2>=2.9.1",
            "mypy>=2.3.0",
            "flake8>=7.3.0",
        ]
    },
)
