GP_ZIP_FILE_PATH = "Data/epraccur.zip"
GP_FILE_NAME = "epraccur.csv"
GP_REPORT_NAME = "epraccur"

ICB_FILE_PATH = "ocsissue/data/eccg.zip"
ICB_FILE_NAME = "eccg.csv"
ICB_REPORT_NAME = "eccg"

ODS_API_WEEKLY_QUERY = "&lastChangePeriod=7"
ODS_API_URL = "https://www.odsdatasearchandexport.nhs.uk/api/getReport?report="

ALL_ICB_AND_GP_FILES = [
    "eccg",
    "epraccur",
]

GP_FILE_HEADERS = [
    "PracticeOdsCode",
    "PracticeName",
    "NationalGrouping",
    "HighLevelHealthGeography",
    "AddressLine1",
    "AddressLine2",
    "AddressLine3",
    "AddressLine4",
    "AddressLine5",
    "Postcode",
    "OpenDate",
    "CloseDate",
    "StatusCode",
    "OrganisationSubTypeCode",
    "IcbOdsCode",
    "JoinParentDate",
    "LeftParentDate",
    "ContactTelephoneNumber",
    "Null",
    "Null2",
    "Null3",
    "AmendedRecordIndicator",
    "Null4",
    "ProviderPurchaser",
    "Null5",
    "PracticeType",
    "Null6",
]

ICB_FILE_HEADERS = [
    "IcbOdsCode",
    "IcbName",
    "NationalGrouping",
    "HighLevelHealthGeography",
    "AddressLine1",
    "AddressLine2",
    "AddressLine3",
    "AddressLine4",
    "AddressLine5",
    "Postcode",
    "OpenDate",
    "CloseDate",
    "Null1",
    "OrganisationSubTypeCode",
    "Null2",
    "Null3",
    "Null4",
    "Null5",
    "Null6",
    "Null7",
    "Null8",
    "AmendedRecordIndicator",
    "Null9",
    "Null10",
    "Null11",
    "Null12",
    "Null13",
]
