#!/bin/bash

# Script to:
# clean up any auto created .rst files interactive confirm
# clean the notebooks that form part of the docs and put them in docs folder
# Prepare the attachments.zip
# build the docs

# setup the folders 
source create_folders.sh

# from pre_scripts
pushd ../docs

pushd classes

read -p "Do you want to delete docs classes files (y/n)?" CONT

if [ "$CONT" == "y" ]; then

    rm -f *.rst
    #giving eror on this line
    echo "Deleted";
fi

popd
popd

source _build_docs.sh