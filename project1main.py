import serial
from serial.tools.list_ports import comports
import time
import numpy as np
import matplotlib.pyplot as plt
import wave
import csv
from scipy.signal import butter, filtfilt

def apply_lpf(data,fs = 44100,cutoff = 5500,order=4):
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low')
    filtered = filtfilt(b, a, data)
    return filtered.astype(np.uint16)

def apply_hpf(data, fs=44100, cutoff=80, order=4):
    nyq = fs / 2
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high')
    filtered = filtfilt(b, a, data)
    return filtered.astype(np.int16)

def serial_initiate():
    port = serial.tools.list_ports.comports()[0].device
    # port = "COM10"
    baudrate = 921600

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


def record_audio(ser, duration, sampleRate):
    data = []
    ser.reset_input_buffer()
    raw = ser.read(int(duration * sampleRate) * 2)  # read all bytes at once
    i = 0
    while (i<len(raw)-2):
        if ((raw[i+1]>>4)^0): #this SHOULD BE FALSE
            i += 1
            continue
        sample = (raw[i+1] << 8) | raw[i]
        i+=2
        # print(sample)
        data.append(sample)

    return np.array(data)
            

def save_wave(filename, data, sampleRate):
    with wave.open(filename, 'wb') as wf: 
        wf.setnchannels(1)              
        # mono audio (single channel) 
        wf.setsampwidth(2)              
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

def manual_mode(ser,sampleRate):
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
        
    data = record_audio(ser, duration, sampleRate)
    if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
        data = (data - data.min()) / (data.max() - data.min()) # scale to 0-1
    else:
        data = np.zeros_like(data,dtype=np.uint16) # if there is no variation, just create an array of zeros
    data = data * (2**12-1)
    data = data.astype(np.uint16)      # convert to uint16 type
    return data

def distance_trigger_mode(ser):
    print("Distance Trigger Mode (press Ctrl+C to exit)")
    stopShortTime = 2.0 

    ser.reset_input_buffer()
    data = []
    ser.timeout = 5
    b = ser.read(2) #only start timing after the first byte is received
    if len(b) == 0:
        print("Timed out")
        return
    
    print("Recording Begun")
    ser.timeout = stopShortTime
    raw = b''
    while True:
        chunk = ser.read(1024)
        if not chunk:  # this chunk timed out = no data for `timeout` seconds
            break
        raw += chunk
    i = 0;
    while (i<len(raw)-2):
        if ((raw[i+1]>>4)^0): #this SHOULD BE FALSE
            i += 1
            continue
        sample = (raw[i+1] << 8) | raw[i]
        i+=2
    # print(sample)
        data.append(sample)
    print("Recording Finished")

    data = np.array(data) # convert to numpy array because we need to do some processing on it

    if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
        data = (data - data.min()) / (data.max()-data.min()) # scale to 0-1
        data = data * (2**12-1)                    
        data = data.astype(np.uint16)         # convert to uint16 type
    else:
        data = np.zeros_like(data, dtype=np.uint16) # if there is no variation, just create an array of zeros

    ser.timeout = None
    return data
            
        
                
            
def main():
    ser = serial_initiate()
    if ser is None:
        return
    ser.write("i".encode()) #send this flag to STM2
    print("Press Ctrl+C to stop loading data.")
    sampleRate = 44100
    try:
        while True:
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
                    data = manual_mode(ser,sampleRate)
                    ser.write("i".encode()) #send this flag to STM2

                case "2":
                    print("Distance Trigger Mode selected.")

                    ser.write("d".encode()) #send this flag to STM2
                    data = distance_trigger_mode(ser)
                    ser.write("i".encode()) #send this flag to STM2

                case "3":
                    print("Exiting the program.")
                    if ser is not None and ser.is_open:
                        ser.close()
                    break
                case _:
                    print("Invalid choice. Please enter a number between 1 to 3")
                    continue
            
            if data is None: continue
            while True:
                decision = input("Do you want to apply a noise filter? (Y/N): ")
                match decision.lower():
                    case "y":
                        filtered_data_0 = apply_lpf(data)
                        filtered_data = apply_hpf(filtered_data_0)
                        break
                    case "n":
                        filtered_data = data
                        break
                    case _:
                        print("Please enter Y/N")
                        continue
            while True:
                # filtered_data = data
                print("Possible File Formats:")
                print("1. wav")
                print("2. png")
                print("3. csv")
                print("4. return to main menu")
                try:
                    filetype = input("Enter your choice (1-4): ")
                    timestamp = int(time.time())
                    match filetype:
                        case "1":
                            print("Saving as wav file")
                            save_wave(f"Team_I_14_{sampleRate}_{timestamp}.wav",filtered_data,sampleRate)
                        case "2":
                            print("Saving as png file")
                            save_plot(f"Team_I_14_{sampleRate}_{timestamp}", filtered_data, sampleRate)
                        case "3":
                            print("Saving as csv file")
                            save_csv(f"Team_I_14_{sampleRate}_{timestamp}.csv", filtered_data, sampleRate)
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