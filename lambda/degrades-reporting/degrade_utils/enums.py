from enum import StrEnum


class CsvHeaders(StrEnum):
    WEEK_BEGINNING = "Week_beginning"
    TYPE = "Type"
    REASON = "Reason"
    COUNT = "Count"

    @staticmethod
    def list_values():
        return list(CsvHeaders.__members__.values())