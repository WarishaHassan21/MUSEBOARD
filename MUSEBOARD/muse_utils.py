import os
import re
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Language mappings
LANGUAGE_NAMES = {
    "en": "English",
    "ur": "Urdu",
    "pa": "Punjabi (پاکستان)",
    "sd": "Sindhi",
    "bal": "Balochi",
    "ps": "Pashto",
    "skr": "Saraiki"
}

def generate_poem(emotion: str, language: str = "en", num_lines: int = 5) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    system_prompt = f"You are a poetic assistant who writes beautiful {num_lines}-line poems in {language_name}."
    user_prompt = f"Write a {num_lines}-line poem in {language_name} inspired by the emotion: {emotion}."

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

def create_poster(poem: str, emotion: str, language: str) -> str:
    width, height = 800, 1000
    image = Image.new("RGB", (width, height), color=(248, 248, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
        title_font = ImageFont.truetype("arialbd.ttf", 34)
    except IOError:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    language_label = LANGUAGE_NAMES.get(language, "English")
    draw.text((50, 40), f"MuseBoard - {emotion.capitalize()} ({language_label})", fill="black", font=title_font)

    y = 150
    for line in poem.split("\n"):
        draw.text((60, y), line.strip(), fill="black", font=font)
        y += 50

    safe_emotion = re.sub(r'\W+', '', emotion)
    filename = f"poster_{safe_emotion}_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join("static", "posters", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    image.save(filepath)
    return filename

def generate_recitation(poem_text, language='en'):
    # Language codes for gTTS
    supported_languages = ['en', 'ur', 'pa', 'sd', 'bal', 'skr', 'ps']

    # Check if the language is supported, if not fallback to Urdu
    if language not in supported_languages:
        language = 'ur'

    try:
        # Initialize gTTS and generate recitation
        tts = gTTS(text=poem_text, lang=language)
        recitation_path = os.path.join('static', 'audio', 'recitation.mp3')
        tts.save(recitation_path)
        return recitation_path
    except ValueError as e:
        print(f"Error generating recitation: {e}")
        return None