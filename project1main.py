import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import wave
import csv

def serial_initiate():
    # port = serial.tools.list_ports.comports()[0].device
    port = "COM10"
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

def save_plot(data, filename,sampleRate):
    time_axis = np.arange(len(data))/sampleRate # create time axis based on sample rate and data length
    plt.figure()
    plt.plot(time_axis, data)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Audio Signal")
    plt.savefig(filename)
    print(f"Plot saved to {filename}")

def manual_mode(ser):
    duration = float(input("Enter recording duration in seconds: "))
    sampleRate = 9200
    sampleRate = int(input(f"Enter sample rate (default {sampleRate} Hz tested on the lab): ") or sampleRate)
    data = record_audio(ser, duration)
    if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
        data = (data - data.min()) / (data.max() - data.min()) # scale to 0-1
    else:
        data = np.zeros_like(data) # if there is no variation, just create an array of zeros
    data = data * 255                    # scale to 0-255
    data = data.astype(np.uint8)         # convert to uint8 type
    save_wave("manual_recording.wav", data, sampleRate)
    save_csv("manual_recording.csv", data, sampleRate)
    save_plot(data, "manual_recording.png", sampleRate)


def distance_trigger_mode(ser):
    print("Distance Trigger Mode (press Ctrl+C to exit)")
    stopShortTime = 1.0
    sampleRate = int(input("Enter sample rate (default 9200 Hz tested on the lab): ") or 9200)
    try:
        while True:
            print("Waiting for trigger...")
            trigger = input("simulate triggered?(0/1): ")
            if trigger == "1":
                print("Trigger detected! Starting recording...")
                data = []
                t1 = time.time()
                tf = t1
                while True:
                    still_triggered = input("still triggered?(0/1): ")
                    if still_triggered == "1":
                        tf = time.time()
                        
                    if ser.in_waiting:
                        b = ser.read()
                        data.append(b[0])
                    if time.time() - tf > stopShortTime:
                        print("Trigger released for too long. Stopping recording.")
                        break
                data = np.array(data) # convert to numpy array because we need to do some processing on it
                if len(data) == 0:
                    print("No data recorded. Returning to trigger mode.")
                    continue
                if data.max() != data.min(): # check if there is any variation in the data to avoid division by zero
                    data = (data - data.min()) / (data.max()-data.min()) # scale to 0-1
                    data = data * 255                    # scale to 0-255
                    data = data.astype(np.uint8)         # convert to uint8 type
                else:
                    data = np.zeros_like(data, dtype=np.uint8) # if there is no variation, just create an array of zeros
                
                save_wave(f"distance_trigger_Team14.wav", data, sampleRate)
                save_csv(f"distance_trigger_Team14.csv", data, sampleRate)
                save_plot(data, f"distance_trigger_Team14.png", sampleRate)
    except KeyboardInterrupt:
        print("\rExiting Distance Trigger Mode... \n")
                

                
            

def main():
    ser = serial_initiate()
    if ser is None:
        return
    dots = ["", ".", "..", "...", "....",  "....."]
    idx = 0
    print("Press Ctrl+C to stop loading data.")
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

            match choice:
                case "1":
                    print("Manual Recording Mode selected.")
                    manual_mode(ser)
                case "2":
                    print("Distance Trigger Mode selected.")
                    distance_trigger_mode(ser)
                    # Implement distance trigger functionality here
                case "3":
                    print("Exiting the program.")
                    if ser is not None and ser.is_open:
                        ser.close()
                    break
                case _:
                    print("Invalid choice. Please enter a number between 1 to 3")
                

    except KeyboardInterrupt:
        print("\rProgram stopped. Exiting gracefully... \n")
        if ser is not None and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()