import os
from app import app, db
from app.models import User
from app.ai_assistant import AI_Assistant


with app.app_context():
    users = User.query.all()
    for user in users:
        print(f'ID: {user.id} ,Usemrame: {user.username} ,email : {user.email}')


if __name__ == "__main__":
    ai_assistant = AI_Assistant()
    #print(gemini_api_key)
    concepts = ["Variables", "Loops", "Functions"]
    language = "Python"
    flashcards = ai_assistant.generate_flashcards(concepts, language)
    print(flashcards)
