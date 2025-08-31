#!/usr/bin/env python3
"""
Web interface for MarkItDown PDF conversion
Provides a simple web UI for uploading and converting PDFs
"""

import os
import sys
import logging
import tempfile
import traceback
from pathlib import Path

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/markitdown/src'))

from flask import Flask, request, render_template, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from markitdown import MarkItDown
from markitdown._stream_info import StreamInfo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = '/app/input'
app.config['OUTPUT_FOLDER'] = './output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize MarkItDown
markitdown = MarkItDown()

ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 
    'txt', 'md', 'html', 'htm', 'epub', 'csv', 'zip'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'markitdown-web',
        'version': '1.0.0'
    })

@app.route('/convert', methods=['POST'])
def convert_file():
    """Convert uploaded file to markdown"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing file: {filename}")
        
        # Convert file using MarkItDown
        result = markitdown.convert(filepath)
        
        # Save result to output folder
        output_filename = f"{Path(filename).stem}.md"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
        
        # Return result
        return jsonify({
            'success': True,
            'filename': filename,
            'output_filename': output_filename,
            'text_length': len(result.markdown),
            'preview': result.markdown[:500] + '...' if len(result.markdown) > 500 else result.markdown,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        logger.error(f"Error converting file: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download converted markdown file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            abort(404)
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/files')
def list_files():
    """List available files in input and output folders"""
    try:
        input_files = []
        output_files = []
        
        # List input files
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file)):
                input_files.append({
                    'name': file,
                    'size': os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], file))
                })
        
        # List output files
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], file)):
                output_files.append({
                    'name': file,
                    'size': os.path.getsize(os.path.join(app.config['OUTPUT_FOLDER'], file)),
                    'download_url': f'/download/{file}'
                })
        
        return jsonify({
            'input_files': input_files,
            'output_files': output_files
        })
    
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8100))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting MarkItDown web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)


