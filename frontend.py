# frontend.py - Flask Frontend for Job Portal

from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'frontend_secret_key'

# API base URL
API_URL = 'http://localhost:5000/api'

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Create static directory if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Create CSS file
with open('static/style.css', 'w') as f:
    f.write('''
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f4f4f4;
    }
    
    .container {
        width: 80%;
        margin: 0 auto;
        padding: 20px;
    }
    
    .navbar {
        background-color: #333;
        color: white;
        padding: 15px 0;
    }
    
    .navbar .container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .navbar ul {
        display: flex;
        list-style: none;
    }
    
    .navbar li {
        margin-left: 20px;
    }
    
    .navbar a {
        color: white;
        text-decoration: none;
    }
    
    .job-card {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        padding: 20px;
    }
    
    .job-title {
        color: #333;
        margin-top: 0;
    }
    
    .company-name {
        color: #666;
        font-weight: bold;
    }
    
    .job-details {
        margin: 10px 0;
    }
    
    .apply-btn {
        background-color: #4CAF50;
        border: none;
        border-radius: 3px;
        color: white;
        cursor: pointer;
        padding: 10px 15px;
        text-decoration: none;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 5px;
    }
    
    .form-control {
        border: 1px solid #ddd;
        border-radius: 3px;
        font-size: 16px;
        padding: 10px;
        width: 100%;
    }
    
    .btn {
        background-color: #4CAF50;
        border: none;
        border-radius: 3px;
        color: white;
        cursor: pointer;
        font-size: 16px;
        padding: 10px 15px;
    }
    
    .flash {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin-bottom: 20px;
        padding: 10px;
    }
    
    .success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    ''')

# Create HTML templates

# Base template
with open('templates/base.html', 'w') as f:
    f.write('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}Online Job Portal{% endblock %}</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <nav class="navbar">
            <div class="container">
                <h1>Job Portal</h1>
                <ul>
                    <li><a href="{{ url_for('index') }}">Home</a></li>
                    {% if session.get('user_id') %}
                        {% if session.get('user_type') == 'employer' %}
                            <li><a href="{{ url_for('post_job') }}">Post Job</a></li>
                            <li><a href="{{ url_for('manage_jobs') }}">Manage Jobs</a></li>
                        {% elif session.get('user_type') == 'seeker' %}
                            <li><a href="{{ url_for('my_applications') }}">My Applications</a></li>
                        {% endif %}
                        <li><a href="{{ url_for('logout') }}">Logout</a></li>
                    {% else %}
                        <li><a href="{{ url_for('login') }}">Login</a></li>
                        <li><a href="{{ url_for('register') }}">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </nav>
        
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash {{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    ''')

# Home page template
with open('templates/index.html', 'w') as f:
    f.write('''
    {% extends 'base.html' %}
    
    {% block content %}
        <h2>Latest Job Listings</h2>
        
        {% if jobs %}
            {% for job in jobs %}
                <div class="job-card">
                    <h3 class="job-title">{{ job.title }}</h3>
                    <p class="company-name">{{ job.company_name }}</p>
                    <div class="job-details">
                        <p><strong>Location:</strong> {{ job.location }}</p>
                        <p><strong>Type:</strong> {{ job.job_type }}</p>
                        <p><strong>Salary:</strong> {{ job.salary }}</p>
                    </div>
                    <p>{{ job.description[:200] }}{% if job.description|length > 200 %}...{% endif %}</p>
                    <a href="{{ url_for('job_details', job_id=job.job_id) }}" class="apply-btn">View Details</a>
                </div>
            {% endfor %}
        {% else %}
            <p>No job listings available at the moment.</p>
        {% endif %}
    {% endblock %}
    ''')

# Login template
with open('templates/login.html', 'w') as f:
    f.write('''
    {% extends 'base.html' %}
    
    {% block title %}Login - Job Portal{% endblock %}
    
    {% block content %}
        <h2>Login</h2>
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
    {% endblock %}
    ''')

# Register template
with open('templates/register.html', 'w') as f:
    f.write('''
    {% extends 'base.html' %}
    
    {% block title %}Register - Job Portal{% endblock %}
    
    {% block content %}
        <h2>Register</h2>
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            <div class="form-group">
                <label for="user_type">Account Type</label>
                <select id="user_type" name="user_type" class="form-control" required>
                    <option value="seeker">Job Seeker</option>
                    <option value="employer">Employer</option>
                </select>
            </div>
            <div id="seeker_fields">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" class="form-control">
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" class="form-control">
                </div>
            </div>
            <div id="employer_fields" style="display: none;">
                <div class="form-group">
                    <label for="company_name">Company Name</label>
                    <input type="text" id="company_name" name="company_name" class="form-control">
                </div>
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
        
        <script>
            document.getElementById('user_type').addEventListener('change', function() {
                var seekerFields = document.getElementById('seeker_fields');
                var employerFields = document.getElementById('employer_fields');
                
                if (this.value === 'seeker') {
                    seekerFields.style.display = 'block';
                    employerFields.style.display = 'none';
                } else {
                    seekerFields.style.display = 'none';
                    employerFields.style.display = 'block';
                }
            });
        </script>
    {% endblock %}
    ''')

# Job details template
# Routes for the frontend application

@app.route('/')
def index():
    response = requests.get(f'{API_URL}/jobs')
    jobs = response.json() if response.status_code == 200 else []
    return render_template('index.html', jobs=jobs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        response = requests.post(f'{API_URL}/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            session['user_id'] = data['user']['id']
            session['username'] = data['user']['username']
            session['user_type'] = data['user']['user_type']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your credentials.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'email': request.form['email'],
            'user_type': request.form['user_type']
        }
        
        if data['user_type'] == 'seeker':
            data['first_name'] = request.form['first_name']
            data['last_name'] = request.form['last_name']
        elif data['user_type'] == 'employer':
            data['company_name'] = request.form['company_name']
        
        response = requests.post(f'{API_URL}/register', json=data)
        
        if response.status_code == 201:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            error_msg = response.json().get('error', 'Registration failed.')
            flash(error_msg, 'error')
    
    return render_template('register.html')

@app.route('/job/<int:job_id>')
def job_details(job_id):
    response = requests.get(f'{API_URL}/jobs/{job_id}')
    if response.status_code == 200:
        job = response.json()
        return render_template('job_details.html', job=job)
    else:
        flash('Job not found', 'error')
        return redirect(url_for('index'))

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if not session.get('user_id') or session.get('user_type') != 'seeker':
        flash('You must be logged in as a job seeker to apply.', 'error')
        return redirect(url_for('login'))
    
    cover_letter = request.form.get('cover_letter', '')
    
    response = requests.post(f'{API_URL}/applications', json={
        'job_id': job_id,
        'cover_letter': cover_letter
    }, headers={
        'Authorization': f'Bearer {session.get("user_id")}'
    })
    
    if response.status_code == 201:
        flash('Application submitted successfully!', 'success')
    else:
        error_msg = response.json().get('error', 'Failed to submit application.')
        flash(error_msg, 'error')
    
    return redirect(url_for('job_details', job_id=job_id))

@app.route('/my-applications')
def my_applications():
    if not session.get('user_id') or session.get('user_type') != 'seeker':
        flash('You must be logged in as a job seeker to view applications.', 'error')
        return redirect(url_for('login'))
    
    # Add code to get profile_id
    profile_response = requests.get(f'{API_URL}/profile/seeker/{session["user_id"]}')
    if profile_response.status_code != 200:
        flash('Failed to retrieve your profile.', 'error')
        return redirect(url_for('index'))
    
    profile = profile_response.json()
    profile_id = profile['profile_id']
    
    response = requests.get(f'{API_URL}/applications/seeker/{profile_id}', headers={
        'Authorization': f'Bearer {session.get("user_id")}'
    })
    
    applications = response.json() if response.status_code == 200 else []
    
    return render_template('my_applications.html', applications=applications)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if not session.get('user_id') or session.get('user_type') != 'employer':
        flash('You must be logged in as an employer to post jobs.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        job_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'salary': request.form['salary'],
            'location': request.form['location'],
            'job_type': request.form['job_type']
        }
        
        response = requests.post(f'{API_URL}/jobs', json=job_data, headers={
            'Authorization': f'Bearer {session.get("user_id")}'
        })
        
        if response.status_code == 201:
            flash('Job posted successfully!', 'success')
            return redirect(url_for('manage_jobs'))
        else:
            error_msg = response.json().get('error', 'Failed to post job.')
            flash(error_msg, 'error')
    
    return render_template('post_job.html')

@app.route('/manage-jobs')
def manage_jobs():
    if not session.get('user_id') or session.get('user_type') != 'employer':
        flash('You must be logged in as an employer to manage jobs.', 'error')
        return redirect(url_for('login'))
    
    # Get company_id first
    company_response = requests.get(f'{API_URL}/profile/employer/{session["user_id"]}')
    if company_response.status_code != 200:
        flash('Failed to retrieve your company profile.', 'error')
        return redirect(url_for('index'))
    
    company = company_response.json()
    company_id = company['company_id']
    
    response = requests.get(f'{API_URL}/jobs/company/{company_id}', headers={
        'Authorization': f'Bearer {session.get("user_id")}'
    })
    
    jobs = response.json() if response.status_code == 200 else []
    
    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)