import os
from dotenv import load_dotenv
import requests

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")


class AI_Assistant:
    def __init__(self):
        self.gemini_api_key = gemini_api_key

    def generate_flashcards(self, concepts, language):
        prompt_text = (
            f"Generate flashcards for the following concepts: {', '.join(concepts)} "
            f"in the programming language: {language}. "
            f"Provide concise and clear definitions for each concept."
        )

        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            ai_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            if ai_response:
                return ai_response.split("\n")  # Assuming each flashcard is on a new line
            else:
                return ["Sorry, I couldn't generate flashcards."]
        except (requests.exceptions.RequestException, IndexError, KeyError) as e:
            print(f"Error: {e}")
            return ["Sorry, there was a problem generating flashcards."]

