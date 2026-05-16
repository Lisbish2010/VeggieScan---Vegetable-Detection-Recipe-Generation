"""
Vegetable Detection & Recipe Generator - Flask Application
Main entry point for the web application.
"""

import os
import sys
import threading
import time

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detector.vegetable_detector import analyze_image
from recipes.recipe_generator import generate_recipes, download_kaggle_dataset, get_dataset_status

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/detect', methods=['POST'])
def detect_vegetables():
    """API endpoint to detect vegetables in an uploaded image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    try:
        image_bytes = file.read()
        if len(image_bytes) == 0:
            return jsonify({'error': 'Empty image file'}), 400

        result, error = analyze_image(image_bytes, app.config['RESULTS_FOLDER'])

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/api/recipes', methods=['POST'])
def get_recipes():
    """API endpoint to generate recipes based on detected vegetables."""
    try:
        data = request.get_json()
        if not data or 'vegetables' not in data:
            return jsonify({'error': 'No vegetables data provided'}), 400

        vegetables = data['vegetables']
        result = generate_recipes(vegetables)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({'error': f'Recipe generation error: {str(e)}'}), 500


@app.route('/api/dataset-status', methods=['GET'])
def dataset_status():
    """API endpoint to check Kaggle dataset download status."""
    status = get_dataset_status()
    return jsonify({
        'success': True,
        'data': status
    })


@app.route('/api/download-kaggle', methods=['POST'])
def trigger_kaggle_download():
    """API endpoint to trigger Kaggle dataset download."""
    status = get_dataset_status()
    if status['loaded'] and status['has_kaggle_data']:
        return jsonify({'success': True, 'message': 'Dataset already loaded', 'data': status})

    # Start download in background
    def do_download():
        download_kaggle_dataset()

    thread = threading.Thread(target=do_download, daemon=True)
    thread.start()

    return jsonify({'success': True, 'message': 'Download started in background'})


@app.route('/results/<path:filename>')
def serve_result(filename):
    """Serve result images."""
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  VEGETABLE DETECTION & RECIPE GENERATOR")
    print("  Starting server on http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
