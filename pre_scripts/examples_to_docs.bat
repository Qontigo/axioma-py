cd ..
jupyter nbconvert --output-dir='./docs/nb_examples' --to notebook --ClearMetadataPreprocessor.enabled=True --ClearOutputPreprocessor.enabled=True ./axioma-py/examples/*.ipynb