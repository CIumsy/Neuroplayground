import asyncio
import threading
import time
import keyboard  # pip install keyboard
from bleak import BleakScanner, BleakClient
from pylsl import StreamInfo, StreamOutlet

###############################################
# Utility and Timing Functions
###############################################

# Global key mapping variables for npg2
key_left_npg2 = "j"   # used when channel1 > channel3
key_right_npg2 = "l"  # used when channel3 > channel1

def millis():
    return int(round(time.time() * 1000))

# Hold time (in ms): if no envelope above threshold is seen for this duration, release key.
HOLD_TIME = 200

###############################################
# BLE Acquisition, Normalization, and Envelope
###############################################

# Normalize a raw 12-bit ADC sample (range ~0-4095) to roughly -1 to 1.
def normalize_sample(sample):
    a = 2**12  # 4096
    return (sample - a/2) * (2 / a)

# Smoothing constant (alpha) for exponential moving average
ALPHA = 0.2

# Initialize envelope values for each of 3 channels
envelopes = [0.0, 0.0, 0.0]

# BLE parameters (adjust to your device)
DEVICE_NAME = "NPG-30:30:f9:f9:db:6e"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
DATA_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
CONTROL_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Packet parameters
SINGLE_SAMPLE_LEN = 7              # Each sample is 7 bytes
BLOCK_COUNT = 10                   # 10 samples per notification
NEW_PACKET_LEN = SINGLE_SAMPLE_LEN * BLOCK_COUNT  # Total packet length

# Set up an LSL stream (if needed)
stream_name = "NPG"
info = StreamInfo(stream_name, "EXG", 3, 250, "float32", "uid007")
outlet = StreamOutlet(info)

# Global tracking variables
prev_unrolled_counter = None
samples_received = 0
start_time = None
total_missing_samples = 0

###############################################
# Keyboard Control Variables
###############################################

# current_key holds the currently pressed key ("j" or "l") or None
current_key = None
# last_trigger_time holds the last time (in ms) an envelope above threshold was seen
last_trigger_time = 0

###############################################
# Process a Single BLE Sample and Update Keyboard State
###############################################

def process_sample(sample_data: bytearray):
    global prev_unrolled_counter, samples_received, start_time, total_missing_samples, envelopes
    global current_key, last_trigger_time

    if len(sample_data) != SINGLE_SAMPLE_LEN:
        print("Unexpected sample length:", len(sample_data))
        return

    # Unpack sample: Byte0 is packet counter; bytes 1-2, 3-4, 5-6 are ADC data for channels 1,2,3
    sample_counter = sample_data[0]
    if prev_unrolled_counter is None:
        prev_unrolled_counter = sample_counter
    else:
        last = prev_unrolled_counter % 256
        if sample_counter < last:
            current_unrolled = prev_unrolled_counter - last + sample_counter + 256
        else:
            current_unrolled = prev_unrolled_counter - last + sample_counter
        if current_unrolled != prev_unrolled_counter + 1:
            print(f"Missing sample: expected {prev_unrolled_counter+1}, got {current_unrolled}")
            total_missing_samples += current_unrolled - (prev_unrolled_counter+1)
        prev_unrolled_counter = current_unrolled

    if start_time is None:
        start_time = time.time()
    elapsed = time.time() - start_time

    channels = []
    for ch in range(3):
        offset = 1 + ch * 2
        value = int.from_bytes(sample_data[offset:offset+2], byteorder='big', signed=True)
        channels.append(value)
    normalized_channels = [normalize_sample(val) for val in channels]

    # Compute envelope using exponential moving average (after rectification)
    enveloped_channels = []
    for i, norm_val in enumerate(normalized_channels):
        rectified = abs(norm_val)
        envelopes[i] = ALPHA * rectified + (1 - ALPHA) * envelopes[i]
        enveloped_channels.append(envelopes[i])
    
    # print(f"Sample {prev_unrolled_counter} at {elapsed:.2f} s:")
    # print(f"  Raw: {channels}")
    # print(f"  Normalized: {normalized_channels}")
    # print(f"  Enveloped: {enveloped_channels} (Missing: {total_missing_samples})")
    
    # Send data via LSL outlet (if needed)
    outlet.push_sample(enveloped_channels)
    samples_received += 1

    # Classification: use channel1 (index 0) and channel3 (index 2) with threshold
    threshold = 0.2
    desired_direction = None
    if enveloped_channels[0] > threshold or enveloped_channels[2] > threshold:
        if enveloped_channels[0] > enveloped_channels[2]:
            desired_direction = key_left_npg2
        elif enveloped_channels[2] > enveloped_channels[0]:
            desired_direction = key_right_npg2

    now = millis()
    if desired_direction is not None:
        # Reset hold timer whenever an envelope above threshold is received.
        last_trigger_time = now
        # If no key is pressed, press desired key.
        if current_key is None:
            keyboard.press(desired_direction)
            print(f"{desired_direction} pressed")
            current_key = desired_direction
        # If a different key is desired, switch immediately.
        elif current_key != desired_direction:
            keyboard.release(current_key)
            print(f"{current_key} released")
            keyboard.press(desired_direction)
            print(f"{desired_direction} pressed")
            current_key = desired_direction
        # If same key is already pressed, simply update the last trigger time.
    else:
        # If no envelope exceeds threshold and key is pressed, check if 200ms passed.
        if current_key is not None and (now - last_trigger_time >= HOLD_TIME):
            keyboard.release(current_key)
            print(f"{current_key} released due to inactivity")
            current_key = None

def notification_handler(sender, data: bytearray):
    if len(data) == NEW_PACKET_LEN:
        for i in range(0, NEW_PACKET_LEN, SINGLE_SAMPLE_LEN):
            sample = data[i:i+SINGLE_SAMPLE_LEN]
            process_sample(sample)
    elif len(data) == SINGLE_SAMPLE_LEN:
        process_sample(data)
    else:
        print("Unexpected packet length:", len(data))

async def print_rate():
    global samples_received
    while True:
        await asyncio.sleep(1)
        print(f"Samples per second: {samples_received}")
        samples_received = 0

async def run():
    while True:
        try:
            print("Scanning for BLE devices...")
            devices = await BleakScanner.discover()
            target = None
            for d in devices:
                if d.name and DEVICE_NAME.lower() in d.name.lower():
                    target = d
                    break
            if target is None:
                print("Device not found. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            print("Found device:", target)
            async with BleakClient(target) as client:
                if not client.is_connected:
                    print("Failed to connect. Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                print("Connected to", target.name)
                await client.write_gatt_char(CONTROL_CHAR_UUID, b"START", response=True)
                print("Sent START command")
                await client.start_notify(DATA_CHAR_UUID, notification_handler)
                print("Subscribed to data notifications")
                asyncio.create_task(print_rate())
                # Stay in the connection until it drops.
                while client.is_connected:
                    await asyncio.sleep(0.01)
        except Exception as e:
            print("Connection error:", e)
        print("Connection lost or error encountered. Retrying in 5 seconds...")
        await asyncio.sleep(5)


def ble_thread():
    asyncio.run(run())

###############################################
# Main Execution: Start BLE Acquisition Thread
###############################################

if __name__ == "__main__":
    ble_thread_instance = threading.Thread(target=ble_thread, daemon=True)
    ble_thread_instance.start()
    # Main thread simply idles.
    while True:
        time.sleep(0.1)
