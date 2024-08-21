from flask import Flask, request, jsonify
from services.image_processing import process_image_for_3d
import os
import json
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/process-image', methods=['POST'])
def process_image_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Process the image and get results
            elements = process_image_for_3d(file_path)
            
            # Convert the elements list to JSON string while preserving order
            json_output = json.dumps(elements, indent=4)
            
            # Return a Response object to avoid altering the JSON structure
            return Response(json_output, mimetype='application/json')
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            # Optionally remove the original uploaded file
            # os.remove(file_path)
            pass
    else:
        return jsonify({"error": "Invalid file type"}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



if __name__ == '__main__':
    print("Starting server...")
    port = os.getenv("PORT") 
    host = os.getenv("HOST")
    app.run(debug=True,host=str(host), port=int(port))
