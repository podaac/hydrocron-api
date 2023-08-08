#!/bin/bash
set -eo pipefail

PACKAGE_NAME=$(awk -F' = ' '{gsub(/"/,"");if($1=="name")print $2}' pyproject.toml)
VERSION="0_0_1"
ROOT_PATH="$PWD"
ZIP_PATH="$ROOT_PATH/dist/$PACKAGE_NAME-$VERSION.zip"

mkdir -p "$ROOT_PATH/dist/"
rm -f "$ZIP_PATH"
zip -vr9 "$ZIP_PATH" .
