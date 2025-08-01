import cv2
import mediapipe as mp
import time
import threading
import random
from flask import Flask, jsonify, render_template_string, Response
from flask_cors import CORS

# Shared state
player_choice = ""
computer_choice = ""
result = ""
current_gesture = None
player_score = 0
computer_score = 0
frame_for_stream = None
lock = threading.Lock()

# Flask app
app = Flask(__name__)
CORS(app)

ASCII_ART = {
    "Rock": """
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
""",
    "Paper": """
     _______
---'    ____)____
           ______)
          _______)
         _______)
---.__________)
""",
    "Scissors": """
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
""",
    "": "Waiting...",
    None: "Waiting..."
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rock Paper Scissors</title>
    <style>
        body {
            font-family: sans-serif;
            background: #1E2229;
            color: white;
            padding: 30px;
            margin: 0;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }
        .video-section {
            margin-right: 40px;
        }
        .ascii-section {
            white-space: pre;
            font-family: monospace;
            font-size: 1em;
            background: #2A2E38;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 15px #000;
            max-width: 300px;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        p {
            font-size: 1.3em;
            margin: 5px 0;
        }
        #countdown {
            font-size: 2em;
            margin-top: 20px;
            color: #1E7A54;
            font-weight: bold;
            text-align: center;
        }
        .gesture-label {
            font-weight: bold;
            color: #00FFAA;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>Rock Paper Scissors with Hand Gestures</h1>

    <div class="container">
        <div class="video-section">
            <img id="video" src="/video_feed" width="640" height="480">
            <div>
                <p id="player">Player: Loading...</p>
                <p id="computer">Computer: Loading...</p>
                <p id="result">Result: Loading...</p>
                <p id="score">Score - Player: 0 | Computer: 0</p>
                <p id="countdown">Get ready: 3</p>
            </div>
        </div>

        <div class="ascii-section">
            <div class="gesture-label">Computer's Gesture:</div>
            <pre id="ascii_art">Loading...</pre>
        </div>
    </div>

    <script>
        let countdownValue = 3;
        const countdownElement = document.getElementById("countdown");

        async function fetchData() {
            const res = await fetch('/status');
            const data = await res.json();

            document.getElementById("player").textContent = "Player: " + data.player;
            document.getElementById("computer").textContent = "Computer: " + data.computer;
            document.getElementById("result").textContent = "Result: " + data.result;
            document.getElementById("score").textContent = 
                "Score - Player: " + data.player_score + " | Computer: " + data.computer_score;
            document.getElementById("ascii_art").textContent = data.ascii_art;
        }

        async function playRound() {
            await fetch('/reset');
            fetchData();
        }

        function startCountdown() {
            countdownValue = 3;
            countdownElement.textContent = "Get ready: " + countdownValue;

            const interval = setInterval(() => {
                countdownValue--;
                if (countdownValue > 0) {
                    countdownElement.textContent = "Get ready: " + countdownValue;
                } else {
                    countdownElement.textContent = "Go!";
                    playRound();
                    setTimeout(() => {
                        startCountdown();
                    }, 1000);
                    clearInterval(interval);
                }
            }, 1000);
        }

        fetchData();
        startCountdown();
        setInterval(fetchData, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/status')
def status():
    with lock:
        return jsonify(
            player=player_choice,
            computer=computer_choice,
            result=result,
            player_score=player_score,
            computer_score=computer_score,
            ascii_art=ASCII_ART.get(computer_choice, "Waiting...")
        )

@app.route('/reset')
def reset():
    global player_choice, computer_choice, result, player_score, computer_score, current_gesture
    with lock:
        if current_gesture:
            player_choice = current_gesture
            computer_choice = random.choice(["Rock", "Paper", "Scissors"])
            result = determine_winner(player_choice, computer_choice)

            if result == "Player Wins":
                player_score += 1
            elif result == "Computer Wins":
                computer_score += 1
        else:
            player_choice = "No Gesture"
            computer_choice = ""
            result = "No valid gesture detected"

    return jsonify(success=True)

@app.route('/video_feed')
def video_feed():
    def generate_video():
        global frame_for_stream
        while True:
            if frame_for_stream is None:
                continue
            ret, buffer = cv2.imencode('.jpg', frame_for_stream)
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Gesture recognition
def finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y

def get_finger_states(lm):
    return {
        'thumb': lm[4].x < lm[3].x,
        'index': finger_up(lm, 8, 6),
        'middle': finger_up(lm, 12, 10),
        'ring': finger_up(lm, 16, 14),
        'pinky': finger_up(lm, 20, 18)
    }

def classify_gesture(f):
    thumb = f['thumb']
    fingers = [int(f['index']), int(f['middle']), int(f['ring']), int(f['pinky'])]

    if not thumb and fingers == [0, 0, 0, 0]:
        return "Rock"
    if thumb and fingers == [1, 1, 1, 1]:
        return "Paper"
    if not thumb and fingers == [1, 1, 0, 0]:
        return "Scissors"
    return None

def determine_winner(player, computer):
    if player == computer:
        return "Draw"
    wins = {
        "Rock": "Scissors",
        "Scissors": "Paper",
        "Paper": "Rock"
    }
    return "Player Wins" if wins[player] == computer else "Computer Wins"

# Camera thread
def camera_thread():
    global frame_for_stream, current_gesture

    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    drawing = mp.solutions.drawing_utils

    with mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        last_sign = ""
        last_time = 0
        delay = 2.0

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_hands = hands.process(rgb)

            if result_hands.multi_hand_landmarks:
                hand_landmarks = result_hands.multi_hand_landmarks[0]
                drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if time.time() - last_time > delay:
                    landmarks = hand_landmarks.landmark
                    fingers = get_finger_states(landmarks)
                    gesture = classify_gesture(fingers)

                    if gesture and gesture != last_sign:
                        last_sign = gesture
                        last_time = time.time()
                        with lock:
                            current_gesture = gesture

            with lock:
                frame_for_stream = frame.copy()

    cap.release()

# Start app
if __name__ == '__main__':
    threading.Thread(target=camera_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
