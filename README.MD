# NeuroPlayground

**NeuroPlayground** is an innovative project that utilizes 6-channel EMG (electromyography) data collected from your muscles to send keystrokes to your laptop. By interpreting hand gestures through muscle activity, this project allows you to control games in a novel and interactive way.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

NeuroPlayground harnesses muscle signals captured via EMG sensors to translate your hand gestures into keyboard commands. This technology provides an alternative way to interact with games and software, making it accessible and engaging.

## Features

- **6-Channel EMG Data Input:** Capture detailed muscle signals for precise gesture detection.
- **Gesture Mapping UI:** Customize the mapping between hand gestures and keyboard keystrokes.
- **Real-Time Control:** Seamlessly control your games with muscle gestures.
- **Modular Design:** Easy to set up and integrate with your projects.

## Setup

Follow these steps to get started with NeuroPlayground:

1. **Download the Repository:**
   - Visit the GitHub repo at: [https://github.com/CIumsy/Neuroplayground](https://github.com/CIumsy/Neuroplayground)
   - Download the ZIP file and extract it to your preferred directory.

2. **Install Dependencies:**
   - Ensure you have Python installed on your system.
   - Install any required libraries using pip. For example:
     ```bash
     pip install -r requirements.txt
     ```
     *(If a requirements file is provided; otherwise, check the documentation for necessary libraries.)*

3. **Connect Your EMG Device:**
   - Connect your EMG sensor to your computer as instructed by your hardware manual.

## Usage

1. **Start the Gesture Mapping UI:**
   - Open a terminal.
   - Navigate to the project directory.
   - Run the following command:
     ```bash
     python connect.py
     ```
   - A user interface will appear where you can map your hand gestures to specific keyboard keys.

2. **Launch the Game Control Script:**
   - Open another terminal in the same directory.
   - Run:
     ```bash
     python neuroplayground.py
     ```
   - Click the **Start** button on the UI and enjoy controlling your game with your gestures!

## How It Works

- **EMG Data Acquisition:**  
  The system captures 6-channel EMG data, which represents muscle activity in real time.

- **Signal Processing:**  
  The raw data is processed and analyzed to detect specific hand gestures.

- **Gesture-to-Key Mapping:**  
  The UI (launched via `connect.py`) allows you to assign specific keystrokes to detected gestures.

- **Game Interaction:**  
  Once the mapping is complete, `neuroplayground.py` listens for gesture events and sends the corresponding keystrokes to your laptop, controlling the game.

## Troubleshooting

- **No EMG Data Received:**  
  Ensure your EMG device is properly connected and configured according to the manufacturer's instructions.

- **UI Not Responding:**  
  Double-check that you have installed all the required Python libraries. Also, ensure your system's audio and display drivers are up to date.

- **Unexpected Behavior in Game:**  
  Review your gesture-to-key mapping in the UI. Incorrect mappings may lead to unexpected keystrokes.

## Contributing

Contributions are welcome! If you’d like to contribute to NeuroPlayground, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [MIT License](LICENSE).

---

Enjoy exploring new ways to interact with your games using your muscle gestures! If you encounter any issues or have suggestions, feel free to create an issue on the GitHub repository.

Happy Gaming!
