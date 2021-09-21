conda env export --no-builds | grep -v "prefix" > environment-freeze.yml
