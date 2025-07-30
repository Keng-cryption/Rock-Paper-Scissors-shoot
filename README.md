#  ASL Translator – Real-Time Sign Language Letter Recognition

This project is a **real-time rock paper scissors web app**. It uses a webcam, computer vision, and hand landmark detection to identify rock paper scissors and displays them on a web interface along with a live video stream. then will generate a radnom number which is the computers choices will display it in ASKII and will say who wins and keeps score.

---

##  Features

-  Real-time hand detection using [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
-  Live webcam video feed via OpenCV
-  Clean, responsive HTML interface served through Flask
-  Continual finger state updates and recognized letter stream
-  Public sharing via [ngrok](https://ngrok.com/)
-  Clear button to reset the current word

---

Tech Stack

- **Python 3**
- **OpenCV**
- **MediaPipe**
- **Flask** (Web backend)
- **Ngrok** (for external access)
- **HTML/CSS/JavaScript** (Frontend)

---

Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Keng-cryption/jetson-nano-AI.git
```

### 2. Install Required Python Packages

```bash
pip install opencv-python mediapipe flask flask-cors pyngrok
```

### 3. (Optional) Set Your Ngrok Authtoken

To avoid ngrok errors, authenticate once:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

```bash
/usr/local/bin/python3 -m ensurepip --upgrade
/usr/local/bin/python3 -m pip install --upgrade pip setuptools wheel
```

```bash
/usr/local/bin/python3 -m pip install --user opencv-python mediapipe flask flask-cors
```

```bash
/usr/local/bin/python3 -m pip --version
/usr/local/bin/python3 -m pip list
```

```bash
/usr/local/bin/python3 -m venv myenv
source myenv/bin/activate
pip install --upgrade pip setuptools wheel
pip install opencv-python mediapipe flask flask-cors
python /Users/henrykent/Rock-Paper-Scissors-shoot/Main.py
```

```bash
/usr/local/bin/python3 -m pip install --break-system-packages --user opencv-python mediapipe flask flask-cors
```

---

Run the App

```bash
python main.py
```

After startup:

- You'll see a **public ngrok URL** in the terminal.
- Open that URL in your browser to access the live game web interface.
- REMEMBER PORT FOWARD 5000
  
Web Interface

- **Live camera feed** showing hand detection
- **Current Word**: showing output in real time
- **Finger State**: Binary values for thumb/index/middle/ring/pinky
- if the screen that should should the skeleton of your hand is black run the code again

Recognized Letters

The app detects most letters based on finger positions:

- index finger and middle finger up is scissors
- all fingers up including thumb is paper
- no fingers up is rock


Troubleshooting

- **Black video screen?** Make sure your webcam is accessible and not used by another app.
- **Ngrok not working?** Check your internet connection and ngrok token.
- **Performance issues?** Reduce resolution or run on a faster device (like Jetson Nano or Pi 4).

Video

 - Video: https://www.youtube.com/watch?v=AKm7fvq1bv4
