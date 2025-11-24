from setuptools import setup, find_packages

setup(
    name="console-iot-cli",
    version="1.0.0",
    description="Una herramienta de línea de comandos para comunicación serial.",
    author="Nicolás Pinochet Flores",
    license="CC BY-NC-SA 4.0",
    packages=find_packages(),
    py_modules=["cli_main"],
    install_requires=[
        "pyserial",
    ],
    entry_points={
        "console_scripts": [
            "console-iot=cli_main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    python_requires='>=3.6',
)
