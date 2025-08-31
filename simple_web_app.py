#!/usr/bin/env python3
"""
Simple web interface for MarkItDown PDF conversion
Uses the advanced PDF OCR converter directly
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/markitdown/src'))

from flask import Flask, request, render_template, jsonify, send_file, abort
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = './input'
app.config['OUTPUT_FOLDER'] = './output'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_markdown(filepath):
    """Convert PDF to markdown using the advanced OCR converter"""
    try:
        # Import the advanced converter
        from markitdown.converters._advanced_optimized_pdf_ocr_converter import AdvancedOptimizedPdfOcrConverter
        from markitdown._stream_info import StreamInfo
        
        # Create converter instance
        converter = AdvancedOptimizedPdfOcrConverter()
        
        # Read file data
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Create stream info
        stream_info = StreamInfo(
            filename=os.path.basename(filepath),
            mimetype="application/pdf",
            extension=".pdf"
        )
        
        # Convert the file
        result = converter.convert(file_data, stream_info)
        
        return result.markdown
        
    except Exception as e:
        logger.error(f"Error converting PDF: {e}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'markitdown-simple-web',
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
            return jsonify({'error': f'File type not allowed. Only PDF files are supported.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing file: {filename}")
        
        # Convert file using advanced OCR converter
        markdown_content = convert_pdf_to_markdown(filepath)
        
        # Save result to output folder
        output_filename = f"{Path(filename).stem}.md"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Return result
        return jsonify({
            'success': True,
            'filename': filename,
            'output_filename': output_filename,
            'text_length': len(markdown_content),
            'preview': markdown_content[:500] + '...' if len(markdown_content) > 500 else markdown_content,
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
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                input_files.append({
                    'name': file,
                    'size': os.path.getsize(file_path)
                })
        
        # List output files
        for file in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], file)
            if os.path.isfile(file_path):
                output_files.append({
                    'name': file,
                    'size': os.path.getsize(file_path),
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
    host = os.environ.get('HOST', '127.0.0.1')

    logger.info(f"Starting MarkItDown simple web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
