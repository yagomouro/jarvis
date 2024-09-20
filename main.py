from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import os
import re
import json
import platform
import pathlib
import time
import ollama
import pandas as pd
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


class LLM():
    def __init__(self) -> None:
        self.llm_model = 'gemma2:2b'

    def clean_code_block(self, response_text):
        pattern = r"```(?:\w+)?(.*?)```"

        match = re.search(pattern, response_text, re.DOTALL)

        if match:
            return match.group(1).strip()

        return response_text.strip()

    def get_response(self, user_question):
        prompt = f"""
        You are an intelligent assistant receiving transcriptions from audio, and your response will be converted back into audio.

        - Provide a concise, clear response to ensure efficiency and optimal response time **maximum of 70 tokens**.
        - Your answer should be **free from special characters** (such as punctuation marks like `,`, `.`, `:`, etc.) or emojis, as they can sound unnatural when spoken aloud.
        - Focus on delivering a **smart and relevant answer** that addresses the user's question in a way that sounds natural when spoken.
        - Keep the tone simple and conversational, avoiding overly complex phrasing.

        Here is the user question: {user_question}
        """

        response = ollama.generate(model=self.llm_model,
                                   prompt=prompt)

        response_text = response['response']

        return response_text

    def get_database_information(self, user_question, data):
        prompt = f"""
            You are an intelligent assistant receiving transcriptions from audio and data in CSV format. Your responses will be converted back into audio, so they must be clear and natural to listen to.

            - Provide a concise and clear response to ensure efficiency and optimal response time.
            - Your answer should be free from special characters (such as punctuation marks like commas, periods, colons, etc.) and emojis, as these can sound unnatural when spoken aloud.
            - Focus on delivering a smart and relevant answer that addresses the user's question based on the provided CSV data in a way that sounds natural when spoken.
            - Maintain a simple and conversational tone, avoiding complex phrasing and jargon.


            Here is the json data:
            {data}

            Here is the user question:
            {user_question}

            The relevant data for your response is in the CSV file provided. Use this data to formulate your answer.
        """

        response = ollama.generate(model=self.llm_model,
                                   prompt=prompt)

        response_text = response['response']

        return response_text

    def get_options(self, user_question):
        files = [file for file in os.listdir() if file.endswith('.xlsx')
                 and not file.startswith('~$')]

        prompt = f"""
            You are an intelligent assistant managing a virtual assistant's menu system. The user is interacting with this system via voice, and their input needs to be processed to determine the appropriate menu option. Based on the user's question or request, provide a JSON response indicating the selected menu option and any relevant details for that option.

            ## Analyze the user's input and determine which menu option they want to access.

            ## The JSON response should include two fields:
                - 'option': the action the user wants to take in the following options:
                    - create_database: If the user wants to create a new database.
                    - search_database: If the user wants to get an existing database, according to the file_list: {files}
                    - gpt_response: If the user want to know anything else (like normal GPT response)

                - 'details': any additional information provided by the user that may be relevant for that option (e.g., file path, data information).

            ## If the option is 'gpt_response' or 'create_database', pass the entire user question in the 'details' field.

            ## If the option is 'search_database' pass the filename in the 'details' field. If file_list is null, there are no files in the directory, so return the 'create_database' option.

            ## If the user's request is unclear, return {{option: 'error', details: ''}}.


            Here is the user's question: {user_question}
        """

        response = ollama.generate(model=self.llm_model,
                                   prompt=prompt)

        cleaned_response = self.clean_code_block(response['response'])

        response_content = json.loads(cleaned_response)

        return response_content

    def create_database(self, user_question):
        prompt = f"""
            You are an intelligent assistant that generates structured CSV data based on user input. The user will provide specific details about the data they want to include in the CSV file. Your task is to create a **valid CSV structure** with headers and rows according to the user's instructions.

            Follow these steps:
            1. **Analyze the user's input** and identify the columns (headers) and the data that should be included. If not identified, create them.
            2. **Create CSV data** where each row represents a record, and each column represents an attribute.
            3. Return **only the CSV data** in plain text format, with no explanations, comments, or extra formatting like code blocks.
            4. Ensure there is a header row, and the data is properly separated by commas, with each row on a new line (`\\n`). The output should be immediately usable as a CSV file.

            Here is the user's input: {user_question}
        """

        response = ollama.generate(model=self.llm_model,
                                   prompt=prompt)

        cleaned_response = self.clean_code_block(response['response'])

        return cleaned_response

    def search_database(self, user_question, files):
        prompt = f"""
        You are an intelligent assistant that helps users select a file from a list of Excel files. The user will specify the file they want to select, and you will return a JSON object with the filename. Your task is:

        1. **Analyze the user's input** to determine which file they have chosen.
        2. **Ensure that the chosen file is one of the files in the provided list.**
        3. **Return the file name** in the following JSON format: `{{"filename": "selected_file.xlsx"}}` and nothing else. Do not return any code or explanations, just the JSON object.
        4. If the user's choice doesn't match any file in the list, return `{{"error": "Invalid file selection"}}` in the same JSON format.
        5. Do not include any other text, code, or comments. Only return the JSON.

        Here is the list of available files: {files}

        Here is the user's input: {user_question}
        """

        response = ollama.generate(model=self.llm_model,
                                   prompt=prompt)

        cleaned_response = self.clean_code_block(response['response'])

        response_content = json.loads(cleaned_response)

        return response_content


audio_processor = AudioProcessor()
llm = LLM()


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
