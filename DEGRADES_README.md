# Degrades-Reporting
To collect data around the number and different types of degrade events received from GP2GP
Degrades events received by event-enrichment lambda are sent to an degrades SQS queue which triggers degrades-message-receiver lambda.
The degrades-message-receiver lambda writes this events to a dynamo table to be later queried.

## Set-up

Setting up virtual venv

`make degrades-env`
Install dependencies needed for degrades work


## Local deployment

To use localstack to deploy the degrades-reporting work locally, create a local.auto.tfvars within the terraform directory
add the following variables to this file
environment="dev"
region="eu-west-2"
registrations_mi_event_bucket="bucket"
degrades_message_queue="queue"
degrades_message_table="table"

This isn't necessary but will require manual input if not present.

`make deploy-local`
Deploy degrades infrastructure to local environment using localstack



### Localstack Limitations:
Lambda layers are not implemented/connected to lambdas on the standard/community tier. 
They will be created however.
IAM Permission relationships are not enforced on the standard/community tier

## Testing

`make test-degrades`
Runs python unit tests for degrades work

`make test-degrades-coverage`
Runs python unit tests for degrades with coverage reporting

## Zipping Lambdas for manual deployment

`make zip-lambda-layer`
Creates a lambda layer zip file => stacks/degrades-dashboards/terraform/lambda/build

`make zip-degrades-lambda`
Creates a lambda layer zip and zip files of degrades lambdas => stacks/degrades-dashboards/terraform/lambda/build
This is used in deployment workflows