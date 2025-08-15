from setuptools import setup, find_packages

setup(
    name="wildeditor-mcp-server",
    version="1.0.0",
    description="Model Context Protocol server for Wildeditor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.25.0",
        # "mcp>=1.0.0",  # Will be added when available
        "wildeditor-auth>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "mypy>=1.5.0",
            "flake8>=6.0.0",
        ]
    },
)
