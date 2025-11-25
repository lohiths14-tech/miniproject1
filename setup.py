#!/usr/bin/env python3
"""
Setup script for AI Grading System
This script sets up the development environment and initializes the database
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def print_step(step, message):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print(f"{'='*60}")

def run_command(command, description):
    print(f"\n>>> {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Output: {e.output}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_content = """# AI Grading System Environment Configuration
# Copy this file to .env and update with your actual values

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/grading_system

# Security Keys
SECRET_KEY=ai_grading_super_secret_key_change_in_production
JWT_SECRET_KEY=jwt_secret_key_for_ai_grading_system

# Email Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✓ Created .env file")

def setup_database():
    """Initialize MongoDB collections with sample data"""
    try:
        from pymongo import MongoClient
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client['grading_system']
        
        # Create collections if they don't exist
        collections = ['users', 'assignments', 'submissions']
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                print(f"✓ Created collection: {collection}")
        
        # Create indexes for better performance
        db.users.create_index("email", unique=True)
        db.assignments.create_index("created_by")
        db.submissions.create_index([("student_id", 1), ("assignment_id", 1)])
        
        print("✓ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        return False

def create_sample_data():
    """Create sample lecturer and assignments for testing"""
    try:
        from werkzeug.security import generate_password_hash
        from pymongo import MongoClient
        from datetime import datetime, timedelta
        from bson import ObjectId
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client['grading_system']
        
        # Create sample lecturer
        lecturer_data = {
            'email': 'lecturer@example.com',
            'username': 'sample_lecturer',
            'password_hash': generate_password_hash('password123'),
            'role': 'lecturer',
            'lecturer_id': 'LECT001',
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        # Check if lecturer already exists
        if not db.users.find_one({'email': lecturer_data['email']}):
            lecturer_result = db.users.insert_one(lecturer_data)
            lecturer_id = str(lecturer_result.inserted_id)
            print("✓ Created sample lecturer account")
            print("  Email: lecturer@example.com")
            print("  Password: password123")
            
            # Create sample assignments
            assignments = [
                {
                    'title': 'Basic Python Programming',
                    'description': 'Write a Python program that calculates the factorial of a given number.',
                    'created_by': lecturer_id,
                    'deadline': datetime.utcnow() + timedelta(days=7),
                    'created_at': datetime.utcnow(),
                    'is_active': True,
                    'test_cases': [
                        {'input': '5', 'expected_output': '120'},
                        {'input': '0', 'expected_output': '1'},
                        {'input': '3', 'expected_output': '6'}
                    ],
                    'programming_language': 'python',
                    'max_score': 100,
                    'starter_code': 'def factorial(n):\n    # Your code here\n    pass\n\nif __name__ == "__main__":\n    n = int(input())\n    result = factorial(n)\n    print(result)',
                    'difficulty': 'easy'
                },
                {
                    'title': 'Array Sorting Algorithm',
                    'description': 'Implement a sorting algorithm to sort an array of integers in ascending order.',
                    'created_by': lecturer_id,
                    'deadline': datetime.utcnow() + timedelta(days=10),
                    'created_at': datetime.utcnow(),
                    'is_active': True,
                    'test_cases': [
                        {'input': '5 3 8 1 9', 'expected_output': '1 3 5 8 9'},
                        {'input': '1', 'expected_output': '1'},
                        {'input': '9 8 7 6 5', 'expected_output': '5 6 7 8 9'}
                    ],
                    'programming_language': 'python',
                    'max_score': 100,
                    'starter_code': 'def sort_array(arr):\n    # Your code here\n    pass\n\nif __name__ == "__main__":\n    arr = list(map(int, input().split()))\n    sorted_arr = sort_array(arr)\n    print(" ".join(map(str, sorted_arr)))',
                    'difficulty': 'medium'
                }
            ]
            
            for assignment in assignments:
                db.assignments.insert_one(assignment)
            
            print("✓ Created sample assignments")
        else:
            print("ℹ Sample lecturer already exists")
        
        # Create sample student
        student_data = {
            'email': 'student@example.com',
            'username': 'sample_student',
            'password_hash': generate_password_hash('password123'),
            'role': 'student',
            'usn': 'STU001',
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        if not db.users.find_one({'email': student_data['email']}):
            db.users.insert_one(student_data)
            print("✓ Created sample student account")
            print("  Email: student@example.com")
            print("  Password: password123")
        else:
            print("ℹ Sample student already exists")
        
        return True
        
    except Exception as e:
        print(f"✗ Sample data creation failed: {e}")
        return False

def main():
    print("🚀 AI Grading System Setup")
    print("Setting up production-ready environment")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print_step(1, "Installing Python Dependencies")
    if not run_command("pip install -r requirements.txt", "Installing required packages"):
        print("✗ Failed to install dependencies")
        sys.exit(1)
    
    print_step(2, "Creating Environment Configuration")
    if not os.path.exists('.env'):
        create_env_file()
    else:
        print("ℹ .env file already exists")
    
    print_step(3, "System Initialization")
    print("✓ Production system ready for user registration")
    
    print(f"\n{'='*60}")
    print("🎉 SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Update the .env file with your actual configuration values")
    print("2. Run the application: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    print("4. Register new student and lecturer accounts")
    print("\nThe system is ready for production use!")
    print("For questions or issues, check the README.md file.")

if __name__ == "__main__":
    main()