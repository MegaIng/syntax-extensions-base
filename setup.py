from setuptools import setup, find_packages, find_namespace_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='syntax_extensions_base',

    version='0.0.1',

    description='A base package to facilitate implementation of new syntax ideas',
    
    url='https://github.com/MegaIng/syntax-extensions',

    author='MegaIng', 
    author_email='trampchamp@hotmail.de',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3', # TODO: to be decided
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='syntax-extensions, development',  # Optional

    package_dir={'': 'src'},

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    py_modules=['__syntax_extensions__'],
    packages=find_namespace_packages(where='src'),  # Required

    python_requires='>=3.7, <4',  # TODO: to be decided
    install_requires=[],
    extras_require={
    },

    package_data={
    },

    data_files=[],
    entry_points={
    },

    # project_urls={
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
)
