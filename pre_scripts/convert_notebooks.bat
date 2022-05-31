REM Converts the example notebooks to .rst files. No longer used as render notebooks directly nbsphinx
pushd ..
python ./pre_scripts/notebook_clean.py -s "./axioma-py/examples"
popd