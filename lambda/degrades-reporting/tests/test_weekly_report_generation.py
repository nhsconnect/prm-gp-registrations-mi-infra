import os

from degrade_utils.generate_weekly_reports import (
    generate_weekly_report,
    get_keys_from_date_range,
    generate_weekly_summary,
    generate_new_rows_from_week_summary,
)

from degrade_utils.enums import CsvHeaders


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
    date_keys = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    for date in date_keys:
        mock_s3.upload_file(f"./tests/reports/{date}.csv", f"reports/daily/{date}.csv")

    actual = generate_weekly_summary(date_keys, "2024-09-16")
    expected = {
        "Count": {
            ("DRUG_ALLERGY", "CODE"): 2,
            ("MEDICATION", "CODE"): 21,
            ("NON_DRUG_ALLERGY", "CODE"): 8,
            ("RECORD_ENTRY", "CODE"): 12,
            ("RECORD_ENTRY", "NUMERIC_VALUE"): 6,
        }
    }
    assert actual == expected


def test_generate_weekly_summary_no_new_entries_returns_empty_dict(mock_s3, set_env):
    date_keys = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    expected = {}
    actual = generate_weekly_summary(date_keys, "2024-09-16")

    assert actual == expected


def test_weekly_report_generation_adds_new_row_to_global_report(
    set_env, mock_s3, mocker
):
    date_keys = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    for date in date_keys:
        mock_s3.upload_file(f"./tests/reports/{date}.csv", f"reports/daily/{date}.csv")

    mock_summary = mocker.patch(
        "degrade_utils.generate_weekly_reports.generate_weekly_summary"
    )

    mock_summary.return_value = {
        "Count": {
            ("MEDICATION", "CODE"): 16,
            ("NON_DRUG_ALLERGY", "CODE"): 7,
            ("RECORD_ENTRY", "CODE"): 11,
            ("RECORD_ENTRY", "NUMERIC_VALUE"): 4,
            ("DRUG_ALLERGY", "CODE"): 2,
            ("ALLERGY", "CODE"): 1,
        }
    }

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


def test_generate_weekly_reports_writes_new_report_no_previous_report_written(
    mock_s3, set_env, mocker
):
    date_keys = [
        "2024-09-16",
        "2024-09-17",
        "2024-09-18",
        "2024-09-19",
        "2024-09-20",
        "2024-09-21",
        "2024-09-22",
    ]

    for date in date_keys:
        mock_s3.upload_file(f"./tests/reports/{date}.csv", f"reports/daily/{date}.csv")

    mock_summary = mocker.patch(
        "degrade_utils.generate_weekly_reports.generate_weekly_summary"
    )

    mock_summary.return_value = {
        "Count": {
            ("MEDICATION", "CODE"): 19,
            ("NON_DRUG_ALLERGY", "CODE"): 8,
            ("RECORD_ENTRY", "CODE"): 12,
            ("RECORD_ENTRY", "NUMERIC_VALUE"): 6,
            ("DRUG_ALLERGY", "CODE"): 2,
        }
    }

    generate_weekly_report("2024-09-16")

    with (
        open("./tests/reports/global.csv", "r") as expected_file,
        open("tmp/degrades_weekly_report.csv", "r") as actual_file,
    ):
        expected = expected_file.read()
        actual = actual_file.read()
        assert actual == expected

    mock_s3.download_file(
        Key="reports/degrades_weekly_report.csv",
        Filename="tmp/degrades_weekly_report.csv",
    )

    os.remove("tmp/degrades_weekly_report.csv")


def test_generate_new_rows_from_weekly_summary_returns_new_rows_with_date():
    mock_summary = {
        "Count": {
            ("MEDICATION", "CODE"): 16,
            ("NON_DRUG_ALLERGY", "CODE"): 7,
            ("RECORD_ENTRY", "CODE"): 11,
            ("RECORD_ENTRY", "NUMERIC_VALUE"): 4,
            ("DRUG_ALLERGY", "CODE"): 2,
            ("ALLERGY", "CODE"): 1,
        }
    }

    expected = [
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "MEDICATION",
            CsvHeaders.REASON: "CODE",
            CsvHeaders.COUNT: 16,
        },
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "NON_DRUG_ALLERGY",
            CsvHeaders.REASON: "CODE",
            CsvHeaders.COUNT: 7,
        },
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "RECORD_ENTRY",
            CsvHeaders.REASON: "CODE",
            CsvHeaders.COUNT: 11,
        },
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "RECORD_ENTRY",
            CsvHeaders.REASON: "NUMERIC_VALUE",
            CsvHeaders.COUNT: 4,
        },
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "DRUG_ALLERGY",
            CsvHeaders.REASON: "CODE",
            CsvHeaders.COUNT: 2,
        },
        {
            CsvHeaders.WEEK_BEGINNING: "2024-09-16",
            CsvHeaders.TYPE: "ALLERGY",
            CsvHeaders.REASON: "CODE",
            CsvHeaders.COUNT: 1,
        },
    ]

    assert generate_new_rows_from_week_summary(mock_summary, "2024-09-16") == expected


def test_generate_new_rows_from_weekly_summary_returns_empty_list_no_summary():
    mock_summary = {}
    expected = []

    assert generate_new_rows_from_week_summary(mock_summary, "2024-09-16") == expected
