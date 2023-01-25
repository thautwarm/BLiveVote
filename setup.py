from setuptools import setup
from datetime import datetime
from pathlib import Path


version = 0.1

with Path('README.md').open(encoding='utf-8') as readme:
    readme = readme.read()

setup(
    name='BLiveVote',
    version=version if isinstance(version, str) else str(version),
    keywords="", # keywords of your project that separated by comma ","
    description="", # a concise introduction of your project
    long_description=readme,
    long_description_content_type="text/markdown",
    license='mit',
    python_requires='>=3.6.0',
    url='https://github.com/thautwarm/BLiveVote/',
    author='thautwarm',
    author_email='twshere@outlook.com',
    package_dir={
        'BLiveVote': 'BLiveVote',
        'BLiveVote.blivedm': '3rd/blivedm/blivedm'
    },
    packages=['BLiveVote', 'BLiveVote.blivedm'],
    entry_points={"console_scripts": [
        'blivevote=BLiveVote.cli:main',
    ]},
    # above option specifies what commands to install,
    # e.g: entry_points={"console_scripts": ["yapypy=yapypy.cmd:compiler"]}
    install_requires=[
        'aiohttp==3.7.4',
        'Brotli==1.0.9',
        'wisepy2',
        'dataset',
        'loguru',
    ], # dependencies
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    zip_safe=False,
)
