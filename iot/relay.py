from asyncio.runners import run
from threading import Thread, Lock
import socketio
import random
import time

io = socketio.Client()

IOT_KEY = "*2138192AHKHSBANM%^#@!@#^%&$%"

thread_lock: Lock = Lock()
running: bool = False
serial_thread: Thread = None

def serial_thread_worker(running, thread_lock: Lock):
    print("serial thread running")

    while running:
        with thread_lock:
            io.emit("update", {
                "temperature": random.randint(10, 100),
                "humidity": random.randint(10, 50)
            })
        
        time.sleep(2)

    print("serial threading stopping")

def start_serial_thread():
    global running, serial_thread
    running = True
    serial_thread = Thread(target=serial_thread_worker, args=(running, thread_lock))
    serial_thread.setDaemon(True)
    serial_thread.start()

def stop_serial_thread():
    global running, serial_thread
    running = False
    if serial_thread:
        serial_thread.join()
        serial_thread = None

@io.event
def connect():
    print("[socketio] connected to server")
    io.emit("upgrade", {
        "UPGRADE-KEY": IOT_KEY
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
        if io.connected:
            io.disconnect()
        stop_serial_thread()
        exit(0)
