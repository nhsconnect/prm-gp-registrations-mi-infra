import os

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class PracticeOds(Model):
    class Meta:
        table_name = "dev_mi_enrichment_practice_ods"

    practice_ods_code = UnicodeAttribute(hash_key=True, attr_name="PracticeOdsCode")
    practice_name = UnicodeAttribute(attr_name="PracticeName")
    icb_ods_code = UnicodeAttribute(null=True, attr_name="IcbOdsCode")
    supplier_name = UnicodeAttribute(null=True, attr_name="SupplierName")
    supplier_last_updated = UTCDateTimeAttribute(
        null=True, attr_name="SupplierLastUpdated"
    )


class IcbOds(Model):
    class Meta:
        table_name = "dev_mi_enrichment_icb_ods"

    icb_ods_code = UnicodeAttribute(hash_key=True, attr_name="IcbOdsCode")
    icb_name = UnicodeAttribute(attr_name="IcbName")
