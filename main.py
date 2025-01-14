from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel
from enum import Enum
from openai import OpenAI
import random

app = Flask(__name__)

# List of categories: 

categories = [
    'Animals',
    'Fruits',
    'Vegetables',
    'Colors',
    'Numbers',
    'Body Parts',
    'Dealing with Time, Dates, etc.',
    'Common Phrases',
    'Greetings',
    'Weather',
    'Directions',
    'Shopping',
    'Food',
    'Travel',
    'Health',
    'Emergencies',
    'Work',
    'School',
    'Family',
    'Relationships',
    'Sports',
    'Entertainment',
    'Technology',
    'Nature',
    'Hobbies',
    'Music',
    'Art',
    'Literature',
    'History',
    'Geography',
    'Politics',
    'Religion',
    'Science',
    'Math',
    'Language',
    'Culture',
    'Society',
    'Business',
    'Finance',
    'Law',
    'Government',
    'Military']


# Structured output models
class Pair(BaseModel):
    L1: str
    L2: str

class LanguagePairs(BaseModel):
    representative_story: str
    pairs: list[Pair]

# Reading level Enum
class ReadingLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

    def description(self):
        descriptions = {
            "beginner": "Simple, common words suitable for new learners.",
            "intermediate": "Moderately complex words for learners with basic proficiency.",
            "advanced": "Challenging and uncommon words for fluent speakers."
        }
        return descriptions[self.value]

# Initialize OpenAI client
client = OpenAI()

def generate_language_pairs(L1_language: str, L2_language: str, n: int, reading_level: ReadingLevel) -> dict:
    # Prepare OpenAI API call

    selected_categories = random.sample(categories, 8)

    prompt = {
        "role": "system",
        "content": "You are a helpful assistant generating language pairs. Generate n pairs of random words in two different languages. Adjust the complexity of the words based on the reading level provided. You will be given a selection of categories to draw from. You may vary noun, adjective, verb (use infinitive), etc., OR a short phrase (which can use proper conjugations, etc. but always respect reading level. When selecting words, consider how the categories may relate. To help, start by writing a representative story based on the selected categories. You can choose English as your story language, regardless of language choices. Be creative with the story because it will be a source of inspiration for the words."
    }
    user_message = {
        "role": "user",
        "content": (
            f"Generate {n} matching pairs of words in the following languages:\n"
            f"L1: {L1_language}\nL2: {L2_language}\n"
            f"Reading Level: {reading_level.value.capitalize()}\n"
            f"Description: {reading_level.description()}\n"
            f"Categories: {', '.join(selected_categories)}\n"
        )
    }

    # Call OpenAI API
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[prompt, user_message],
        response_format=LanguagePairs
    )

    parsed = response.choices[0].message.parsed.model_dump()
    return {'pairs': parsed["pairs"]}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    try:
        L1_language = data["L1_language"]
        L2_language = data["L2_language"]
        n = int(data["n"])
        reading_level = ReadingLevel[data["reading_level"]]

        result = generate_language_pairs(L1_language, L2_language, n, reading_level)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
