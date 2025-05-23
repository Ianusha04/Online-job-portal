-- Database Schema for Simplified Online Job Portal

-- Create Database
CREATE DATABASE IF NOT EXISTS job_portal;
USE job_portal;

-- Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    user_type ENUM('seeker', 'employer', 'admin') NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company Table
CREATE TABLE companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    industry VARCHAR(50),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Job Seeker Profile Table
CREATE TABLE seeker_profiles (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    skills TEXT,
    experience TEXT,
    education TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Job Listings Table
CREATE TABLE jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    salary VARCHAR(50),
    location VARCHAR(100),
    job_type ENUM('full-time', 'part-time', 'contract', 'internship') NOT NULL,
    posting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- Job Applications Table
CREATE TABLE applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    profile_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('applied', 'under_review', 'rejected', 'shortlisted', 'selected') DEFAULT 'applied',
    cover_letter TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES seeker_profiles(profile_id) ON DELETE CASCADE
);

-- Insert sample data for users
INSERT INTO users (username, password, email, user_type) VALUES
('rajesh123', 'password123', 'rajesh@example.com', 'seeker'),
('priya87', 'secure456', 'priya@example.com', 'seeker'),
('amit_hr', 'company789', 'amit@tcs.com', 'employer'),
('neha_rec', 'infosys123', 'neha@infosys.com', 'employer'),
('admin', 'admin123', 'admin@jobportal.com', 'admin');

-- Insert sample data for companies
INSERT INTO companies (user_id, company_name, location, industry, description) VALUES
(3, 'TCS', 'Mumbai, India', 'IT Services', 'Tata Consultancy Services is an Indian multinational information technology services and consulting company.'),
(4, 'Infosys', 'Bangalore, India', 'IT Services', 'Infosys is a global leader in next-generation digital services and consulting.');

-- Insert sample data for seeker profiles
INSERT INTO seeker_profiles (user_id, first_name, last_name, phone, skills, experience, education) VALUES
(1, 'Rajesh', 'Kumar', '9876543210', 'Python, Java, SQL, HTML, CSS', '2 years as Junior Developer at XYZ Corp', 'B.Tech in Computer Science from Delhi University'),
(2, 'Priya', 'Sharma', '8765432109', 'JavaScript, React, Node.js, MongoDB', '3 years as Frontend Developer at ABC Tech', 'MCA from Pune University');

-- Insert sample data for jobs
INSERT INTO jobs (company_id, title, description, salary, location, job_type) VALUES
(1, 'Python Developer', 'We are looking for a Python developer to join our team. Should have experience with Django and Flask.', '6-10 LPA', 'Mumbai, India', 'full-time'),
(1, 'Database Administrator', 'Looking for experienced DBA with knowledge of MySQL and MongoDB.', '8-12 LPA', 'Mumbai, India', 'full-time'),
(2, 'Frontend Developer', 'Need a frontend developer with expertise in React.js and modern JavaScript.', '5-9 LPA', 'Bangalore, India', 'full-time'),
(2, 'Software Testing Intern', 'Opportunity for freshers to learn software testing.', '3-4 LPA', 'Pune, India', 'internship');

-- Insert sample data for applications
INSERT INTO applications (job_id, profile_id, status, cover_letter) VALUES
(3, 1, 'applied', 'I am excited to apply for this position as I have relevant experience in frontend development.'),
(1, 2, 'shortlisted', 'With my Python expertise, I believe I would be a great fit for your team.'),
(4, 1, 'under_review', 'I am eager to start my career in software testing and looking forward to learning with your organization.');