#!/usr/bin/env python
import os
import asyncio
import random
import websockets
import time
from pathlib import Path
import sys

HEARTBEAT_INTERVAL = 15  # seconds

async def talk(websocket, log_path):
    try:
        f = open(log_path, "rb")
    except Exception as e:
        print(f"Error opening log file: {e}")
        await websocket.close()
        return

    tail_contents = tail(f, 5)
    print(tail_contents)
    for line in tail_contents:
        await websocket.send(str(line))

    f.seek(0, os.SEEK_END)
    last_pos = f.tell()
    last_heartbeat = time.time()

    try:
        while True:
            f = open(log_path, "r")
            f.seek(last_pos)
            new_text = f.readline()
            if new_text:
                # something new
                last_heartbeat = time.time()
                await websocket.send(new_text)
                last_pos = f.tell()
            await asyncio.sleep(random.random() * 3)

            # wait for certain time and then ping
            if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
                try:
                    await websocket.send('ping')
                    pong = await asyncio.wait_for(websocket.recv(), 5)
                    if pong != 'pong':
                        raise Exception()
                except Exception:
                    raise Exception('Ping error')
                else:
                    last_heartbeat = time.time()

    except Exception as e:
        print("Closed connection with the browser. Message: {}".format(e))
        await websocket.close()

def tail(f, window=20):
    """Returns the last `window` lines of file `f` as a list."""
    if window == 0:
        return []

    BUFSIZ = 1024
    f.seek(0, 2)
    remaining_bytes = f.tell()
    size = window + 1
    block = -1
    data = []

    while size > 0 and remaining_bytes > 0:
        if remaining_bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            bunch = f.read(BUFSIZ)
        else:
            # file too small, start from beginning
            f.seek(0, 0)
            # only read what was not read
            bunch = f.read(remaining_bytes)

        bunch = bunch.decode('utf-8')
        data.insert(0, bunch)
        size -= bunch.count('\n')
        remaining_bytes -= BUFSIZ
        block -= 1

    return ''.join(data).splitlines()[-window:]

async def main():
    #log_path = input("Please enter the path to the log file: ")
    if len(sys.argv) < 2:
        print("Usage: logwatch.py <log_file_path>")
        sys.exit(1)
    log_path = sys.argv[1]
    async with websockets.serve(
        lambda ws: talk(ws, log_path),  # Corrected to accept one argument
        "0.0.0.0", 
        5678
    ):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
