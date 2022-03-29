
# from pre_scripts
source clean_example_notebooks.sh


source clean_usecase_notebooks.sh

# from pre_scripts
pushd ../docs/attach

# empty the folder 

rm -fr credentials sample_data

rm -f *.ipynb *.py *.zip *.json

mkdir credentials sample_data

# copy the files needed
cp ../nb_examples/* .
cp ../../axiomapy/examples/load_credentials.py .
cp ../../axiomapy/examples/load_sample_data.py .

pushd ./credentials
cp ../../../axiomapy/examples/credentials/sample.credentials.json .
popd

pushd ./sample_data
cp ../../../axiomapy/examples/sample_data/*.json .
popd

# creates gzip
# tar -cvzf all_examples.zip *

# might need to install zip for your shell if running on windows
zip -r all_examples.zip *


# clean up again apart from the zip
rm -fr credentials sample_data

rm -f *.ipynb *.py  *.json

popd

pushd ../docs

cp ../CHANGELOG.rst changelog.rst

sphinx-build -b html . _build/html

popd
