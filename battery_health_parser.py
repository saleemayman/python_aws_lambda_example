import logging

from definitions import State, log

# start locations of info in input hexadecimal data
positions = {
    "type": 0,
    "time_1": 0,  # start location of the byte in which part of this data exists
    "time_2": 1,
    "time_3": 2,
    "time_4": 3,
    "time_5": 4,
    "state": 4,  # use start of whole byte
    "state_of_charge": 5,
    "battery_temperature": 6,
}


class BatteryHealthInputParser:
    """This class will parse a Hexadecimal encoded information about
    the health of a battery pack. It extracts each info using a
    separate method.

    Information is encoded in little-endian as follows:
    Byte 1:
        - first 4 bits are device type (?)
        - last 4 bits are starting location of time info (time since epoch)
    Byte 2: continuation of time info
    Byte 3: continuation of time info
    Byte 4: continuation of time info
    Byte 5:
        - first 4 bits are part of time info
        - last 4 bits contain info about state of the battery
    Byte 6: battery state of charge
    Byte 7: battery temperature
    """

    def __init__(self, payload: str):
        self.payload = payload

    def slicer(self, byte_start_location: int):
        # TODO: add return type for slice object
        start = byte_start_location * 2
        end = (byte_start_location + 1) * 2

        return slice(start, end, 1)

    def get_device_type(self) -> int:
        logging.info(log("Getting device type"))

        first_byte = int(self.payload[self.slicer(positions["type"])], 16)

        return first_byte & 0b00001111  # get the 4 LSB of the first byte

    def get_time(self) -> int:
        first_byte = int(self.payload[self.slicer(positions["time_1"])], 16)
        t1 = (first_byte >> 4) & 0b1111  # get the 4 MSB of the first byte
        t2 = int(self.payload[self.slicer(positions["time_2"])], 16)
        t3 = int(self.payload[self.slicer(positions["time_3"])], 16)
        t4 = int(self.payload[self.slicer(positions["time_4"])], 16)
        fifth_byte = int(self.payload[self.slicer(positions["time_5"])], 16)
        t5 = fifth_byte & 0b00001111  # get the 4 LSB of the 5th byte

        def binary_bits(n: int, pad8: bool = True) -> str:
            if pad8:
                return bin(n)[2:].zfill(8)
            return bin(n)[2:].zfill(4)

        # collect all time bytes (str in binary) in correct order and convert to int
        time = int(
            binary_bits(t5, pad8=False)
            + binary_bits(t4)
            + binary_bits(t3)
            + binary_bits(t2)
            + binary_bits(t1, pad8=False),
            2,
        )

        logging.info(log("Getting battery time", time=time))

        return time

    def get_state(self) -> State:
        fifth_byte = int(self.payload[self.slicer(positions["state"])], 16)
        state = (fifth_byte >> 4) & 0b1111  # get the 4 MSB of the 5th byte

        logging.info(log("Getting battery state", state=state))

        return State(state)

    def get_state_of_charge(self) -> int:
        logging.info(log("Getting state of charge"))

        return int(self.payload[self.slicer(positions["state_of_charge"])], 16) / 2

    def get_battery_temperature(self) -> int:
        logging.info(log("Getting battery temperature"))

        return (
            int(self.payload[self.slicer(positions["battery_temperature"])], 16) / 2
            - 20
        )
