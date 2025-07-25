# Degrades-Reporting
To collect data around the number and different types of degrade events received from GP2GP
Degrades events received by event-enrichment lambda are sent to a Degrades SQS queue which triggers degrades-message-receiver lambda.
The degrades-message-receiver lambda writes these events to a DynamoDB table to be later queried for reports generation. These reports are
written to CSV and stored in an S3 bucket, under paths reports/ and reports/daily/, to be consumed by PowerBi for the creation of dashboards.

![](degrades_architecture.svg)


As we already have a check in the gp-registrations-mi lambda against whether an event is a degrade event or not, it was decided to use
this lambda to send any degrades events to an SQS queue to be processed.
The alternative was to read every gp2gp event received each day from S3 to determine its event type, and only store or process degrades found.

## Set-up

Setting up virtual venv

`make degrades-env`
Install dependencies needed for degrades work

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

## Scripts

There are 3 adhoc scripts that have been used to prepopulate the dev environment with historical data held within S3.
Each will need environmental variables defined, which can be found in AWS, bucket name, queue name, table name, and region.
The terminal they are run from/tool used to run them will also need to be granted permission to be able to interact with these AWS resources.

### populate_table.py 
Loops through the S3 bucket where enriched gp registration events are stored by date prefix, on dev this can be YYYY/MM as there is
relatively little data held there, sending degrade events to a queue to be written to the degrades event dynamo table.

### generate_daily_report.py
Reads degrades dynamo table for a given date YYYY-MM-DD to generate a daily summary of this data and store in S3 reports/daily/YYYY-MM-DD.csv
Headers are: Type, Reason, Count 

### generate_weekly_report.py
Collects reports for a week, 7 days, starting from date YYYY-MM-DD, summarises the data within these reports and appends new rows 
to an existing report, creates new report if one does not exist.
Headers are: Week_beginning, Type, Reason, Count 

