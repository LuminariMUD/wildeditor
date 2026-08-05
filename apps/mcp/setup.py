from setuptools import setup, find_packages

setup(
    name="wildeditor-mcp-server",
    version="1.0.0",
    description="Model Context Protocol server for Wildeditor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.14",
    install_requires=[
        "fastapi>=0.141.1",
        "uvicorn[standard]>=0.52.1",
        "pydantic>=2.13.4",
        "pydantic-settings>=2.14.2",
        "httpx>=0.28.1",
        "pydantic-ai-slim[openai,anthropic]>=2.24.0",
        "openai>=2.53.0",
        "anthropic>=0.120.2",
        "wildeditor-auth>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=9.1.1",
            "pytest-asyncio>=1.4.0",
            "mypy>=2.3.0",
            "flake8>=7.3.0",
        ]
    },
)
