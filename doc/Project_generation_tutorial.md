# Project generation tutorial

## Create distribution

```bash
python setup.py sdist bdist_wheel
```

## Install it

```bash
python -m pip install --upgrade --force-reinstall dist/blockchain-*.*.*-py3-none-any.whl
```

or 

```bash
python -m pip install --upgrade -e src/
```

replace * with the version you are using

## Publish it

python -m twine upload dist/*
