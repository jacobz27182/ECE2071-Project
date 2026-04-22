import numpy as np
import wave
import serial
from serial.tools import list_ports
import time


def main():
    # port = serial.tools.list_ports.comports()[0].device
    port = "COM10"
    baudrate = 115200
    SAMPLE_RATE = 9200 

    try:
        with serial.Serial(port=port, baudrate=baudrate) as ser:
            print(f"Connected to {port} at {baudrate} baud")
            data = []
            t1 = time.time()
            for i in range(5*SAMPLE_RATE):
                b = ser.read()
                data.append(b[0])
            print(time.time()-t1)
            data = np.array(data)
            
            print(data)
            data = (data - data.min()) / data.max() # scale to 0-1 
            data = data * 255                    
            # scale to 0-255 
            data = data.astype(np.uint8)
            # convert to uint8 type 

            with wave.open("output.wav", 'wb') as wf: 
                wf.setnchannels(1)              
                # mono audio (single channel) 
                wf.setsampwidth(1)              
                # 8 bits (1 byte ) per sample 
                wf.setframerate(SAMPLE_RATE)    
                # set the sample rate that the data was recorded at 
                wf.writeframes(data.tobytes())  # write the audio data to the file 
    except serial.SerialException as exc:
        print("Serial error:", exc)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()