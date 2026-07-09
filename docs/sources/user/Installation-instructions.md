# Installation instructions

## pip

**Note that using pip outside virtualenv is not recommended since it ignores
your systems package manager. If you aren't comfortable debugging package
installation issues use virtualenv.**

Create and activate a virtualenv:

```bash
virtualenv dtfabric_venv
cd dtfabric_venv
source ./bin/activate
```

Upgrade pip and install dtFabric:

```bash
pip install --upgrade pip
pip install dtfabric
```

To deactivate the virtualenv run:

```bash
deactivate
```
