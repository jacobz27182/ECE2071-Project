import serial
import sys
import time


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
    baudrate = 115200

    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=0.5) as ser:
            print(f"Connected to {port} at {baudrate} baud")

            #msg = str(6)
            ser.write(b'B')
            print("Listening for STM32 output. Press Ctrl+C to stop.")

            while True:
                line = ser.readline()
                if not line:
                    continue
                try:
                    #print(line)
                    #print(line.decode("utf-8"))
                    print(line.decode())
                except Exception:
                    print(repr(line))
                time.sleep(0.01)

    except serial.SerialException as exc:
        print("Serial error:", exc)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()