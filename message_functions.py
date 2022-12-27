from datetime import datetime
import serial


def get_crc(message: bytes):
    count = 0
    for b in message:
        count += b
    return (count & 0xff).to_bytes(1, "big")


def create_message(func):
    def inner():
        message = func()
        crc = get_crc(bytes(message, 'ascii'))
        return bytes(message + "\n", "ascii")  # + crc

    return inner

def create_message_with_arg(func):
    def inner(arg):
        message = func(arg)
        crc = get_crc(bytes(message, 'ascii'))
        return bytes(message + "\n", "ascii")  # + crc

    return inner


@create_message
def create_time_message() -> str:
    return "s" + datetime.now().strftime("%Y%m%d%H%M%S")


@create_message
def ask_for_time():
    return "d"


@create_message
def get_file_list_message():
    return "l"


@create_message_with_arg
def get_file_content(filename: str):
    return "c" + filename
