import os
from dotenv import load_dotenv
import requests

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

class AI_Assistant:
    def __init__(self):
        self.gemini_api_key = gemini_api_key
        self.full_transcript = []

    def generate_flashcards(self, concepts, language):
        prompt_text = (f"Generate flashcards for the following concepts: {', '.join(concepts)} in the programming language: {language}. "
                       "Provide concise and clear definitions for each concept.")
        self.full_transcript.append({"role": "user", "content": prompt_text})

        response = self.query_gemini(prompt_text)

        if response:
            try:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                if ai_response:
                    return ai_response.split("\n")  # Assuming each flashcard is on a new line
                else:
                    return ["Sorry, I couldn't generate flashcards."]
            except (IndexError, KeyError) as e:
                print(f"Error parsing AI response: {e}")
                return ["Sorry, I couldn't generate flashcards."]
        else:
            return ["Sorry, I couldn't connect to the AI service."]

    def query_gemini(self, text):
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": text}]}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying AI service: {e}")
            return None
