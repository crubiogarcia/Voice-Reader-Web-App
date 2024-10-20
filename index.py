from flask import Flask, render_template, request, jsonify, send_file, session, url_for
from flask_cors import CORS
from flask_babel import Babel, _
import tempfile
import pdfplumber
from gtts import gTTS
import docx
import os

app = Flask(__name__)  # Initialize the Flask app
CORS(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # Set default language
babel = Babel(app)

# Set a secret key for session management
app.secret_key = os.urandom(24)  # Generates a random secret key

# Define the locale selector function
def get_locale():
    # Check if a language is set in the session
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['en', 'es'])

# Initialize Babel with the locale selector
babel.init_app(app, locale_selector=get_locale)

# Set a maximum character limit
MAX_CHAR_LIMIT = 5000

@app.route('/set_language/<lang>', methods=['POST'])
def set_language(lang):
    if lang in ['en', 'es']:
        session['lang'] = lang  # Store selected language in the session
        return {'success': True}, 200  # Return success response
    return {'success': False}, 400  # Return error response if language not valid

@app.route('/')
@app.route('/home')
def home():
    #return render_template('home.html')
    current_language = session.get('lang', 'en')  # Default to 'en'
    return render_template('home.html', current_language=current_language)

@app.route('/about')
def about():
    # Get the current language from the session
    current_language = session.get('lang', 'en')  # Default to 'en'
    
    # Define the audio files for each language
    audio_files = {
        'en': url_for('static', filename='audio/about_en.mp3'),
        'es': url_for('static', filename='audio/about_es.mp3')
    }
    
    # Pass the appropriate audio file URL based on the language
    audio_src = audio_files.get(current_language, audio_files['en'])  # Fallback to English if not found
    
    return render_template('about.html', title='about', audio_src=audio_src, current_language=current_language)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the file from the request
    file = request.files['file']
    
    if file.mimetype not in ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
    return jsonify({'error': _('Invalid file type')}), 400

    # Check if file has an extension and is allowed
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ['pdf', 'txt', 'docx']:
        return jsonify({'error': _('File type not allowed, only .pdf, .txt, or .docx are allowed.')}), 400
    
    # Check file size
    max_size = 10 * 1024 * 1024  # 10MB
    if file.content_length > max_size:
        return jsonify({'error': _('File too large, must be less than 10MB.')}), 400

    # Create a temporary file to save the uploaded document
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        file_path = temp_file.name  # Save the path for processing

    # Extract text from the file
    text = ''
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    if file_extension == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file_extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()      
    elif file_extension == 'docx':
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])

    # Check character count
    if len(text) > MAX_CHAR_LIMIT:
        return jsonify({'error': _('File exceeds the maximum character limit of {} characters.').format(MAX_CHAR_LIMIT)}), 400

    if not text:
        return jsonify({'error': _('No text found in the file.')}), 400
    
    # Determine the language for TTS based on the selected language
    current_language = session.get('lang', 'en')  # Default to 'en'
    tts_lang = 'en' if current_language == 'en' else 'es'  
    
    # Convert text to speech and create a temporary audio file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
        tts = gTTS(text=text, lang=tts_lang)
        tts.save(temp_audio_file.name)  # Save TTS output to the temporary file
        
        # Return the audio file URL
        audio_file_url = f'/audio/{os.path.basename(temp_audio_file.name)}'
        
    # Delete the uploaded file after processing
    os.remove(file_path)
    
    return jsonify({'audio_url': audio_file_url})

@app.route('/audio/<filename>')
def serve_audio(filename):
    try:

        audio_file_path = os.path.join(tempfile.gettempdir(), filename)
        response = send_file(audio_file_path, as_attachment=True, download_name=filename)
        os.remove(audio_file_path)  # Delete the file after serving it
        return response
    
    except FileNotFoundError:
        return jsonify({'error': _('Audio file not found.')}), 404

if __name__ == '__main__':
    app.run(debug=True)
