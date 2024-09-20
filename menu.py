import io
import os
import platform
import pathlib
import time
import pandas as pd
from audio import AudioProcessor
from llm import LLM


llm = LLM()

audio_processor = AudioProcessor()


class Menu:
    def __init__(self) -> None:
        ...

    def error(self):
        text = 'Sorry I could not understand you. Can you repeat your question, please?'
        audio_processor.get_audio(text, 'en')

    def restart(self):
        text = 'How can I help you?'
        audio_processor.get_audio(text, 'en')

    def hello(self):
        text = 'Hello! I am Jarvis, your Data Assistant. How can I help you?'
        audio_processor.get_audio(text, 'en')

    def confirmation(self):
        text = 'Do you confirm?'
        audio_processor.get_audio(text, 'en')

    def create_file(self, details):
        csv = llm.create_database(details)

        csv_data = io.StringIO(csv)

        df = pd.read_csv(csv_data)

        filename = 'database.xlsx'

        path = pathlib.Path(__file__).parent.resolve()
        file_path = f"{path}/{filename}"

        if os.path.exists(file_path):
            os.remove(file_path)

        df.to_excel(file_path, index=False)

        json_data = df.to_json(orient='records', index=False)

        print("Excel generated!")
        print("Opening file...")

        os_platform = platform.system()

        if os_platform == "Windows":
            cmd = f"start excel {file_path}"
        elif os_platform == "Linux":
            if "WSLENV" in os.environ:
                cmd = f"wslview {file_path}"
            else:
                cmd = f"gnome-open {file_path}"
        elif os_platform == "Darwin":  # MacOS
            cmd = f"open -a Microsoft Excel {file_path}"

        os.system(cmd)

        time.sleep(10)

        while True:
            text = 'What do you want to know about the generated database?'
            audio_processor.get_audio(text, 'en')

            question = audio_processor.get_transcript_audio()

            if not question:
                self.error()
                continue

            if 'exit' in question:
                text = 'Ok, lets back to the menu!'
                audio_processor.get_audio(text, 'en')
                break
            else:
                response = llm.get_database_information(question, json_data)
                audio_processor.get_audio(response, 'en')

    def search_database(self, filename):
        if not filename:
            self.error()
            return

        csv = pd.read_excel(filename).to_json(orient='records', index=False)

        while True:
            text = 'What do you want to know about the database?'
            audio_processor.get_audio(text, 'en')

            question = audio_processor.get_transcript_audio()

            if not question:
                self.error()
                continue

            if 'exit' in question:
                break
            else:
                response = llm.get_database_information(question, csv)
                audio_processor.get_audio(response, 'en')

    def options(self, text):
        response = llm.get_options(text)

        option = response.get('option')
        details = response.get('details')

        if option == 'create_database':
            self.create_file(details)
        elif option == 'search_database':
            self.search_database(details)
        elif option == 'gpt_response':
            response = llm.get_response(details)
            audio_processor.get_audio(response, 'en')
        elif option == 'exit':
            speech_text = 'Ok! If you want something else, I will be here!'
            audio_processor.get_audio(speech_text, 'en')
            return False
        elif option == 'error':
            self.error()
        else:
            self.error()

        return True
