import json
import logging
from enum import Enum

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated


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
    payload: Annotated[
        str, StringConstraints(strict=True, min_length=16, max_length=16)
    ]


class BatteryHealth(BaseModel):
    device: str
    time: int  # TODO: add Unix timestamp int type
    state: State
    state_of_charge: Annotated[float, Field(strict=True, ge=0, le=100)]
    temperature: Annotated[float, Field(strict=True, ge=-20, le=100)]

    # use names instead of values for State when creating JSON dump
    class Config:
        json_encoders = {State: lambda s: s.name}


class JSONLogger(object):
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs))


logging.basicConfig(level=logging.INFO, format="%(message)s")

log = JSONLogger
