from typing import Union
from flask import Flask
from BetaBriteConstants import *
import typing
import serial
import time

ControlToken = typing.NamedTuple('ControlToken', [('text', str),
                                                      ('byte_value', bytes), ('description', str)])


display_modes = [ControlToken(text="HOLD", byte_value=MODE_HOLD, description="Holds the message statically on the sign, "
                                                                            "unless the message is longer than the sign in "
                                                                            "which case it will repeatedly scroll the "
                                                                            "message across the sign"),
                 ControlToken(text="FLASH", byte_value=MODE_FLASH,
                             description="Repeatedly flashes the message on the sign"),
                 ControlToken(text="ROTATE", byte_value=MODE_ROTATE,
                             description="Repeatedly scrolls the message across the "
                                         "sign")]

control_commands = [ControlToken(text="SET_TIME", byte_value=CMD_SET_TIME,
                                   description="Sets the current time on sign's internal clock"),
                    ControlToken(text="SET_TIME_FORMAT", byte_value=CMD_SET_TIME_FORMAT,
                                   description="Sets the format of the time displayed on the sign: 'S' = standard, "
                                               "'M' = military"),
                    ControlToken(text="SET_DAY_OF_WEEK", byte_value=CMD_SET_DAY_OF_WEEK,
                                   description="Sets the day of the week on the sign: 0-6")]

betabrite_tokens = [ControlToken(text='<red>', byte_value=TEXT_COLOR_RED,
                                   description='Set text color to red'),
                    ControlToken(text='<green>', byte_value=TEXT_COLOR_GREEN,
                                   description='Set text color to green'),
                    ControlToken(text='<amber>', byte_value=TEXT_COLOR_AMBER,
                                   description='Set text color to amber'),
                    ControlToken(text='<dimred>', byte_value=TEXT_COLOR_DIMRED,
                                   description='Set text color to dim red'),
                    ControlToken(text='<dimgreen>', byte_value=TEXT_COLOR_DIMGREEN,
                                   description='Set text color to dim green'),
                    ControlToken(text='<brown>', byte_value=TEXT_COLOR_BROWN,
                                   description='Set text color to brown'),
                    ControlToken(text='<orange>', byte_value=TEXT_COLOR_ORANGE,
                                   description='Set text color to orange'),
                    ControlToken(text='<yellow>', byte_value=TEXT_COLOR_YELLOW,
                                   description='Set text color to yellow'),
                    ControlToken(text='<rainbow1>', byte_value=TEXT_COLOR_RAINBOW1,
                                   description='Set text color to \'rainbow1\''),
                    ControlToken(text='<rainbow2>', byte_value=TEXT_COLOR_RAINBOW2,
                                   description='Set text color to \'rainbow2\''),
                    ControlToken(text='<color_mix>', byte_value=TEXT_COLOR_MIX,
                                   description='Set text color to \'mix\''),
                    ControlToken(text='<flash_on>', byte_value=CHAR_FLASH_ON,
                                   description='Characters after this token will flash'),
                    ControlToken(text='<flash_off>', byte_value=CHAR_FLASH_OFF,
                                   description='Characters after this token will not flash'),
                    ControlToken(text='<degree>', byte_value=XC_DEGREES,
                                   description='Degree symbol'),
                    ControlToken(text='<fixed_width>', byte_value=FIXED_WIDTH_ON,
                                   description='Should be first token in message - left-justify and '
                                                     'make text fixed width'),
                    ControlToken(text='<time>', byte_value=CURTIME_INSERT,
                                   description='Insert current time'),
                    ControlToken(text='<week_day>', byte_value=CURDATE_WEEKDAYY,
                                   description='Insert current day of the week')
                    ]


tag_dict = {token.text: token for
                token in
                betabrite_tokens}

mode_dict = {token.text: token for
                token in
                display_modes}

command_dict = {token.text: token for
                token in
                control_commands}


def parse_message(message: str) -> bytes:
    output = b''
    i = 0

    while i < len(message):
        if message[i] == '<':
            closing_bracket_idx = message.find('>', i)
            if closing_bracket_idx > 0:
                tag = message[i:closing_bracket_idx + 1]
                tag_obj = tag_dict.get(tag, tag)
                if hasattr(tag_obj, 'byte_value'):
                    code = tag_obj.byte_value
                    output += to_bytes(code)
                else:
                    output += to_bytes(tag)
                i = closing_bracket_idx + 1
        else:
            output += to_bytes(message[i])
            i += 1

    return output


def to_bytes(value: Union[str, bytes]) -> bytes:
    if isinstance(value, bytes):
        return value

    b = bytes(value, 'utf-8')
    return b


def get_token_descriptions() -> list[dict[str, str]]:
    description_list = list({'token_text': betabrite_token.text,
                                   'description': betabrite_token.description}
                                  for betabrite_token in betabrite_tokens)

    return description_list


def get_display_modes() -> list[dict[str, str]]:
    mode_description_list = list({'display_mode': mode.text,
                                  'description': mode.description}
                                 for mode in display_modes)

    return mode_description_list


def get_control_commands() -> list[dict[str, str]]:
    command_description_list = list({'control_command': command.text,
                                     'description': command.description}
                                    for command in control_commands)

    return command_description_list


class BetaBriteSign:

    def __init__(self, port: str):
        self.port = port

    def display_message(self, mode: ControlToken = mode_dict['HOLD'], message: str = ''):
        payload = COMMAND_WRITE_TEXT + FILE_PRIORITY + SOM + TEXT_POS_MIDDLE + mode.byte_value \
                  + parse_message(message)

        self.transmit_payload(payload)

    def control_command(self, command: ControlToken, message: str = ''):
        payload = COMMAND_WRITE_SPECIAL + command.byte_value \
                  + parse_message(message)

        self.transmit_payload(payload)

    def transmit_payload(self, payload):
        packet = WAKEUP + SOH + SIGN_TYPE_BETABRITE + SIGN_ADDRESS_BROADCAST + STX + payload + EOT
        try:
            ser = serial.Serial(self.port, 9600, timeout=10)
            ser.write(packet)
            time.sleep(2)
            ser.close()
        except Exception as err:
            if Flask.testing:
                return {'result': 'OK', 'result_message': 'Test response'}
            else:
                raise err
