from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import speech_recognition as sr


class AudioProcessor:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def get_transcript_audio(self, language='en-US') -> str | None:
        try:
            with sr.Microphone() as source:
                print('\n')
                print("Listening...")

                self.recognizer.pause_threshold = 3
                audio_data = self.recognizer.listen(source)

                text = self.recognizer.recognize_google(
                    audio_data, language=language).lower()

                print('\n')
                print(text)
                print('--------------------------------------------------------')
                print('\n')

                return text
        except Exception as e:
            print(f"Error: {e}")

            return None

    def get_audio(self, text, language) -> bytes:
        print(text)

        tts = gTTS(text, lang=language)
        audio_data = io.BytesIO()

        tts.write_to_fp(audio_data)

        audio_data.seek(0)

        audio_bytes = audio_data.read()

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

        play(audio)


audio_processor = AudioProcessor()
