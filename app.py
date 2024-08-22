from flask import Flask, request, jsonify,Response
import os
import json
import sqlite3
import bcrypt
from services.image_processing import process_image_for_3d
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

# Sign-up route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    company_name = data.get('company_name')
    company_email = data.get('company_email')
    password = data.get('password')

    if not company_name or not company_email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO companies (company_name, company_email, password) 
            VALUES (?, ?, ?)
        ''', (company_name, company_email, hashed_password))
        conn.commit()
        return jsonify({"message": "Company registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Company email already registered"}), 400
    finally:
        conn.close()

# Sign-in route
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    company_email = data.get('company_email')
    password = data.get('password')

    if not company_email or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies WHERE company_email = ?', (company_email,))
    company = cursor.fetchone()

    if company and bcrypt.checkpw(password.encode('utf-8'), company['password']):
        return jsonify({"message": "Sign-in successful", "company_name": company['company_name'],"company_email": company['company_email']}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
     




# Image processing endpoint (existing logic)
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
    app.run(debug=True, host=str(host), port=int(port))
