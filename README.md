# Data Assistant (Jarvis) - Voice Interaction System

A voice-controlled assistant to manage Excel databases and respond to user queries via audio.

## Setup

1. Clone the repository:
   - `git clone https://github.com/yagomouro/jarvis.git`
   - `cd jarvis`

2. Install dependencies from `requirements.txt`:
   - `pip install -r requirements.txt`

3. Install FFmpeg (required for handling audio with `pydub`):
   - **Windows**: Download from [FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.
   - **Mac**: Run `brew install ffmpeg`
   - **Linux**: Run `sudo apt install ffmpeg`

4. Install Ollama (required for running the Gemma 2:2B model):
   - Follow the installation steps from the official [Ollama documentation](https://ollama.com/download).

5. Pull the Gemma 2:2B model:
   - Run `ollama pull gemma2:2b` in your terminal.

## Running the Assistant

1. Run the Python script:
   - `python main.py`

2. Use voice commands:
   - To create a new database: Say `"Create a database"`
   - To search for an existing database: Say `"Search for a database"`
   - To exit: Say `"Exit"`

## Notes

- The program will automatically detect `.xlsx` files in the current directory (excluding temporary files).
- Make sure your microphone is working properly as the assistant listens for commands in real time.
