from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from muse_utils import generate_poem, create_poster, generate_recitation, LANGUAGE_NAMES
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_dev_key')

# Folder where posters and audio are saved
app.config['UPLOAD_FOLDER'] = 'static/posters'


@app.route('/')
def home():
    return redirect(url_for('museboard'))


@app.route('/museboard', methods=['GET', 'POST'])
def museboard():
    if request.method == 'POST':
        emotion = request.form.get('emotion', '').strip().lower()
        language = request.form.get('language', 'en')
        num_lines = int(request.form.get('lines', 5))

        if not emotion:
            return redirect(url_for('museboard'))

        # Generate original poem
        poem_original = generate_poem(emotion, language, num_lines)

        # Generate English translation (if different language)
        poem_translated = generate_poem(emotion, 'en', num_lines) if language != 'en' else poem_original

        # Create poster
        poster_filename = create_poster(poem_original, emotion, language)

        # Generate audio recitation for the specific language
        recitation_path = generate_recitation(poem_original, language)

        # Store in session
        session['poem_original'] = poem_original
        session['poem_translated'] = poem_translated
        session['poster'] = poster_filename
        session['recitation'] = recitation_path
        session['emotion'] = emotion
        session['language'] = language

        return redirect(url_for('poster_generation'))

    return render_template('museboard.html')


@app.route('/poster_generation')
def poster_generation():
    required_keys = ('poem_original', 'poster', 'language', 'emotion')
    if not all(k in session for k in required_keys):
        return redirect(url_for('museboard'))

    poem_original = session['poem_original']
    poem_translated = session.get('poem_translated', poem_original)
    poster_filename = session['poster']
    language = session['language']
    emotion = session['emotion']
    language_name = LANGUAGE_NAMES.get(language, 'English')

    return render_template('poster.html',
                           poem_original=poem_original,
                           poem_translated=poem_translated,
                           poster_filename=poster_filename,
                           language=language,
                           emotion=emotion,
                           language_name=language_name)


@app.route('/music')
def music():
    poem_original = session.get('poem_original')
    recitation = session.get('recitation')

    # Handle missing data safely
    if not poem_original or not recitation or not os.path.exists(recitation):
        return redirect(url_for('museboard'))

    recitation_filename = os.path.basename(recitation)

    return render_template('music.html',
                           poem=poem_original,
                           recitation_file=recitation_filename)


@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    return send_from_directory(os.path.join(app.root_path, 'static', folder), filename)


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('museboard'))


if __name__ == '__main__':
    app.run(debug=True)
