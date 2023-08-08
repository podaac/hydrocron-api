#!/usr/bin/env bash

set -Eexo pipefail

# Read in args from command line

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --ticket)
    ticket="$2"
    shift # past argument
    shift # past value
    ;;
    --app-version)
    app_version="$2"
    shift # past argument
    shift # past value
    ;;
    -v|--tf-venue)
    tf_venue="$2"
    case $tf_venue in
     sit|uat|ops) ;;
     *)
        echo "tf_venue must be sit, uat, or ops"
        exit 1;;
    esac
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters




PACKAGE_NAME="hydrocron"
VERSION="0.0.1"

ROOT_PATH="$PWD"
ZIP_PATH="$ROOT_PATH/$PACKAGE_NAME-$VERSION.zip"

mkdir -p "$ROOT_PATH/"
rm -f "$ZIP_PATH"
zip -vr9 "$ZIP_PATH" .







# https://www.terraform.io/docs/commands/environment-variables.html#tf_in_automation
TF_IN_AUTOMATION=true

if [[ "${ticket}" ]]; then
  set +e
  terraform workspace new "${ticket}"
  set -e
  terraform workspace select "${ticket}"
else
  terraform workspace select default
fi
