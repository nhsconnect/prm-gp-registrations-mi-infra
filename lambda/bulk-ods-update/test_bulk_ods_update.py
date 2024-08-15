import datetime
import os

import pytest
import pytest_mock
from moto import mock_aws
from freezegun import freeze_time

from bulk_ods_update import lambda_handler, compare_and_overwrite, determine_ods_manifest_download_type
from utils.enums.trud import OdsDownloadType
from utils.models.ods_models import PracticeOds, IcbOds

test_amended_values = [
    {
        "PracticeOdsCode": "B86094",
        "PracticeName": "DR S M CHEN & PARTNER",
        "NationalGrouping": "Y63",
        "HighLevelHealthGeography": "QWO",
        "AddressLine1": "THE GABLES SURGERY",
        "AddressLine2": "231 SWINNOW ROAD",
        "AddressLine3": "PUDSEY, LEEDS",
        "AddressLine4": "WEST YORKSHIRE",
        "AddressLine5": "",
        "Postcode": "LS28 9AW",
        "OpenDate": "19740401",
        "CloseDate": "",
        "StatusCode": "A",
        "OrganisationSubTypeCode": "B",
        "IcbOdsCode ": "15F",
        "JoinParentDate": "20180401",
        "LeftParentDate": "",
        "ContactTelephoneNumber": "0113 2574730",
        "Null": "",
        "Null2": "",
        "Null3": "",
        "AmendedRecordIndicator": "1",
        "Null4": "",
        "ProviderPurchaser": "15F",
        "Null5": "",
        "PracticeType": "4",
        "Null6": "",
    },
    {
        "PracticeOdsCode": "G85054",
        "PracticeName": "LAMBETH WALK GROUP PRACTICE",
        "NationalGrouping": "Y56",
        "HighLevelHealthGeography": "QKK",
        "AddressLine1": "AKERMAN HEALTH CENTRE",
        "AddressLine2": "60 PATMOS ROAD",
        "AddressLine3": "",
        "AddressLine4": "",
        "AddressLine5": "",
        "Postcode": "SW9 6AF",
        "OpenDate": "19740401",
        "CloseDate": "",
        "StatusCode": "A",
        "OrganisationSubTypeCode": "B",
        "IcbOdsCode ": "72Q",
        "JoinParentDate": "20200401",
        "LeftParentDate": "",
        "ContactTelephoneNumber": "020 77354412",
        "Null": "",
        "Null2": "",
        "Null3": "",
        "AmendedRecordIndicator": "1",
        "Null4": "",
        "ProviderPurchaser": "72Q",
        "Null5": "",
        "PracticeType": "4",
        "Null6": "",
    },
    {
        "PracticeOdsCode": "H85032",
        "PracticeName": "CARSHALTON FIELDS SURGERY",
        "NationalGrouping": "Y56",
        "HighLevelHealthGeography": "QWE",
        "AddressLine1": "11 CRICHTON ROAD",
        "AddressLine2": "CARSHALTON BEECHES",
        "AddressLine3": "SURREY",
        "AddressLine4": "",
        "AddressLine5": "",
        "Postcode": "SM5 3LS",
        "OpenDate": "19740401",
        "CloseDate": "",
        "StatusCode": "D",
        "OrganisationSubTypeCode": "B",
        "IcbOdsCode ": "36L",
        "JoinParentDate": "20200401",
        "LeftParentDate": "",
        "ContactTelephoneNumber": "020 86433030",
        "Null": "",
        "Null2": "",
        "Null3": "",
        "AmendedRecordIndicator": "1",
        "Null4": "",
        "ProviderPurchaser": "36L",
        "Null5": "",
        "PracticeType": "4",
        "Null6": "",
    },
]


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("GP_ODS_DYNAMO_TABLE_NAME", "PracticeTableTest")
    monkeypatch.setenv("ICB_ODS_DYNAMO_TABLE_NAME", "IcbTableTest")


@pytest.fixture
def create_practice_table(set_env):
    with mock_aws():
        if not PracticeOds.exists():
            PracticeOds.create_table()

        p1 = PracticeOds(
            practice_ods_code="B86094",
            practice_name="DR S M CHEN & PARTNER",
            icb_ods_code="123",
            supplier_name="EMIS",
            supplier_last_updated=datetime.datetime.now(),
        )
        p1.save()
        p2 = PracticeOds(
            practice_ods_code="G85054",
            practice_name="LAMBETH WALK GROUP PRACTICE",
            icb_ods_code="456",
            supplier_name="EMIS",
            supplier_last_updated=datetime.datetime.now(),
        )
        p2.save()
        p3 = PracticeOds(
            practice_ods_code="H85032",
            practice_name="CARSHALTON FIELDS",
            icb_ods_code="789",
            supplier_name="EMIS",
            supplier_last_updated=datetime.datetime.now(),
        )
        p3.save()


def test_lambda_handler():
    pass


def test_compare_and_overwrite_practice(create_practice_table):
    compare_and_overwrite(OdsDownloadType.GP, test_amended_values)


@pytest.mark.parametrize("date, download_type", [
    ("2024-08-04", OdsDownloadType.GP),
    ("2024-08-11", OdsDownloadType.GP),
    ("2024-08-18", OdsDownloadType.GP),
    ("2024-08-25", OdsDownloadType.BOTH),
    ("2024-09-01", OdsDownloadType.GP),
    ("2024-09-08", OdsDownloadType.GP),
    ("2024-09-15", OdsDownloadType.GP),
    ("2024-09-22", OdsDownloadType.GP),
    ("2024-09-29", OdsDownloadType.BOTH),
    ("2024-10-06", OdsDownloadType.GP),
    ("2024-10-13", OdsDownloadType.GP),
    ("2024-10-20", OdsDownloadType.GP),
    ("2024-10-27", OdsDownloadType.BOTH),
    ("2024-11-03", OdsDownloadType.GP),
    ("2024-11-10", OdsDownloadType.GP),
    ("2024-11-17", OdsDownloadType.GP),
    ("2024-11-24", OdsDownloadType.BOTH),
    ("2024-12-01", OdsDownloadType.GP),
    ("2024-12-08", OdsDownloadType.GP),
    ("2024-12-15", OdsDownloadType.GP),
    ("2024-12-22", OdsDownloadType.GP),
    ("2024-12-29", OdsDownloadType.BOTH),
])
def test_determine_ods_manifest_download_type_gp(date, download_type):
    with freeze_time(date):
        assert determine_ods_manifest_download_type() == download_type

