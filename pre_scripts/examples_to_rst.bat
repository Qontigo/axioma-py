cd ..
jupyter nbconvert --output-dir='./docs/examples' --to rst --ClearOutputPreprocessor.enabled=True ./axioma-py/examples/*.ipynb