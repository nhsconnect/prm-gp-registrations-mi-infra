
import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from utils.models.ods_models import PracticeOds,IcbOds  

dynamodb = boto3.resource('dynamodb')
icb_table = "dev_mi_enrichment_icb_ods"
gp_table = "dev_mi_enrichment_practice_ods"

logger = logging.getLogger(__name__)



def find_missing_data(field_name, table_name):
    missing_data = []
    try:
        table = dynamodb.Table(table_name)
        table.load()
        scan_kwargs = {
            "FilterExpression": f"attribute_not_exists({field_name})",
        }
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = table.scan(**scan_kwargs)
            missing_data.extend(response.get("Items", []))
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None
    except ClientError as err:
        logger.error(
            "Couldn't scan for %s with value %s. Here's why: %s: %s",
            field_name,
            None,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    else:
        return missing_data

print("Starting to scan for missing data...\n\n")

print("Scanning ICB ODS table for missing ICB Statuses...")
missing_icb_status_data = find_missing_data("IcbStatus", icb_table)
print("Scanning gp ODS table for missing ICB Codes...")
missing_gp_icb_data = find_missing_data("IcbOdsCode", gp_table)
print("Scanning gp ODS table for missing Practice Statuses...\n\n")
missing_gp_status_data = find_missing_data("PracticeStatus", gp_table)

total_issues = len(missing_icb_status_data) + len(missing_gp_icb_data) + len(missing_gp_status_data)

print(f"Scan complete. Found {total_issues} records with missing data:")
print(f" - {len(missing_icb_status_data)} ICB records missing ICB Status")
print(f" - {len(missing_gp_icb_data)} GP records missing ICB ODS")
print(f" - {len(missing_gp_status_data)} GP records missing Practice Status")