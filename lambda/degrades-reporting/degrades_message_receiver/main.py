import json
import os
import logging
from datetime import datetime
from pydantic import ValidationError
from models.degrade_message import DegradeMessage
from degrade_utils.dynamo_service import DynamoService
from degrade_utils.utils import extract_degrades_payload

logger = logging.getLogger()
logger.setLevel("INFO")


def lambda_handler(event, context):
    messages = event.get("Records", [])
    dynamo_service = DynamoService()

    for message in messages:
        try:
            message = json.loads(message["body"])

            logger.info(f"Processing message: {message['eventId']}")

            if message["eventType"] != "DEGRADES":
                logger.error("Validation error: Message is not of type DEGRADES")
                raise ValueError("Invalid degrade message")

            timestamp = int(
                datetime.fromisoformat(message["eventGeneratedDateTime"]).timestamp()
            )

            degrades = extract_degrades_payload(message["payload"])

            degrades_message = DegradeMessage(
                timestamp=timestamp,
                message_id=message["eventId"],
                event_type=message["eventType"],
                degrades=degrades,
            )
            DegradeMessage.model_validate(degrades_message)

            dynamo_service.put_item(
                table_name=os.getenv("DEGRADES_MESSAGE_TABLE"),
                payload=degrades_message.model_dump(
                    by_alias=True, exclude={"event_type"}
                ),
            )
            logger.info("Degrade successfully added to table.")
        except ValidationError as e:
            logger.error("Validation error: Invalid degrade message")
            raise ValueError("Invalid degrade message", e.json)
        except Exception as e:
            logger.error(f"{e}")
            raise e
