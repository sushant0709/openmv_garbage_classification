import sensor, image, time, os, ml, uos, gc, network, json
import usocket as socket
from ulab import numpy as np
import random  # Import the random module to choose random values

CONFIDENCE_THRESHOLD = 0.8  # Adjust this value as needed (0.8 = 80% confidence)
COOLDOWN_PERIOD = 10
last_submission_time = 0

# Add these global variables
last_ntp_sync = 0
local_time_offset = 0
NTP_SYNC_INTERVAL = 3600  # Sync with NTP server every hour

def get_ntp_time():
    NTP_SERVER = "pool.ntp.org"
    NTP_PORT = 123
    TIME_OFFSET = 2208988800  # Epoch time offset (1970-01-01 to 1900-01-01)

    addr = socket.getaddrinfo(NTP_SERVER, NTP_PORT)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    try:
        ntp_packet = bytearray(48)
        ntp_packet[0] = 0x1B  # LI=0, VN=3, Mode=3 (client)
        s.sendto(ntp_packet, addr)

        msg, _ = s.recvfrom(48)
        if len(msg) == 48:
            t = (msg[40] << 24 | msg[41] << 16 | msg[42] << 8 | msg[43]) - TIME_OFFSET
            return t
        else:
            print("Invalid NTP response length.")
            return None
    except Exception as e:
        print("NTP error:", e)
        return None
    finally:
        s.close()

def get_current_time():
    global last_ntp_sync, local_time_offset

    current_local_time = time.time()

    # Check if it's time to sync with NTP
    if current_local_time - last_ntp_sync >= NTP_SYNC_INTERVAL:
        ntp_time = get_ntp_time()
        if ntp_time is not None:
            local_time_offset = ntp_time - current_local_time
            last_ntp_sync = current_local_time
            print("NTP sync successful. Offset:", local_time_offset)
        else:
            print("NTP sync failed. Using local time.")

    return current_local_time + local_time_offset

def http_post(url, data, headers=None):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)

    content = json.dumps(data)
    content_type = "application/json"
    content_length = len(content)
    print("in post function")
    request = f"POST /{path} HTTP/1.0\r\nHost: {host}\r\n"
    request += f"Content-Type: {content_type}\r\n"
    request += f"Content-Length: {content_length}\r\n"
    if headers:
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
    request += "\r\n" + content

    s.send(request.encode())

    response = s.recv(4096)
    s.close()

    return response.decode('utf-8')

# WiFi and Server Config
SSID = "AndroidAP_1964" /* Add your SSID */
KEY = "3be004bcc2c0" /* Add your WiFi password */
URL = "https://sushantk.pythonanywhere.com/api/upload"

# Initialize Camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((240, 240))
sensor.skip_frames(time=2000)

# Load Model and Labels
try:
    net = ml.Model("trained_gc2.tflite", load_to_fb=True)
except Exception as e:
    raise Exception('Failed to load "trained_gc2.tflite". Ensure the file is on the device. (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels_gc2.txt")]
except Exception as e:
    raise Exception('Failed to load "labels_gc2.txt". Ensure the file is on the device. (' + str(e) + ')')

# WiFi Setup
wlan = network.WLAN()
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print(f'Trying to connect to "{SSID}"...')
    time.sleep_ms(1000)

print("WiFi Connected:", wlan.ifconfig())

# Categorization Rules
recyclable_classes = ["Recyclabe"]
organic_classes = ["kitchen"]  # Add organic classes if applicable
hazardous_classes = ["Harmful"]
other_classes = ["Other"]

# Initialize Data
bin_ids = ["BIN_001", "BIN_002", "BIN_003", "BIN_004", "BIN_005", "BIN_006", "BIN_007", "BIN_008", "BIN_009", "BIN_010"]
bin_locations = ["Location_A", "Location_B", "Location_C", "Location_D", "Location_E"]

while True:
    clock = time.clock()
    clock.tick()
    img = sensor.snapshot()
    current_timestamp = get_current_time()

    if current_timestamp - last_submission_time >= COOLDOWN_PERIOD:
        try:
            # Run prediction
            predictions = list(zip(labels, net.predict([img])[0].flatten().tolist()))
            predictions.sort(key=lambda x: x[1], reverse=True)

            # Get the top prediction
            top_label, top_probability = predictions[0]

            # Only proceed if the confidence is above the threshold
            if top_probability >= CONFIDENCE_THRESHOLD:
                # Categorize based on the class
                if top_label in recyclable_classes:
                    category = "Recyclable"
                elif top_label in organic_classes:
                    category = "Organic"
                elif top_label in hazardous_classes:
                    category = "Hazardous"
                elif top_label in other_classes:
                    category = "Other"
                else:
                    category = "Unknown"

                # Randomly select bin_id and bin_location from the predefined lists
                bin_id = random.choice(bin_ids)
                bin_location = random.choice(bin_locations)

                # Prepare payload
                payload = {
                    "timestamp": current_timestamp,
                    "bin_id": bin_id,
                    "bin_location": bin_location,
                    "category": category,
                    "class_name": top_label,
                    "probability": round(top_probability, 2),
                }

                # Send data to server
                headers = {'Content-Type': 'application/json'}
                response = http_post(URL, payload, headers)

                print("Posted data:", payload)
                status_line = response.split('\n')[0]
                status_code = int(status_line.split(' ')[1])
                print("Server response status code:", status_code)
            else:
                print(f"Prediction confidence ({top_probability:.2f}) below threshold. Not sending data.")

        except Exception as e:
            print("Error:", e)

        print(clock.fps(), "fps")
        last_submission_time = current_timestamp

    else:
        pass
        # print("Cooldown period active. Skipping submission.")
