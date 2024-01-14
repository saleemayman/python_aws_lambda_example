import json
import logging
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from battery_health_parser import BatteryHealthInputParser
from definitions import BatteryHealth, InputEvent, log


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        result = parse_battery_health(InputEvent(**event))
        logging.info(
            log("Finished parsing battery health", result=result.model_dump_json())
        )

        response = {
            "statusCode": 200,
            "body": json.dumps({"result": result.model_dump_json()}),
        }
    except ValidationError as e:
        logging.error(log("Error parsing and processing input", error=str(e)))
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Error parsing input", "details": str(e)}),
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Unexpected server error", "details": str(e)}),
        }

    return response


def parse_battery_health(event: InputEvent) -> BatteryHealth:
    parser = BatteryHealthInputParser(event.payload)

    return BatteryHealth(
        device=event.device,
        time=parser.get_time(),
        state=parser.get_state(),
        state_of_charge=parser.get_state_of_charge(),
        temperature=parser.get_battery_temperature(),
    )


# if __name__ == "__main__":
#     test_inputs = [
#         {"device": "device_1", "payload": "F1E6E63676C75000"},
#         {"device": "device_2", "payload": "9164293726C85400"},
#         {"device": "device_3", "payload": "6188293726C75C00"},
#     ]

#     for test in test_inputs:
#         lambda_handler(event=test, context=None)
