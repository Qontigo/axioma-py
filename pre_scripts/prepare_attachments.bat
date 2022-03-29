pushd ..\docs\attach



rmdir /s /q .\credentials\
rmdir /s /q .\sample_data\

DEL /S *.ipynb *.py *.zip *.json

MKDIR credentials sample_data

COPY ..\nb_examples\*
COPY ..\..\axiomapy\examples\load_credentials.py+.\..\axiomapy\examples\load_sample_data.py

pushd .\credentials
COPY ..\..\..\axiomapy\examples\credentials\sample.credentials.json
popd
pushd .\sample_data
COPY ..\..\..\axiomapy\examples\sample_data\*.json
popd



7z a all_examples.zip *

rmdir /s /q .\credentials\
rmdir /s /q .\sample_data\

DEL /S *.ipynb *.py *.json

popd
