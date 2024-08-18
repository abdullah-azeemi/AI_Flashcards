import os
from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path="./.env")
gemini_api_key = os.getenv("NEW_GEMINI_KEY")
class AI_Assistant:
    def __init__(self):
        self.gemini_api_key = os.getenv("NEW_GEMINI_KEY")

    def generate_flashcards(self, concepts, language):
        prompt_text = (
            f"Generate flashcards for the following concepts: {', '.join(concepts)} "
            f"in the programming language: {language}. "
            f"Provide concise and clear definitions for each concept. "
            f"Single Liner flashcards. "
            f"You have to generate 6 flashcards every time. "
            f"They should be different every time."
        )

        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            ai_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]

            if ai_response:
                flashcards = self._parse_flashcards(ai_response)
                return flashcards
            else:
                return ["Sorry, I couldn't generate more flashcards."]
        except (requests.exceptions.RequestException, IndexError, KeyError) as e:
            print(f"Error: {e}")
            return ["Sorry, there was a problem generating flashcards."]

    def _parse_flashcards(self, ai_response):
        lines = ai_response.split("\n")
        flashcards = []
        current_flashcard = {}

        for line in lines:
            line = line.strip()

            if line.startswith("**Front:**"):
                current_flashcard["question"] = line.replace("**Front:**", "").strip()

            elif line.startswith("**Back:**"):
                current_flashcard["answer"] = line.replace("**Back:**", "").strip()

            # When both question and answer are available, save the flashcard
            if "question" in current_flashcard and "answer" in current_flashcard:
                flashcards.append(current_flashcard)
                current_flashcard = {}

        return flashcards


if __name__ == "__main__":
    ai_assistant = AI_Assistant()
    print(gemini_api_key)
    concepts = ["Pragma"]
    language = "Python"
    flashcards = ai_assistant.generate_flashcards(concepts, language)
    print(flashcards)