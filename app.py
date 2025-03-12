import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import document_processor as dp

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure upload settings
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from the document
        text = dp.extract_text(filepath)
        
        # Clean up the file after processing
        os.remove(filepath)
        
        return jsonify({'text': text})
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': 'Error processing file'}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        if not data or 'question' not in data or 'context' not in data:
            return jsonify({'error': 'Missing question or context'}), 400
        
        answer = dp.get_answer(data['question'], data['context'])
        return jsonify({'answer': answer})
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': 'Error processing question'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
