#!/bin/bash
set -eo pipefail

PACKAGE_NAME=$(awk -F' = ' '{gsub(/"/,"");if($1=="name")print $2}' pyproject.toml)
VERSION=$(poetry version -s)

ROOT_PATH="$PWD"
ZIP_PATH="$ROOT_PATH/dist/$PACKAGE_NAME-$VERSION.zip"

mkdir -p "$ROOT_PATH/dist/"
rm -f "$ZIP_PATH"
zip -vr9 "$ZIP_PATH" .
echo "++++"
echo "$ROOT_PATH/dist/$PACKAGE_NAME-$VERSION.zip"