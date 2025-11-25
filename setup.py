from setuptools import setup, find_packages

setup(
    name="console-iot-cli",
    version="2.0.0",
    description="Herramienta CLI para comunicación serial, TCP y UDP - Alternativa a Hercules SETUP Utility.",
    author="Nicolás Pinochet",
    license="CC BY-NC-SA 4.0",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.5",
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "console-iot=console_iot.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    python_requires='>=3.6',
)
