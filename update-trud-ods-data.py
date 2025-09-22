
import json
import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import requests
from utils.models.ods_models import PracticeOds,IcbOds  
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
icb_table = "dev_mi_enrichment_icb_ods"
gp_table = "dev_mi_enrichment_practice_ods"

logger = logging.getLogger(__name__)

# list_of_ods_to_ignore = ['M','X','C','W', 'F', 'K', 'Y', 'B', 'A', 'J', 'G', 'H', 'P', 'N', 'E', 'L']
list_of_ods_to_ignore = []
def find_missing_data(field_name, table_name):
    missing_data = []
    try:
        table = dynamodb.Table(table_name)
        table.load()
        scan_kwargs = {
            # Use a real condition, not a string. (String works sometimes, but this is safer.)
            "FilterExpression": Attr(field_name).not_exists(),  # from boto3.dynamodb.conditions
        }
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = table.scan(**scan_kwargs)
            missing_data.extend(response.get("Items", []))
            start_key = response.get("LastEvaluatedKey")
            done = start_key is None
    except ClientError as err:
        logger.error(
            "Couldn't scan %s for missing %s. %s: %s",
            table_name, field_name,
            err.response.get("Error", {}).get("Code"),
            err.response.get("Error", {}).get("Message"),
        )
        # Don't raise; keep going with what we have
        return []
    return missing_data

def _safe_get_json(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code != 200:
            logger.warning("GET %s -> %s", url, r.status_code)
            return None
        # Some endpoints return empty body on 200
        if not r.content:
            return None
        return r.json()
    except requests.RequestException as e:
        logger.error("HTTP error for %s: %s", url, e)
        return None
    except ValueError as e:
        # invalid JSON
        logger.error("Invalid JSON from %s: %s", url, e)
        return None

def get_ods_status(ods_code, is_status_field=True):
    ord_url = f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{ods_code}"
    stu3_url = f"https://directory.spineservices.nhs.uk/STU3/Organization/{ods_code}"

    data = _safe_get_json(ord_url)
    if isinstance(data, dict):
        org = data.get('Organisation') or data.get('organisation')  # be liberal in what you accept
        if org:
            if is_status_field:
                return org.get('Status')
            # ICB ODS code path
            rels = org.get('Rels') or {}
            rel_list = (rels.get('Rel') or []) if isinstance(rels, dict) else []
            if rel_list:
                target = (rel_list[0] or {}).get('Target') or {}
                org_id = target.get('OrgId') or {}
                return org_id.get('extension')
        else:
            logger.warning("ORD payload missing 'Organisation' for %s: %s", ods_code, json.dumps(data)[:300])

    # Fallback to STU3
    data = _safe_get_json(stu3_url)
    if data:
        # STU3 can be a dict (single resource) or Bundle-like
        if isinstance(data, list) and data:
            # e.g., search result array
            first = data[0]
            return first.get('active') if isinstance(first, dict) else None
        if isinstance(data, dict):
            # If it's a Bundle
            if data.get('resourceType') == 'Bundle':
                entries = data.get('entry') or []
                if entries and isinstance(entries[0], dict):
                    res = entries[0].get('resource') or {}
                    return res.get('active')
            # Or a single Organization resource
            if data.get('resourceType') == 'Organization':
                return data.get('active')
    logger.error("Unable to determine status/ICB for ODS %s from ORD or STU3", ods_code)
    return None

    
def backfill_statuses(missing_status_data, table_name, is_status_field=True):
    for record in missing_status_data:
        odsCode = record.get("IcbOdsCode") if table_name == icb_table else record.get("PracticeOdsCode")
        if not odsCode:
            logger.warning("Record missing ODS code: %s", record)
            continue
        if odsCode[0] not in list_of_ods_to_ignore:

            try:
                if table_name == gp_table:
                    if is_status_field:
                        gp_status = get_ods_status(odsCode, True)
                        if gp_status is None:
                            logger.warning("No Practice status for %s", odsCode)
                            continue
                        gp = PracticeOds(odsCode)
                        gp.update(actions=[
                            PracticeOds.practice_status.set(gp_status),
                            PracticeOds.last_updated.set(datetime.now(timezone.utc))
                        ])
                        logger.info("Backfilled Practice %s with status %s", odsCode, gp_status)
                    else:
                        icb_code = get_ods_status(odsCode, False)
                        if not icb_code:
                            logger.warning("No ICB ODS for %s", odsCode)
                            continue
                        gp = PracticeOds(odsCode)
                        gp.update(actions=[
                            PracticeOds.icb_ods_code.set(icb_code),
                            PracticeOds.last_updated.set(datetime.now(timezone.utc))
                        ])
                        logger.info("Backfilled Practice %s with ICB ODS %s", odsCode, icb_code)
                else:
                    icb_status = get_ods_status(odsCode, True)
                    if icb_status is None:
                        logger.warning("No ICB status for %s", odsCode)
                        continue
                    icb = IcbOds(odsCode)
                    icb.update(actions=[
                        IcbOds.icb_status.set(icb_status),
                        IcbOds.last_updated.set(datetime.now(timezone.utc))
                    ])
                    logger.info("Backfilled ICB %s with status %s", odsCode, icb_status)

            except Exception as e:
                # Keep going; don’t exit the loop
                logger.exception("Failed to backfill %s (%s): %s", odsCode, table_name, e)
                continue

print("Starting to scan for missing data...\n\n")

print("Scanning ICB ODS table for missing ICB Statuses...")
missing_icb_status_data = find_missing_data("IcbStatus", icb_table)

print("Scanning GP ODS table for missing ICB Codes...")
missing_gp_icb_data = find_missing_data("IcbOdsCode", gp_table)

print("Scanning gp ODS table for missing Practice Statuses...\n\n")
missing_gp_status_data = find_missing_data("PracticeStatus", gp_table)

total_issues = len(missing_icb_status_data) + len(missing_gp_icb_data) + len(missing_gp_status_data)

print(f"Scan complete. Found {total_issues} records with missing data:")
print(f" - {len(missing_icb_status_data)} ICB records missing ICB Status")
print(f" - {len(missing_gp_icb_data)} GP records missing ICB ODS")
print(f" - {len(missing_gp_status_data)} GP records missing Practice Status\n\n")

if missing_gp_status_data:
    print(f"Found {len(missing_gp_status_data)} GP records with missing Practice Status. Starting backfill...")
    backfill_statuses(missing_gp_status_data, gp_table)

if missing_icb_status_data:
    print(f"Found {len(missing_icb_status_data)} ICB records with missing ICB Status. Starting backfill...")
    backfill_statuses(missing_icb_status_data, icb_table)

if missing_gp_icb_data:
    print(f"Found {len(missing_gp_icb_data)} GP records with missing ICB ODS. Starting backfill...")
    backfill_statuses(missing_gp_icb_data, gp_table, False)