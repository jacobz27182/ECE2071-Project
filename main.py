import serial
import serial.tools.list_ports

def main():
    verbose = True
    port = serial.tools.list_ports.comports()[0].device
    # print(port)
    baudrate = 115200

    try:
        with serial.Serial(port=port, baudrate=baudrate) as ser:
            print(f"Connected to {port} at {baudrate} baud")
            
            msg = ("0"+input("Enter message to send: ")).encode()
 
            # print("Listening for STM32 output. Press Ctrl+C to stop.")

            while True:
                # ser.write(bytes([len(msg)]))
                # if verbose: print(f"sent msg: {len(msg)}")
                # ack = ser.read()
                # if verbose: print(f"received ack: {ack}") 
                ser.write(msg)
                if verbose: print(f"Sent msg: {msg}")

                line = ser.readline()

                print(line.decode()[1:])
                
                input("Press enter to continue\n")

    except serial.SerialException as exc:
        print("Serial error:", exc)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()