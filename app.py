import os
import logging
import boto3  # <--- PHASE 4 CHANGE: Added AWS SDK for S3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# --- 1. SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 2. CONFIGURATION CLASS ---
class Config:
    # --- PHASE 4 CHANGE: Environment Variables for Secrets ---
    # In Phase 3, we used local defaults. In Phase 4, we read strict env vars.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-prod'
    
    # --- PHASE 4 CHANGE: DATABASE URL (PostgreSQL) ---
    # Switched from SQLite ('sqlite:///employees.db') to AWS RDS (Postgres)
    user = os.environ.get('POSTGRES_USER')
    password = os.environ.get('POSTGRES_PASSWORD')
    host = os.environ.get('POSTGRES_HOST')
    port = os.environ.get('POSTGRES_PORT')
    dbname = os.environ.get('POSTGRES_DB')

    # Construct the Postgres connection string
    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- PHASE 4 CHANGE: AWS S3 Configuration ---
    # Replaced local 'UPLOAD_FOLDER' with S3 Bucket configs
    S3_BUCKET = os.environ.get('S3_BUCKET')
    AWS_REGION = os.environ.get('AWS_REGION')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# --- 3. APP INITIALIZATION ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# --- 5. DATABASE MODEL ---
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # --- PHASE 4 CHANGE: New Column 'Role' ---
    # Added role field to capture job position (DevOps/Developer etc)
    role = db.Column(db.String(50))
    
    # --- PHASE 4 CHANGE: S3 URL instead of Filename ---
    # We now store the full S3 URL (https://...) instead of just 'resume.pdf'
    resume_url = db.Column(db.String(255), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Employee {self.name}>'

# --- 🔥 THE FIX: Auto-Create Tables on Startup (Phase 4 Specific) 🔥 ---
# In Phase 3, this ran in __main__. In Phase 4 (Gunicorn), we force it here.
with app.app_context():
    try:
        db.create_all()
        print("✅ Database Table 'employee' checked/created successfully!")
    except Exception as e:
        print(f"⚠️ Database Warning: {e}")

# --- PHASE 4 CHANGE: Initialize AWS S3 Client ---
# We use IAM Roles (attached to EC2), so no hardcoded keys needed here.
try:
    s3_client = boto3.client('s3', region_name=app.config['AWS_REGION'])
except Exception as e:
    logger.error(f"Failed to connect to AWS S3: {e}")

# --- 4. HELPER FUNCTIONS ---
def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- 6. ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['resume']
    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            
            # --- PHASE 4 CHANGE: Upload to S3 ---
            # Replaced 'file.save(local_path)' with 's3_client.upload_fileobj'
            s3_client.upload_fileobj(
                file,
                app.config['S3_BUCKET'],
                filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            # Generate the Public S3 URL
            file_url = f"https://{app.config['S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{filename}"
            logger.info(f"File uploaded to S3: {file_url}")

            # --- PHASE 4 CHANGE: Save Metadata to RDS ---
            new_emp = Employee(name=name, email=email, role=role, resume_url=file_url)
            db.session.add(new_emp)
            db.session.commit()
            
            logger.info(f"Database entry created for: {name}")
            flash('Successfully uploaded to Cloud! ☁️', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            logger.error(f"Error during save: {e}")
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))

    else:
        flash('Invalid file type. Only PDF, PNG, JPG allowed.', 'error')
        return redirect(request.url)

if __name__ == '__main__':
    # --- PHASE 4 CHANGE: Production Server ---
    # This block is only for local testing. In Production, Gunicorn handles this.
    app.run(host='0.0.0.0', port=5000)

@app.route("/health")
def health():
    return {"status": "ok"}, 200