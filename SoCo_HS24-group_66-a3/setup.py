from setuptools import setup, find_packages

setup(
    name="mytig",  # Renamed to avoid conflict with the existing tig tool
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mytig=tig.tig:main',  # Command renamed to "mytig"
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
