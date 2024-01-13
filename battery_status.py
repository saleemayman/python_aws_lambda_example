import json
import logging
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from typing import Dict, Any
from enum import Enum

from aws_lambda_powertools.utilities.typing import LambdaContext

positions = {
    "type": 0,
    "time_1": 0, # start location of the byte in which part of this data exists
    "time_2": 1,
    "time_3": 2,
    "time_4": 3,
    "time_5": 4,
    "state": 4, # use start of whole byte
    "state_of_charge": 5,
    "battery_temperature": 6,
}

class State(Enum):
    power_off = 0
    power_on = 1
    discharge = 2
    charge = 3
    charge_complete = 4
    host_mode = 5
    shutdown = 6
    error = 7
    undefined = 8


class InputEvent(BaseModel):
    device: str
    payload: str


class BatteryHealth(BaseModel):
    device: str
    time: int # TODO: add Unix timestamp int type
    state: State
    state_of_charge: Annotated[float, Field(strict=True, ge=0, le=100)]
    temperature: Annotated[float, Field(strict=True, ge=-20, le=100)]


class JSONMessage(object):
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs
    def __str__(self):
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs))

msg = JSONMessage
logging.basicConfig(level=logging.INFO, format="%(message)s")


def battery_status(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        request_body = json.loads(event["body"])

        result = parse_battery_health(InputEvent(**request_body))
        logging.info(msg("Finished parsing battery health"))

        response = {
            "statusCode": 200,
            "body": json.dumps({"result": result})
        }
    except ValidationError as e:
        logging.error(msg("Error parsing and processing input", error=e))
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Error parsing input", "details": e.errors()})
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Unexpected server error", "details": str(e)})
        }

    return response

def parse_battery_health(event: InputEvent) -> BatteryHealth:
    return BatteryHealth(
        device=event.device,
        time=get_time(event.payload),
        state=get_state(event.payload),
        state_of_charge=get_state_of_charge(event.payload),
        temperature=get_battery_temperature(event.payload),
    )

def slicer(byte_start_location: int):
    start = byte_start_location * 2
    end = (byte_start_location + 1) * 2
    return slice(start, end, 1)

def get_device_type(payload: str) -> int:
    logging.info(msg("Getting device type"))
    first_byte = int(payload[slicer(positions["type"])], 16)
    return (first_byte &  0b00001111) # get the 4 LSB of the first byte

def get_time(payload: str) -> int:
    first_byte = int(payload[slicer(positions["time_1"])], 16)
    t1 = (first_byte >> 4) & 0b1111 # get the 4 MSB of the first byte
    t2 = int(payload[slicer(positions["time_2"])], 16)
    t3 = int(payload[slicer(positions["time_3"])], 16)
    t4 = int(payload[slicer(positions["time_4"])], 16)
    fifth_byte = int(payload[slicer(positions["time_5"])], 16)
    t5 = (fifth_byte & 0b00001111) # get the 4 LSB of the 5th byte
    def binary_bits(n: int, pad8: bool = True) -> str:
        if pad8:
            return bin(n)[2:].zfill(8)
        return bin(n)[2:].zfill(4)
    # collect all time bytes (str in binary) in correct order and convert to int
    time = int(
        binary_bits(t5, pad8=False) +
        binary_bits(t4) +
        binary_bits(t3) +
        binary_bits(t2) +
        binary_bits(t1, pad8=False),
        2
    )
    logging.info(msg("Getting battery time", time=time))
    return time

def get_state(payload: str) -> State:
    fifth_byte = int(payload[slicer(positions["state"])], 16)
    state = (fifth_byte >> 4) & 0b1111 # get the 4 MSB of the 5th byte
    logging.info(msg("Getting battery state", state=state))
    return State(state)

def get_state_of_charge(payload: str) -> int:
    logging.info(msg("Getting state of charge"))
    return int(payload[slicer(positions["state_of_charge"])], 16) / 2

def get_battery_temperature(payload: str) -> int:
    logging.info(msg("Getting battery temperature"))
    return int(payload[slicer(positions["battery_temperature"])], 16) / 2 - 20