import serial.tools.list_ports
import inquirer
import serial
import pickle

STORE_FILE = ".arduino.device"

class RememberedDeviceIsNotConnectedException(Exception):
    def __init__(self, device):
        super().__init__(message=f"Device {device} is not connected")

def get_arduino_serial_connection(*args, **kwargs) -> serial.Serial:
    remembered_choice = load_previous_choice()
    ports = serial.tools.list_ports.comports()
    devices = [ (device.device, device.serial_number) for device in ports ]
    device = None
    ask_question = True

    if remembered_choice:
        for _device in devices:
            if _device[1] == remembered_choice:
                device = _device
                break

        if device is None:
            print("Remembered device not connected")
            if input("Do you want to choose another device? (Y/N) ").lower() == "n":
                raise RememberedDeviceIsNotConnectedException(remembered_choice)
        else:
            print("Using arduino %s | %s" % device)
            ask_question = False

    if ask_question:

        if len(devices) == 0:
            print("No arduino devices connected!")
            exit(1) # TODO throw exception
        
        questions = [
            inquirer.List("comport", "Choose arduino device", choices=[(f"{device[1]} | {device[0]}", device) for device in devices]),
            inquirer.Confirm("remember", message="Do you want to remember your choice?", default=False)
        ]

        answers = inquirer.prompt(questions)
        device = answers['comport']
        if answers['remember']:
            remember_choice(device[1])

    return serial.Serial(port=device[0], **kwargs)

def remember_choice(serial_number: str):
    with open(STORE_FILE, "wb+") as fp:
        pickle.dump(serial_number, fp)

def load_previous_choice():
    try:
        with open(STORE_FILE, "rb") as fp:
            return pickle.load(fp)
    except Exception:
        return None
  