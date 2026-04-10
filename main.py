import serial
import serial.tools.list_ports
import time
import keyboard

def main():
    port = serial.tools.list_ports.comports()[0]
    baudrate = 115200

    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=0.5) as ser:
            print(f"Connected to {port} at {baudrate} baud")
            
            msg = input("Enter message to send: ").encode()
 
            # print("Listening for STM32 output. Press Ctrl+C to stop.")

            while True:
                ser.write(str(len(msg)).encode())
                ser.read() #reads 1 byte if no arguments fed
                # print("Acklowledgement Receiveds.")
                ser.write(msg)

                line = ser.readline()
                if not line:
                    continue

                print(line.decode())
                
                keyboard.wait()

    except serial.SerialException as exc:
        print("Serial error:", exc)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()