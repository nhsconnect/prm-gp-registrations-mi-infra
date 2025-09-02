from enum import StrEnum


class OdsItem(StrEnum):
    NHS_ODS_WEEKLY = "58"
    ORG_REF_DATA_MONTHLY = "242"


class OdsDownloadType(StrEnum):
    GP = "ODS_GP"
    ICB = "ODS_ICB"
    BOTH = "ODS_GP_ICB"
