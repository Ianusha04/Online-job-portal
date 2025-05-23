# app.py - Flask Backend for Job Portal

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='manager',  # Change to your MySQL password
        database='job_portal'
    )

# Helper function to convert MySQL results to JSON serializable format
def format_result(cursor):
    columns = [col[0] for col in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    # Convert datetime objects to strings
    for result in results:
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    
    return results

# Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not user or user['password'] != password:  # In a real app, use check_password_hash for security
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = user['user_id']
    session['user_type'] = user['user_type']
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'user_type': user['user_type']
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    user_type = data.get('user_type')
    
    if not username or not password or not email or not user_type:
        return jsonify({'error': 'All fields are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO users (username, password, email, user_type) VALUES (%s, %s, %s, %s)',
                      (username, password, email, user_type))
        conn.commit()
        user_id = cursor.lastrowid
        
        # Create corresponding profile based on user type
        if user_type == 'employer':
            company_name = data.get('company_name', f"{username}'s Company")
            cursor.execute('INSERT INTO companies (user_id, company_name) VALUES (%s, %s)',
                          (user_id, company_name))
        elif user_type == 'seeker':
            first_name = data.get('first_name', username)
            last_name = data.get('last_name', '')
            cursor.execute('INSERT INTO seeker_profiles (user_id, first_name, last_name) VALUES (%s, %s, %s)',
                          (user_id, first_name, last_name))
        
        conn.commit()
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT j.*, c.company_name, c.location as company_location
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.posting_date DESC
        ''')
        
        jobs = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for job in jobs:
            if 'posting_date' in job and isinstance(job['posting_date'], datetime):
                job['posting_date'] = job['posting_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(jobs)
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.json
    user_id = session.get('user_id')
    
    if not user_id or session.get('user_type') != 'employer':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    required_fields = ['title', 'description', 'salary', 'location', 'job_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get company_id for the logged-in employer
        cursor.execute('SELECT company_id FROM companies WHERE user_id = %s', (user_id,))
        company = cursor.fetchone()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        company_id = company[0]
        
        cursor.execute('''
            INSERT INTO jobs (company_id, title, description, salary, location, job_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (company_id, data['title'], data['description'], data['salary'], data['location'], data['job_type']))
        
        conn.commit()
        return jsonify({'message': 'Job created successfully', 'job_id': cursor.lastrowid}), 201
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/applications', methods=['POST'])
def apply_for_job():
    data = request.json
    user_id = session.get('user_id')
    
    if not user_id or session.get('user_type') != 'seeker':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    job_id = data.get('job_id')
    cover_letter = data.get('cover_letter', '')
    
    if not job_id:
        return jsonify({'error': 'Job ID is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get profile_id for the logged-in job seeker
        cursor.execute('SELECT profile_id FROM seeker_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
        
        if not profile:
            return jsonify({'error': 'Job seeker profile not found'}), 404
        
        profile_id = profile[0]
        
        # Check if already applied
        cursor.execute('SELECT * FROM applications WHERE job_id = %s AND profile_id = %s', (job_id, profile_id))
        if cursor.fetchone():
            return jsonify({'error': 'You have already applied for this job'}), 400
        
        cursor.execute('''
            INSERT INTO applications (job_id, profile_id, cover_letter)
            VALUES (%s, %s, %s)
        ''', (job_id, profile_id, cover_letter))
        
        conn.commit()
        return jsonify({'message': 'Application submitted successfully'}), 201
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/profile/<user_type>/<int:user_id>', methods=['GET'])
def get_profile(user_type, user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if user_type == 'seeker':
            cursor.execute('''
                SELECT sp.*, u.email, u.username
                FROM seeker_profiles sp
                JOIN users u ON sp.user_id = u.user_id
                WHERE sp.user_id = %s
            ''', (user_id,))
        elif user_type == 'employer':
            cursor.execute('''
                SELECT c.*, u.email, u.username
                FROM companies c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.user_id = %s
            ''', (user_id,))
        else:
            return jsonify({'error': 'Invalid user type'}), 400
        
        profile = cursor.fetchone()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(profile)
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/applications/employer/<int:company_id>', methods=['GET'])
def get_employer_applications(company_id):
    user_id = session.get('user_id')
    
    if not user_id or session.get('user_type') != 'employer':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if the company belongs to the logged-in employer
        cursor.execute('SELECT * FROM companies WHERE company_id = %s AND user_id = %s', (company_id, user_id))
        if not cursor.fetchone():
            return jsonify({'error': 'You don\'t have access to this company'}), 403
        
        cursor.execute('''
            SELECT a.*, j.title as job_title, j.job_type,
                   CONCAT(sp.first_name, ' ', sp.last_name) as applicant_name,
                   sp.skills, sp.experience, sp.education
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN seeker_profiles sp ON a.profile_id = sp.profile_id
            WHERE j.company_id = %s
            ORDER BY a.application_date DESC
        ''', (company_id,))
        
        applications = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for app in applications:
            if 'application_date' in app and isinstance(app['application_date'], datetime):
                app['application_date'] = app['application_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(applications)
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/applications/seeker/<int:profile_id>', methods=['GET'])
def get_seeker_applications(profile_id):
    user_id = session.get('user_id')
    
    if not user_id or session.get('user_type') != 'seeker':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if the profile belongs to the logged-in seeker
        cursor.execute('SELECT * FROM seeker_profiles WHERE profile_id = %s AND user_id = %s', (profile_id, user_id))
        if not cursor.fetchone():
            return jsonify({'error': 'You don\'t have access to this profile'}), 403
        
        cursor.execute('''
            SELECT a.*, j.title as job_title, j.job_type, j.salary, j.location,
                   c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.profile_id = %s
            ORDER BY a.application_date DESC
        ''', (profile_id,))
        
        applications = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for app in applications:
            if 'application_date' in app and isinstance(app['application_date'], datetime):
                app['application_date'] = app['application_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(applications)
    
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)