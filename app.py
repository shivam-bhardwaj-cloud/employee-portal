import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# --- 1. SETUP LOGGING (DevOps Best Practice) ---
# In Docker/K8s, we read logs from stdout. This sets that up.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 2. CONFIGURATION CLASS ---
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///employees.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit upload to 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# --- 3. APP INITIALIZATION ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- 4. HELPER FUNCTIONS ---
def allowed_file(filename: str) -> bool:
    """Checks if the file has a valid extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- 5. DATABASE MODEL ---
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Employee {self.name}>'

# --- 6. ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # A. Validate Form Data
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['resume']
    name = request.form.get('name')
    email = request.form.get('email')

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    # B. Security Checks
    if file and allowed_file(file.filename):
        try:
            # Secure the filename (Critical for security!)
            filename = secure_filename(file.filename)
            # Add timestamp to filename to prevent overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # C. Save File
            file.save(save_path)
            logger.info(f"File saved: {save_path}")

            # D. Save to DB
            new_emp = Employee(name=name, email=email, resume_filename=unique_filename)
            db.session.add(new_emp)
            db.session.commit()
            
            logger.info(f"Database entry created for: {name}")
            flash('Successfully uploaded! details saved.', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            logger.error(f"Error during save: {e}")
            db.session.rollback()
            flash('Internal Server Error. Please try again.', 'error')
            return redirect(url_for('index'))

    else:
        flash('Invalid file type. Only PDF, PNG, JPG allowed.', 'error')
        return redirect(request.url)

# --- 7. RUNNER ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)