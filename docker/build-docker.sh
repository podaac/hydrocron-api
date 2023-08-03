#!/usr/bin/env bash

# This script is intended to be run by the CI/CD pipeline to build a specific version of the FTS API.

set -Eeo pipefail

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -n|--service-name)
    service_name="$2"
    shift # past argument
    shift # past value
    ;;
    -v|--service-version)
    service_version="$2"
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

USAGE="USAGE: build-docker.sh -n|--service-name service_name -v|--service-version service_version"

# shellcheck disable=SC2154
if [[ -z "${service_name}" ]]; then
  echo "service_name required. Name of the service as found in pyproject.toml (e.g. podaac-staging)" >&2
  echo "$USAGE" >&2
  exit 1
fi

# shellcheck disable=SC2154
if [[ -z "${service_version}" ]]; then
  echo "service_version required. Version of software to install (e.g. 0.1.0-a1+12353)." >&2
  echo "$USAGE" >&2
  exit 1
fi

set -u

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROJECT_DIR="$(dirname "${SCRIPTPATH}")"

repositoryName=podaac/podaac-cloud/${service_name}

# Docker tags can't include '+' https://github.com/docker/distribution/issues/1201
dockerTagVersion=$(echo "${service_version}" | tr "+" _)

tar_filename="${service_name}-${service_version}.tar.gz"
docker build -t "${repositoryName}":"${dockerTagVersion}" --build-arg SOURCE="dist/${tar_filename}" -f "$SCRIPTPATH"/Dockerfile "$PROJECT_DIR" 1>&2

echo "${repositoryName}":"${dockerTagVersion}"