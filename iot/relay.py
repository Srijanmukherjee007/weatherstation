from asyncio.runners import run
from threading import Thread, Lock
from arduino import STORE_FILE as arduino_remember_cache, RememberedDeviceIsNotConnectedException, get_arduino_serial_connection
import socketio
import serial
import json
import time


io = socketio.Client()
try:
    arduino = get_arduino_serial_connection(baudrate=115200)
except RememberedDeviceIsNotConnectedException as e:
    print(f"[ERROR] {str(e)}")
    print(f"        connect the arduino or remove the '{arduino_remember_cache}' file")
IOT_KEY = "*2138192AHKHSBANM%^#@!@#^%&$%"

running: bool = False
serial_thread: Thread = None

def serial_thread_worker():
    global running, arduino
    print("serial thread running")

    while running:
        data = arduino.readline().decode("utf-8").strip()
        if data:
            try:
                json_data = json.loads(data)
                io.emit("update", {
                    "temperature": json_data["temperature"],
                    "humidity": json_data["humidity"]
                })
            except json.JSONDecodeError:
                print("[ERROR] Couldn't parse data from arduino")
                print("incoming data: '%s'" % data)
        time.sleep(2)

    print("serial threading stopping")

def start_serial_thread():
    global running, serial_thread
    running = True
    serial_thread = Thread(target=serial_thread_worker)
    serial_thread.start()

def stop_serial_thread():
    global running
    running = False
    if serial_thread:
        serial_thread.join()

@io.event
def connect():
    print("[socketio] connected to server")
    io.emit("upgrade", {
        "UPGRADE-KEY": IOT_KEY,
        "location": "Srijan's Home"
    })

@io.on("upgrade-success")
def upgrade_success(data):
    print(data)
    start_serial_thread()


@io.on("upgrade-error")
def upgrade_error(data):
    print(data)

@io.on("update-error")
def update_error(data):
    print("update error", data)

@io.event
def disconnected():
    print("[socketio] disconnected")
    stop_serial_thread()

def main():
    io.connect("https://weather-station-relay-server.herokuapp.com/")
    io.wait()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        stop_serial_thread()
        if io.connected:
            io.disconnect()
        exit(0)
