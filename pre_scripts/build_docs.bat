call create_folders.bat 

pushd ..\docs
pushd .\classes
DEL *.rst
popd
popd

call clean_example_notebooks.bat

call clean_usecase_notebooks.bat

call prepare_attachments.bat

pushd ..\docs

COPY ..\CHANGELOG.rst changelog.rst /Y

make html
popd
