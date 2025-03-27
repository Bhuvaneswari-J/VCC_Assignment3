from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configure the database URIs
db_path = os.path.join(os.getcwd(), 'combined.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database connection
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Year Model
class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_value = db.Column(db.String(4), nullable=False)

# ExamType Model
class ExamType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Subject Model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    exam_type_id = db.Column(db.Integer, db.ForeignKey('exam_type.id'))

# Keyword Model
class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(80), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

# Question Model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    exam_year_id = db.Column(db.Integer, nullable=False)
    exam_type_id = db.Column(db.Integer, nullable=False)

# Root route
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Monolithic API!'}), 200

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login failed'}), 401
    return jsonify({'message': 'Logged in successfully'}), 200

# Add Year
@app.route('/year', methods=['POST'])
def add_year():
    data = request.get_json()
    new_year = Year(year_value=data['year_value'])
    db.session.add(new_year)
    db.session.commit()
    return jsonify({'message': 'Year added'}), 201

# Add Exam Type
@app.route('/exam-type', methods=['POST'])
def add_exam_type():
    data = request.get_json()
    new_exam_type = ExamType(name=data['name'])
    db.session.add(new_exam_type)
    db.session.commit()
    return jsonify({'message': 'Exam type created'}), 201

# Add Question
@app.route('/question', methods=['POST'])
def add_question():
    data = request.get_json()
    new_question = Question(
        text=data['text'],
        exam_year_id=data['exam_year_id'],
        exam_type_id=data['exam_type_id']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added'}), 201

# Get all Subjects
@app.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': subject.id, 'name': subject.name, 'exam_type_id': subject.exam_type_id} for subject in subjects]), 200

# Get all Keywords
@app.route('/keywords', methods=['GET'])
def get_keywords():
    keywords = Keyword.query.all()
    return jsonify([{'id': keyword.id, 'value': keyword.value, 'subject_id': keyword.subject_id} for keyword in keywords]), 200

# Categorize Question
@app.route('/categorize/<int:question_id>', methods=['GET'])
def categorize_question(question_id):
    question = Question.query.get_or_404(question_id)
    question_text = question.text

    subjects = Subject.query.all()
    keywords = Keyword.query.all()

    categories = []

    for subject in subjects:
        if subject.name.lower() in question_text.lower():
            category_info = {
                'subject': subject.name,
                'keywords': []
            }
            related_keywords = [kw for kw in keywords if kw.subject_id == subject.id]
            for keyword in related_keywords:
                if keyword.value.lower() in question_text.lower():
                    category_info['keywords'].append(keyword.value)
            categories.append(category_info)

    if not categories:
        return jsonify({'message': 'No categories found for this question'}), 404

    return jsonify({
        'question_id': question_id,
        'question_text': question_text,
        'categories': categories
    }), 200

if __name__ == '__main__':
    try:
        # Ensure tables are created within app context
        with app.app_context():
            print(f"Creating database tables in: {db_path}")
            db.create_all()
            print("Database tables created successfully in combined.db")
    except Exception as e:
        print(f"Error creating tables: {e}")

    # Run the Flask application
    app.run(debug=True, host='0.0.0.0')
