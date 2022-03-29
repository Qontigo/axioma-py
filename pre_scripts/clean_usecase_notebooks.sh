pushd ..
# clean the examples into the doc folder
# they will be included via nbsphinx (i.e. not converted to rst)
jupyter nbconvert --output-dir='./docs/use_cases' --to notebook --TagRemovePreprocessor.remove_cell_tags="['remove']" --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True ./use_cases/*.ipynb

popd