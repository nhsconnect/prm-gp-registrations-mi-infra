import os
import csv
from unittest.mock import call
import boto3
import pandas as pd
from moto import mock_aws

from degrade_utils.generate_weekly_reports import (
    generate_weekly_report,
    get_keys_from_date_range,
    generate_weekly_summary,
)


def test_get_keys_from_date_range():
    expected = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]
    assert get_keys_from_date_range("2024-09-16") == expected


def test_generate_weekly_summary_summarises_weekly_data(mock_s3, set_env):
    files = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    for file in files:
        mock_s3.upload_file(f"./tests/reports/{file}.csv", f"reports/daily/{file}.csv")

    actual = generate_weekly_summary(files, "2024-09-16")
    expected = {"Count": {('DRUG_ALLERGY', 'CODE'): 2, ('MEDICATION', 'CODE'): 21, ('NON_DRUG_ALLERGY', 'CODE'): 8,
                          ('RECORD_ENTRY', 'CODE'): 12, ('RECORD_ENTRY', 'NUMERIC_VALUE'): 6}}
    assert actual == expected




@mock_aws
def test_weekly_report_generation_adds_new_row_to_global_report(set_env, mock_s3, mocker):
    files = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    for file in files:
        mock_s3.upload_file(f"./tests/reports/{file}.csv", f"reports/daily/{file}.csv")

    mock_summary = mocker.patch("degrade_utils.generate_weekly_reports.generate_weekly_summary")

    mock_summary.return_value = {"Count": {('MEDICATION', 'CODE'): 16, ('NON_DRUG_ALLERGY', 'CODE'): 7,
                                           ('RECORD_ENTRY', 'CODE'): 11, ('RECORD_ENTRY', 'NUMERIC_VALUE'): 4,
                                           ('DRUG_ALLERGY', 'CODE'): 2, ('ALLERGY', 'CODE'): 1}}

    mock_s3.upload_file(
        "./tests/reports/global.csv", "reports/degrades_weekly_report.csv"
    )

    generate_weekly_report("2024-09-23")

    mock_s3.download_file(
        Key="reports/degrades_weekly_report.csv",
        Filename="tmp/degrades_weekly_report.csv",
    )
    with (
        open("./tests/reports/global_2.csv", "r") as expected_file,
        open("tmp/degrades_weekly_report.csv", "r") as actual_file,
    ):
        expected = expected_file.read()
        actual = actual_file.read()
        assert actual == expected

    os.remove("tmp/degrades_weekly_report.csv")

# TODO PRM-410 add test cases: gen new rows from weekly summary, pos + neg, neg test gen report and summary
