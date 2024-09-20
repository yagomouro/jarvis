from menu import Menu
from audio import AudioProcessor

audio_processor = AudioProcessor()


menu = Menu()

menu.hello()

while True:
    text = audio_processor.get_transcript_audio()

    if not text:
        menu.error()
        continue

    if not menu.options(text):
        break

    menu.restart()
