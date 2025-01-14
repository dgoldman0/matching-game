from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel
from enum import Enum
from openai import OpenAI
import random

app = Flask(__name__)

# List of categories: 

categories = [
    # Animals
    "Domesticated Pets",
    "Farm Animals",
    "Wild Mammals",
    "Birds",
    "Reptiles & Amphibians",
    "Marine Life",
    "Insects & Arachnids",
    
    # Plants (Fruits, Vegetables, and More)
    "Citrus Fruits",
    "Berries & Stone Fruits",
    "Tropical Fruits",
    "Melons & Gourds",
    "Root Vegetables",
    "Leafy Greens",
    "Cruciferous Vegetables",
    "Legumes & Pulses",
    "Herbs & Spices",
    
    # Colors & Shapes
    "Basic Colors",
    "Extended Color Palette",
    "2D Shapes",
    "3D Shapes",
    
    # Numbers & Mathematics
    "Cardinal Numbers",
    "Ordinal Numbers",
    "Fractions, Decimals & Percentages",
    "Arithmetic",
    "Algebraic Concepts",
    "Geometry & Measurement",
    "Advanced Math Topics",
    
    # Body Parts & Health
    "External Body Parts",
    "Internal Organs",
    "Body Systems",
    "Symptoms & Illnesses",
    "Medical Treatments & Procedures",
    "Nutrition & Wellness",
    
    # Time & Calendars
    "Days of the Week & Months",
    "Seasons & Weather Patterns",
    "Clock Times",
    "Dates & Holidays",
    
    # Common Phrases & Greetings
    "Polite Expressions",
    "Formal Greetings & Farewells",
    "Informal Greetings",
    "Introducing Yourself & Others",
    "Idioms & Slang",
    
    # Weather & Nature
    "Weather Conditions",
    "Severe Weather & Disasters",
    "Natural Landforms",
    "Ecosystems",
    
    # Directions & Navigation
    "Compass Directions",
    "Giving Simple Directions",
    "Location & Position",
    "Using Maps & GPS",
    
    # Shopping & Money
    "Grocery Shopping",
    "Clothing & Accessories",
    "Online Shopping",
    "Payment & Currency",
    "Personal Finance",
    
    # Food & Dining
    "Ingredients & Cooking Methods",
    "Cuisines",
    "Dishes & Meals",
    "Dietary Preferences",
    "Restaurant Etiquette",
    
    # Travel & Transportation
    "Travel Planning & Booking",
    "Transportation Methods",
    "Accommodation",
    "Tourism & Sightseeing",
    "Visas & Border Control",
    
    # Emergencies & Safety
    "Medical Emergencies",
    "Accidents & Injuries",
    "Natural Disasters",
    "Emergency Services",
    "Disaster Preparedness",
    
    # Work & Career
    "Office Environment & Roles",
    "Professional Communication",
    "Job Hunting & Recruitment",
    "Career Paths & Development",
    "Freelancing & Entrepreneurship",
    
    # School & Education
    "School Levels",
    "Academic Subjects",
    "Exams & Homework",
    "Classroom Routines",
    "Higher Education",
    
    # Family & Relationships
    "Immediate Family Members",
    "Extended Family",
    "Romantic Relationships",
    "Friendship & Social Circles",
    "Conflict Resolution",
    
    # Sports & Recreation
    "Team Sports",
    "Individual Sports",
    "Outdoor Activities",
    "Competitive vs. Recreational Sports",
    "Sports Terminology & Equipment",
    
    # Entertainment & Leisure
    "Movies & TV",
    "Music",
    "Video Games",
    "Art & Design",
    "Literature & Reading",
    "Theater & Performance Arts",
    
    # Technology & Science
    "Computers & Software",
    "Internet & Digital Life",
    "Electronics & Gadgets",
    "Artificial Intelligence & Robotics",
    "Basic Sciences",
    "Advanced Sciences",
    
    # Culture, Society & Lifestyle
    "Traditions & Customs",
    "Religious Practices",
    "Social Issues & Ethics",
    "Fashion & Trends",
    "Hobbies & Personal Interests",
    
    # Language & Communication
    "Grammar & Syntax",
    "Vocabulary Building",
    "Pronunciation & Phonetics",
    "Dialect & Regional Varieties",
    "Writing & Composition",
    
    # History & Geography
    "Historical Eras",
    "Major Civilizations & Empires",
    "Key Historical Events",
    "Physical Geography",
    "Political Geography",
    
    # Politics, Law & Government
    "Political Systems & Ideologies",
    "Government Structures",
    "Voting & Elections",
    "Law & Legal Systems",
    "Military & Defense",
    
    # Business & Finance
    "Business Management",
    "Marketing & Advertising",
    "Entrepreneurship & Startups",
    "Personal Finance",
    "Investments & Trading"
]


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
    basic = "basic"
    intermediate = "intermediate"
    proficient = "proficient"
    advanced = "advanced"

    def description(self):
        descriptions = {
            "beginner": "For learners starting from scratch, focusing on basic greetings, essential vocabulary, and simple, structured phrases for everyday situations. Emphasis on listening and speaking.",
            "basic": "Building on foundational skills with simple grammar structures, practical vocabulary, and short texts or dialogues. Ideal for those gaining confidence in basic communication.",
            "intermediate": "Strengthening understanding of grammar with more complex verb conjugations and sentence structures. Expanding conversational skills and comprehension of intermediate-level texts.",
            "proficient": "Focusing on advanced vocabulary, nuanced grammar, and specialized topics. Developing fluency in expressing ideas clearly and confidently in diverse scenarios.",
            "advanced": "Challenging for near-native fluency, exploring idiomatic expressions, formal writing styles, and stylistic nuances. Designed for professionals, academics, or deep cultural immersion."
        }
        return descriptions[self.value]

# Initialize OpenAI client
client = OpenAI()

def generate_language_pairs(L1_language: str, L2_language: str, n: int, reading_level: ReadingLevel) -> dict:
    # Prepare OpenAI API call

    selected_categories = random.sample(categories, 8)

    prompt = {
        "role": "system",
        "content": "You are a helpful assistant generating words, phrases, and/or sentence pairs. Generate n pairs of random words (or phrases) in two different languages. Adjust the complexity of the words based on the reading level provided. You will be given a selection of categories to draw from. You may vary noun, adjective, verb (use infinitive), etc., OR a short phrase (which can use proper conjugations, etc. but always respect reading level. When selecting words, consider how the categories may relate. To help, start by writing a representative story based on the selected categories. Write the story in language 2. Be creative with the story because it will be a source of inspiration for the words."
    }
    user_message = {
        "role": "user",
        "content": (
            f"L1: {L1_language}\nL2: {L2_language}\n"
            f"Reading Level: {reading_level.value.capitalize()}\n"
            f"Description: {reading_level.description()}\n"
            f"Categories: {', '.join(selected_categories)}\n"
            f"Write a representative story and then generate {n} matching pairs, aligning with the requirements above:\n"
        )
    }

    # Call OpenAI API
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-11-20",
        messages=[prompt, user_message],
        response_format=LanguagePairs
    )

    parsed = response.choices[0].message.parsed.model_dump()
    return parsed

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
