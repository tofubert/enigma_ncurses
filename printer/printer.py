#!/usr/bin/python3
import serial
import subprocess
import time

while True:
    try:
        with serial.Serial("/dev/ttyACM0", 9600, timeout=2) as ser:
            count = 0
            keys = ""
            resps = ""
            while True:
                line = str(ser.readline())
                if "MODE" not in line and "ENGIMA" not in line and len(line) == 10:
                    keys += line[2]
                    resps += line[4]
                    count += 1
                    print(line)
                elif len(line) == 3 and len(keys) > 0:
                    count += 1
                if count >= 4:
                    with open("/home/pi/enigma_ncurses/printer/foo", "w") as f:
                        f.write(keys)
                        f.write("\n")
                        f.write(resps)
                    cmd = ["/home/pi/enigma_ncurses/printer/create.sh"]
                    subprocess.call(cmd)
                    count = 0
                    keys = ""
                    resps = ""
    except Exception as e:
        print(e)
        time.sleep(2)
        pass
