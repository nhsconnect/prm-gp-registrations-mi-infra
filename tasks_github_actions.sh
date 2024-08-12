#!/bin/bash

set -Eeo pipefail

task="$1"

function build_lambda {
    lambda_name=$1
    lambda_services=$2

    build_dir=lambda/build/$lambda_name
    rm -rf $build_dir
    mkdir -p $build_dir

    requirements_file=lambda/$lambda_name/requirements.txt
    if test -f "$requirements_file"; then
        build_lambda_layer $lambda_name
    fi

    if test "$lambda_services"; then
        cp -r ./$lambda_services $build_dir
    fi
    cp lambda/$lambda_name/*.py $build_dir

    pushd $build_dir
    zip -r -X ../$lambda_name.zip .
    popd
}

function build_lambda_layer {
    lambda_name=$1
    build_dir=lambda/build/layer/$lambda_name

    rm -rf $build_dir/python
    mkdir -p $build_dir/python

    requirements_file=lambda/$lambda_name/requirements.txt
    if test -f "$requirements_file"; then
        python3 -m venv create_layer
        source create_layer/bin/activate
        pip install -r $requirements_file
    fi

    cp -r create_layer/lib $build_dir/python
    pushd $build_dir
    zip -r -X ../$lambda_name.zip .
    popd
}

echo "--- ${task} ---"
case "${task}" in
build-lambdas)
  build_lambda bulk-ods-update utils
  build_lambda error-alarm-alert
  build_lambda splunk-cloud-event-uploader
  build_lambda event-enrichment utils
  build_lambda s3-event-uploader
;;
*)
  echo "Invalid task: '${task}'"
  exit 1
  ;;
esac

set +e
