#!/usr/bin/env bash
set -eo pipefail

if [ ! $# -eq 1 ]
then
    echo "usage: $(caller | cut -d' ' -f2) venue"
    exit 1
fi

VENUE=$1
REGISTRY=$2
IMAGE_NAME=$3

source "$(dirname $BASH_SOURCE)/../environments/$VENUE.env"

export TF_IN_AUTOMATION=true  # https://www.terraform.io/cli/config/environment-variables#tf_in_automation
export TF_INPUT=false  # https://www.terraform.io/cli/config/environment-variables#tf_input

export TF_VAR_region="$REGION"
export TF_VAR_stage="$VENUE"

export TF_VAR_REGISTRY="$REGISTRY"
export TF_VAR_IMAGE_NAME="$IMAGE_NAME"


terraform init -reconfigure -backend-config="bucket=$BUCKET" -backend-config="region=$REGION"