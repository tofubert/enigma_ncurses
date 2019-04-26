import serial
import subprocess
import shlex

while True:
    try:
        with serial.Serial("/dev/ttyACM0", 9600) as ser:
            while True:
                line = str(ser.readline())
                if "MODE" not in line and "ENGIMA" not in line:
                    key = line[2]
                    response = line[4]
                    cmd = ["./create.sh", key, response]
                    print(cmd)
                    subprocess.call(cmd)
    except:
        pass
