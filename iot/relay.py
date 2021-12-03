from asyncio.runners import run
from threading import Thread, Lock
import socketio
import serial
import json
import time

io = socketio.Client()
arduino = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)

IOT_KEY = "*2138192AHKHSBANM%^#@!@#^%&$%"

running: bool = False
serial_thread: Thread = None

def serial_thread_worker():
    global running, arduino
    print("serial thread running")

    while running:
        data = arduino.readline().decode("utf-8").strip()
        if data:
            json_data = json.loads(data)
            io.emit("update", {
                "temperature": json_data["temperature"],
                "humidity": json_data["humidity"]
            })
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
    io.connect("http://localhost:8080")
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
