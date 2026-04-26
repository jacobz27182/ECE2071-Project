import serial
from serial.tools.list_ports import comports
import time
import numpy as np
import matplotlib.pyplot as plt
import wave
import csv

def serial_initiate():
    port = serial.tools.list_ports.comports()[0].device
    # port = "COM10"
    baudrate = 115200

    try:
        ser = serial.Serial(port=port, baudrate=baudrate)
        print(f"Connected to {port} at {baudrate} baud")
        return ser
            
    except serial.SerialException as exc:
        print("Serial error:", exc)
        return None
    except KeyboardInterrupt:
        print("Stopped by user")
        return None


def record_audio(ser, duration):
    data = []
    t1 = time.time()
    dots = ["", ".", "..", "...", "....",  "....."]
    idx = 0
    while time.time() - t1 < duration:
        b = ser.read()
        data.append(b[0])
        print(f"\rRecording{dots[idx % len(dots)]}", end="", flush=True)
        idx += 1
        #time.sleep(0.5)
                
    print(f"Recording completed in {time.time() - t1:.2f} seconds")
    return np.array(data)

def save_wave(filename, data, sampleRate):
    with wave.open(filename, 'wb') as wf: 
        wf.setnchannels(1)              
        # mono audio (single channel) 
        wf.setsampwidth(1)              
        # 8 bits (1 byte ) per sample 
        wf.setframerate(sampleRate)    
        # set the sample rate that the data was recorded at 
        wf.writeframes(data.tobytes())  # write the audio data to the file
        print(f"Audio saved to {filename}")

def save_csv(filename, data, sampleRate):
    with open(filename, 'w', newline='') as fp:
        writer = csv.writer(fp)
        # First row = sample rate only
        writer.writerow([sampleRate])
        # Following rows = raw data
        for d in data:
            writer.writerow([d])
    print(f"Data saved to {filename}")

def save_plot(filename, data, sampleRate):
    time_axis = np.arange(len(data))/sampleRate # create time axis based on sample rate and data length
    plt.figure()
    plt.plot(time_axis, data)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Audio Signal")
    plt.savefig(filename)
    print(f"Plot saved to {filename}")

def manual_mode(ser):
    while True:
        try:
            duration = float(input("Enter recording duration in seconds: "))
            if duration < 0: raise ValueError
            break
        except ValueError:  
            print("Please enter a positive float")
            continue
        except KeyboardInterrupt:
            return
        
    data = record_audio(ser, duration)
    if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
        data = (data - data.min()) / (data.max() - data.min()) # scale to 0-1
    else:
        data = np.zeros_like(data) # if there is no variation, just create an array of zeros
    data = data * 255                    # scale to 0-255
    data = data.astype(np.uint8)         # convert to uint8 type
    return data

def distance_trigger_mode(ser):
    print("Distance Trigger Mode (press Ctrl+C to exit)")
    stopShortTime = 1.0 

    ser.reset_input_buffer()
    try:
        data = []
        ser.timeout = 20
        b = ser.read() #only start timing after the first byte is received
        if len(b) == 0:
            print("Timed out")
            return
        
        print("Recording Begun")
        data.append(b[0]) 
        ser.timeout = stopShortTime
        while True: 
            b = ser.read()
            if len(b)==0: break #timed out
            data.append(b[0])

        print("Recording Finished")
        data = np.array(data) # convert to numpy array because we need to do some processing on it

        if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
            data = (data - data.min()) / (data.max()-data.min()) # scale to 0-1
            data = data * 255                    # scale to 0-255
            data = data.astype(np.uint8)         # convert to uint8 type
        else:
            data = np.zeros_like(data, dtype=np.uint8) # if there is no variation, just create an array of zeros

        ser.timeout = None
        return data
            
        
    except KeyboardInterrupt:
        print("\rExiting Distance Trigger Mode... \n")
        ser.timeout = None
        return
                
            

def main():
    ser = serial_initiate()
    if ser is None:
        return
    dots = ["", ".", "..", "...", "....",  "....."]
    idx = 0
    print("Press Ctrl+C to stop loading data.")
    sampleRate = 9200
    try:
        Flag = True
        round = 0
        while True:
            '''
            while Flag:
                print(f"\rLoading{dots[idx % len(dots)]}", end="", flush=True)
                idx += 1
                round = round + 1
                time.sleep(0.5)
                if round > 10:
                    Flag = False'''
            print("\n===== AUDIO SYSTEM MENU =====")
            print("1. Manual Recording Mode")
            print("2. Distance Trigger Mode")
            print("3. Exit")            
            choice = input("Enter your choice (1-3): ")

            
            data = None
            match choice:
                case "1":
                    print("Manual Recording Mode selected.")

                    ser.write("m".encode()) #send this flag to STM2
                    data = manual_mode(ser)

                case "2":
                    print("Distance Trigger Mode selected.")

                    ser.write("d".encode()) #send this flag to STM2
                    data = distance_trigger_mode(ser)

                case "3":
                    print("Exiting the program.")
                    if ser is not None and ser.is_open:
                        ser.close()
                    break
                case _:
                    print("Invalid choice. Please enter a number between 1 to 3")
                    continue
            
            while data is not None:
                print("Possible File Formats:")
                print("1. wav")
                print("2. png")
                print("3. csv")
                print("4. return to main menu")
                try:
                    filetype = input("Enter your choice (1-3): ")
                    match filetype:
                        case "1":
                            print("Saving as wav file")
                            save_wave(f"Team_I_14_{sampleRate}.wav",data,sampleRate)
                        case "2":
                            print("Saving as png file")
                            save_plot(f"Team_I_14_{sampleRate}", data, sampleRate)
                        case "3":
                            print("Saving as csv file")
                            save_csv(f"Team_I_14_{sampleRate}.csv", data, sampleRate)
                        case "4":
                            break
                        case _:
                            print("Invalid choice. Please enter a number between 1 to 3")
                            continue
                except KeyboardInterrupt:
                    break

    except (KeyboardInterrupt, EOFError):
        try:
            print("\rProgram stopped. Exiting gracefully... \n")
            if ser is not None and ser.is_open:
                ser.close()
        except KeyboardInterrupt:
            if ser is not None and ser.is_open:
                ser.close()

if __name__ == "__main__":
    main()