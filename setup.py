from setuptools import setup, find_packages

setup(
    name="linkedin_automator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver_manager",
        "python-dotenv",
        "openai",
        "tiktoken",
        "requests",
        "beautifulsoup4",
        "pillow",
        "tkinter",
    ],
    python_requires=">=3.8",
) 