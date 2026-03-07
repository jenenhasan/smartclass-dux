# 🏫 Smart Classroom Control System

A real-time IoT classroom management system that combines **gesture-controlled device management**, **WebRTC live video streaming**, and a **web dashboard** for monitoring environmental sensors and controlling classroom devices — all running on a Raspberry Pi.

---

## 🛠️ Built With

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-333333?style=for-the-badge&logo=webrtc&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white)

---

## ✨ Features

### 🤚 Gesture Control
Control classroom devices hands-free using a live camera feed and MediaPipe hand landmark detection. A simple hand gesture (thumb vs. index finger position) toggles devices **on** or **off** without touching anything.

### 📡 WebRTC Video Streaming
Streams live camera footage from the Raspberry Pi to any connected laptop or browser using WebRTC peer-to-peer connections, with a WebSocket signaling server handling the offer/answer/ICE handshake.

### 📽️ Projector Output via GStreamer
Decoded video frames are piped directly to a projector or display using a GStreamer pipeline — no GUI required.

### 🌡️ Sensor Dashboard
Pulls real-time **temperature and humidity** data from the classroom's sensor API and displays it on the web dashboard.

### 🔘 Manual Device Switches
All devices can also be controlled manually through toggle switches on the web UI — no gestures needed.

---

## 📁 Project Structure

```
smart-classroom/
├── webrtc_server.py        # WebRTC signaling server — streams camera via WebSocket (port 8765)
├── projector_display.py    # Receives video track and pipes frames to projector via GStreamer
├── app.py                  # Flask web server — gesture control, sensor API, device control
├── templates/
│   └── index.html          # Web dashboard UI
├── static/
│   └── style.css           # Dashboard styling (maroon university theme)
└── requirements.txt
```

---

## 🖥️ System Architecture

```
Raspberry Pi Camera
        │
        ▼
┌─────────────────────────┐        WebSocket (port 8765)       ┌──────────────┐
│   WebRTC Server         │ ◄──────────────────────────────── │  Laptop /    │
│   (webrtc_server.py)    │ ────── Video Stream (WebRTC) ────► │  Browser     │
└─────────────────────────┘                                     └──────────────┘
        │
        ▼
┌─────────────────────────┐        HTTP (port 5000)            ┌──────────────┐
│   Flask App             │ ◄──────────────────────────────── │  Web UI      │
│   (app.py)              │ ─── Sensor data / device state ──► │  Dashboard   │
└─────────────────────────┘                                     └──────────────┘
        │
        ▼
┌─────────────────────────┐
│  Remote API             │  https://smartclass.serveo.net
│  - /sensor_data         │  ← Temperature & Humidity
│  - /control             │  ← Lamp / Projector / AC
└─────────────────────────┘
```

---

## 🚀 Getting Started

### Hardware Requirements

- Raspberry Pi (3B+ or 4 recommended)
- Pi Camera Module or USB webcam
- Classroom devices connected to the remote API (lamp, projector, AC)
- Projector with HDMI/display connection for GStreamer output

### Software Prerequisites

- Python 3.9+
- GStreamer installed on the Pi:
```bash
sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

### Installation

```bash
git clone https://github.com/your-username/smart-classroom.git
cd smart-classroom
pip install -r requirements.txt
```

---

## ▶️ Usage

### Start the Flask Web Dashboard

```bash
python app.py
```

Open `http://<raspberry-pi-ip>:5000` in a browser on any device on the same network.

### Start the WebRTC Streaming Server

```bash
python webrtc_server.py
```

This starts a WebSocket signaling server at `ws://0.0.0.0:8765`. Connect from a laptop browser using a WebRTC client to receive the live camera stream.

### Start Projector Display

```bash
python projector_display.py
```

Receives the video track and pipes it to the projector via GStreamer's `autovideosink`.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web dashboard |
| `GET` | `/sensor_data` | Fetch temperature & humidity from remote API |
| `POST` | `/control` | Control a device (`device`, `action` in form data) |
| `GET` | `/video_feed/<device>` | MJPEG video stream with gesture detection active |

### Example — Control a Device

```bash
curl -X POST http://<pi-ip>:5000/control \
  -d "device=lamp&action=on"
```

Response:
```json
{ "status": "success", "device": "lamp", "action": "on" }
```

---

## 🤚 Gesture Control Logic

The system uses MediaPipe to detect a single hand and compares the Y-coordinates of the **thumb tip** and **index finger tip**:

```
Thumb tip Y > Index tip Y  →  gesture = "off"  →  device turned off
Thumb tip Y < Index tip Y  →  gesture = "on"   →  device turned on
```

To avoid spamming the API, the gesture is only sent when it **changes** from the previous state (`last_gesture` tracking).

---

## 📟 Controlled Devices

| Device | API key | Default State |
|--------|---------|---------------|
| Lamp | `lamp` | `off` |
| Projector | `projector` | `off` |
| Air Conditioning | `ac` | `off` |

---

## 🔧 Configuration

Update the remote API base URL in `app.py` if your backend changes:

```python
url = 'https://smartclass.serveo.net/control'
```

WebRTC signaling server port (default `8765`) can be changed in `webrtc_server.py`:

```python
async with websockets.serve(handle_webrtc_connection, "0.0.0.0", 8765):
```

---

## 📦 Key Dependencies

```
flask
opencv-python
mediapipe
aiortc
websockets
requests
```

---

## ⚠️ Known Limitations

- Gesture control currently uses a basic thumb/index comparison — lighting conditions can affect detection accuracy.
- GStreamer projector display spawns a new subprocess per frame, which is not optimal for high frame rates. Consider a persistent pipeline for production use.
- The system assumes a single camera input (`cv2.VideoCapture(0)`).

---

## 📄 License

This project is open source. See `LICENSE` for details.
