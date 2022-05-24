#!/bin/bash

set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTPUT_DIR="$SCRIPT_DIR/../../../checkers/sites/lambdaadmin"
mkdir -p "$OUTPUT_DIR"

cd ../contentseller
npx html-minifier ../admincheck/src/index.html -o "$OUTPUT_DIR/index.html" --collapse-whitespace --remove-comments --remove-optional-tags --remove-redundant-attributes --remove-script-type-attributes --minify-css true --minify-js true
sed -i 's|semantic/semantic.min.css|semantic.min.css|' "$OUTPUT_DIR/index.html"
ls -lh "$OUTPUT_DIR"
