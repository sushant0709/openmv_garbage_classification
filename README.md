# Garbage Classification System

## Overview

This project is an embedded machine vision system for real-time waste classification using the OV5652 camera module on an OpenMV board. The system utilizes a pre-trained TensorFlow Lite model from Edge Impulse to classify waste as organic or recyclable.

Additionally, the system is integrated with a Flask-based backend, where it sends categorized waste data via HTTP POST requests to a cloud-hosted server for logging and further processing.

## Features

- Real-time waste classification using an OpenMV camera module

- Edge AI model inference with TensorFlow Lite

- WiFi-enabled data transmission to a Flask-based backend server

- NTP synchronization for accurate timestamps in data logging

## Hardware Requirements

- OpenMV board with OV5652 camera module

- WiFi connectivity module

- Power source (USB or battery pack)

## Software Requirements

- Python (MicroPython) for embedded firmware

- Edge Impulse trained model (trained_gc2.tflite)

- Flask-based backend server for data collection

- Network and socket programming for HTTP communication

## Installation & Setup

1. Setting Up OpenMV

   Install OpenMV IDE and flash the latest firmware.
   Copy trained_gc2.tflite and labels_gc2.txt to the device.
   Connect the OpenMV board to your system and verify the camera is detected.

2. Configuring WiFi

   Update the following credentials in the script:

   SSID = "Your_WiFi_Name"
   KEY = "Your_WiFi_Password"

3. Running the Script

   Deploy the script to the OpenMV board.

   Ensure the Flask backend is running and accessible.

   The script will capture images, classify them, and send the data to the server.

   Data Transmission

   The device makes HTTP POST requests to:

   URL = "https://sushantk.pythonanywhere.com/api/upload"

   The payload contains:

   {
   "timestamp": 1700000000,
   "bin_id": "BIN_001",
   "bin_location": "Location_A",
   "category": "Recyclable",
   "class_name": "Plastic Bottle",
   "probability": 0.92
   }

## Future Enhancements

- Add more waste categories for finer classification.

- Improve model accuracy with additional training data.

- Optimize network communication for lower latency.

## Author

Sushant Khattar

For any queries, feel free to reach out via [LinkedIn](https://www.linkedin.com/in/sushantkhattar).
