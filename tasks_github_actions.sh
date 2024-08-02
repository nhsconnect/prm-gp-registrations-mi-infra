#!/bin/bash

set -Eeo pipefail


function build_lambda {
    lambda_name=$1
    lambda_services=$2

    build_dir=lambda/build/$lambda_name
    rm -rf $build_dir
    mkdir -p $build_dir

    requirements_file=lambda/$lambda_name/requirements.txt
    if test -f "$requirements_file"; then
        pip install -r $requirements_file -t $build_dir
    fi

    if test "$lambda_services"; then
        cp -r ./$lambda_services $build_dir
    fi
    cp lambda/$lambda_name/*.py $build_dir

    pushd $build_dir
    zip -r -X ../$lambda_name.zip .
    popd
}


build-lambdas)
  build_lambda error-alarm-alert
  build_lambda splunk-cloud-event-uploader
  build_lambda event-enrichment services
  build_lambda s3-event-uploader
;;
*)
  echo "Invalid task: '${task}'"
  exit 1
  ;;
esac

set +e
