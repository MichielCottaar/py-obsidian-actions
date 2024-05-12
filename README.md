[![PyPI - Downloads](https://img.shields.io/pypi/dm/py-obsidian-actions)](https://pypi.org/project/py-obsidian-actions/)
[![Documentation](https://img.shields.io/badge/Documentation-py-obsidian-actions-blue)](https://open.win.ox.ac.uk/pages/MichielCottaar/py-obsidian-actions)
[![Pipeline status](https://github.com/MichielCottaar/py-obsidian-actions/badges/main/pipeline.svg)](https://github.com/MichielCottaar/py-obsidian-actions/-/pipelines/latest)
[![Coverage report](https://github.com/MichielCottaar/py-obsidian-actions/badges/main/coverage.svg)](https://open.win.ox.ac.uk/pages/MichielCottaar/py-obsidian-actions/htmlcov)

Python interface to the obsidian-actions-uri (https://github.com/czottmann/obsidian-actions-uri).
This package is still in alpha stage and being actively written.

# Installation
```shell
pip install git+https://github.com/MichielCottaar/py-obsidian-actions.git
```

Any bug reports and feature requests are very welcome (see [issue tracker](https://github.com/MichielCottaar/py-obsidian-actions/-/issues)).

# Setting up local test environment
First clone the repository:
```shell
pip install https://github.com/MichielCottaar/py-obsidian-actions.git
```

Then, we install the package in an interactive manner:
```shell
cd py-obsidian-actions
pip install -e .
```

Development tools can be installed using:
```
pip install -r requirements_dev.txt
pre-commit install  # installs pre-commit hooks to keep the code clean
```
[Pull requests](https://github.com/MichielCottaar/py-obsidian-actions/pulls) with any bug fixes are always welcome.

For new features, please raise an [issue](https://github.com/MichielCottaar/py-obsidian-actions/issues) to allow for discussion before you spend the time implementing them.

## Releasing new versions
- Run `bump2version` (install using `pip install bump2version`)
- Push to gitlab
- Manually activate the "to_pypi" task in the [pipeline](https://github.com/MichielCottaar/py-obsidian-actions/-/pipelines/latest) to upload to pypi
