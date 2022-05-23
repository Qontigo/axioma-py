pushd ..

REM clean the examples into the doc folder
REM they will be included via nbsphinx (i.e. not converted to rst)
jupyter nbconvert --output-dir='./docs/nb_examples' --to notebook --TagRemovePreprocessor.remove_cell_tags="['remove']" --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True ./axioma-py/examples/*.ipynb

popd