import os
from copy import deepcopy

from moto import mock_aws
import pandas as pd
from degrades_daily_summary.main import (
    lambda_handler,
    generate_report_from_dynamo_query,
)
from tests.conftest import TEST_DEGRADES_DATE, mock_s3_service, MOCK_BUCKET, readfile
from tests.mocks.dynamo_response.degrade_table import simple_message_timestamp
from boto3.dynamodb.conditions import Key


@mock_aws
def test_degrades_daily_summary_lambda_queries_dynamo(
    set_env,
    context,
    mock_dynamo_service,
    mock_table,
    mock_scheduled_event,
    mock_s3_service,
):
    lambda_handler(mock_scheduled_event, context)
    mock_dynamo_service.query.assert_called()


@mock_aws
def test_degrades_daily_summary_uses_trigger_date_to_query_dynamo(
    set_env,
    context,
    mock_dynamo_service,
    mock_table,
    mock_scheduled_event,
    mock_s3_service,
):
    lambda_handler(mock_scheduled_event, context)
    mock_dynamo_service.query.assert_called_with(
        key="Timestamp",
        condition=simple_message_timestamp,
        table_name=mock_table.table_name,
    )


@mock_aws
def test_generate_report_from_dynamo_query_result(mock_table_with_files, mocker):
    mocker.patch(
        "degrades_daily_summary.main.get_degrade_totals_from_degrades"
    ).return_value = pd.DataFrame(
        [
            {"Type": "MEDICATION", "Reason": "CODE", "Count": 3},
            {"Type": "NON_DRUG_ALLERGY", "Reason": "CODE", "Count": 1},
            {"Type": "RECORD_ENTRY", "Reason": "CODE", "Count": 1},
        ]
    )

    degrades_from_table = mock_table_with_files.query(
        KeyConditionExpression=Key("Timestamp").eq(simple_message_timestamp)
    )["Items"]

    generate_report_from_dynamo_query(degrades_from_table, TEST_DEGRADES_DATE)

    expected = readfile(f"{os.getcwd()}/tests/reports/{TEST_DEGRADES_DATE}.csv")
    with open(f"/tmp/{TEST_DEGRADES_DATE}.csv", "r") as file:
        actual = file.read()
        assert actual == expected
    os.remove(f"/tmp/{TEST_DEGRADES_DATE}.csv")


@mock_aws
def test_degrades_daily_summary_generates_report(
    mock_scheduled_event,
    context,
    set_env,
    mocker,
    mock_table_with_files,
    mock_s3_service,
):
    mock_generate_report = mocker.patch(
        "degrades_daily_summary.main.generate_report_from_dynamo_query"
    )

    degrades = mock_table_with_files.query(
        KeyConditionExpression=Key("Timestamp").eq(simple_message_timestamp)
    )["Items"]

    lambda_handler(mock_scheduled_event, context)

    mock_generate_report.assert_called_with(degrades, TEST_DEGRADES_DATE)


@mock_aws
def test_degrades_daily_summary_uploads_to_s3(
    mock_scheduled_event,
    context,
    set_env,
    mock_s3_service,
    mock_table_with_files,
):
    lambda_handler(mock_scheduled_event, context)

    mock_s3_service.upload_file.assert_called_with(
        file="/tmp/2024-09-20.csv",
        bucket_name=MOCK_BUCKET,
        key="reports/daily/2024-09-20.csv",
    )
    os.remove(f"/tmp/{TEST_DEGRADES_DATE}.csv")


@mock_aws
def test_daily_summary_calls_generate_weekly_report_on_a_monday(
    mock_scheduled_event, context, set_env, mocker, mock_dynamo_service, mock_s3_service
):
    mock_dynamo_service.query.return_value = ["object returned"]
    mocker.patch("degrades_daily_summary.main.generate_report_from_dynamo_query")
    mock_generate_weekly_report = mocker.patch(
        "degrades_daily_summary.main.generate_weekly_report"
    )

    MONDAY_EVENT = deepcopy(mock_scheduled_event)
    MONDAY_EVENT["time"] = "2024-09-23T06:00:00Z"
    lambda_handler(MONDAY_EVENT, context)

    mock_generate_weekly_report.assert_called_with("2024-09-16")


@mock_aws
def test_generate_weekly_report_is_not_called_not_monday(
    mock_scheduled_event, context, set_env, mock_s3_service, mock_dynamo_service, mocker
):
    mock_dynamo_service.query.return_value = ["object returned"]
    mocker.patch("degrades_daily_summary.main.generate_report_from_dynamo_query")
    mock_generate_weekly_report = mocker.patch(
        "degrades_daily_summary.main.generate_weekly_report"
    )

    lambda_handler(mock_scheduled_event, context)

    mock_generate_weekly_report.assert_not_called()
