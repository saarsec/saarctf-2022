#!/bin/bash

set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTPUT_DIR="$SCRIPT_DIR/../../../checkers/sites/cdnstore"
mkdir -p "$OUTPUT_DIR"

# npm i
#npx purgecss --css semantic/dist/semantic.min.css -o semantic/dist/semantic.min2.css --content src/index.html -font

# build all themes
cd semantic
for CFG in src/theme-*.config; do
  THEME=${CFG:9:-7}
  echo "CFG=$CFG THEME=$THEME"
  cp "$CFG" src/theme.config
  npx gulp build-css
  npx purgecss --css dist/semantic.min.css -o "$OUTPUT_DIR/semantic$THEME.min.css" -font \
    --content ../src/index.html --content ../../admincheck/src/index.html --content ../../admincheck/src/colors.html --content ../../issues/src/index.html
done
cd ..

npx html-minifier src/index.html -o "$OUTPUT_DIR/index.html" --collapse-whitespace --remove-comments --remove-optional-tags --remove-redundant-attributes --remove-script-type-attributes --minify-css true --minify-js true
sed -i 's|semantic/semantic.min.css|semantic.min.css|' "$OUTPUT_DIR/index.html"
ls -lh "$OUTPUT_DIR"
