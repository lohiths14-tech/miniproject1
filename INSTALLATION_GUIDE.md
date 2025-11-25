# AI-Powered Grading System - Complete Installation Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- MongoDB 4.0 or higher
- Modern web browser (Chrome, Firefox, Safari)
- Git (optional)

### Installation Steps

1. **Extract the project files** to your desired directory
2. **Install MongoDB** if not already installed:
   - Download from: https://www.mongodb.com/try/download/community
   - Start MongoDB service: `mongod --dbpath /path/to/data/db`

3. **Run the setup script**:
   ```bash
   python setup.py
   ```

4. **Configure environment variables** in `.env` file:
   ```bash
   # Required: Update these values
   MONGODB_URI=mongodb://localhost:27017/grading_system
   SECRET_KEY=your_secure_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   
   # Optional: For email notifications
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   
   # Optional: For AI-powered grading
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Start the application**:
   ```bash
   python app.py
   ```

6. **Access the system**:
   - Open browser to: http://localhost:5000
   - Use sample accounts or create new ones

## 📋 Features Overview

### ✅ Core Features Implemented

#### 🔐 Authentication System
- Student/Lecturer registration and login
- Password strength validation
- JWT-based session management
- Password reset functionality
- Role-based access control

#### 🤖 AI Grading Engine
- Automated code evaluation
- Test case execution and validation
- AI-powered code quality assessment
- Performance metrics (execution time, memory usage)
- Multi-language support (Python, Java, C++, C, JavaScript)
- Detailed feedback generation

#### 🛡️ Plagiarism Detection (>91% threshold)
- Advanced similarity detection algorithms
- TF-IDF vectorization analysis
- Sequence similarity comparison
- Structural code analysis
- Code normalization and fingerprinting
- Configurable threshold (default: 91%)

#### 📧 Email Notification System
- Welcome emails for new users
- Assignment publication notifications
- Submission confirmation emails
- Password reset emails
- Asynchronous email delivery

#### 👨‍🎓 Student Dashboard
- Assignment list with status indicators
- Progress tracking and analytics
- Recent submissions history
- Upcoming deadlines
- Performance statistics
- Responsive design

#### 👨‍🏫 Lecturer Dashboard
- Assignment creation and management
- Student submission monitoring
- Performance analytics and reports
- Plagiarism detection reports
- Leaderboard and rankings
- Bulk operations

#### 💻 Code Editor
- Syntax highlighting
- Real-time compilation
- Test case execution
- Multiple programming languages
- Code submission system
- Error handling and debugging

#### 📊 Performance Analytics
- Student performance tracking
- Assignment difficulty analysis
- Submission statistics
- Score distribution
- Plagiarism reports
- Export functionality

### 🛠️ Technical Architecture

#### Backend (Python Flask)
```
app.py                 # Main application entry point
config.py             # Configuration management
models/               # Database models
├── __init__.py       # User, Assignment, Submission models
routes/               # API endpoints
├── auth.py          # Authentication routes
├── student.py       # Student-specific routes
├── lecturer.py      # Lecturer-specific routes
├── assignments.py   # Assignment management
└── submissions.py   # Submission handling
services/             # Business logic
├── ai_grading_service.py      # AI evaluation engine
├── plagiarism_service.py      # Plagiarism detection
├── code_execution_service.py  # Code compilation/execution
└── email_service.py           # Email notifications
utils/                # Utility functions
└── helpers.py        # Common helper functions
```

#### Frontend (HTML/CSS/JavaScript)
```
templates/            # Jinja2 templates
├── base.html        # Base template
├── index.html       # Landing page
├── auth/            # Authentication pages
├── student/         # Student dashboard
└── lecturer/        # Lecturer dashboard
static/              # Static assets
├── css/style.css    # Custom styling
├── js/app.js        # Main JavaScript
└── images/          # Image assets
```

#### Database (MongoDB)
- **users**: Student and lecturer accounts
- **assignments**: Programming assignments and test cases
- **submissions**: Code submissions and grading results

## 🎯 Sample Accounts

After running setup.py, these accounts are available:

### Lecturer Account
- **Email**: lecturer@example.com
- **Password**: password123
- **Features**: Create assignments, view submissions, analytics

### Student Account
- **Email**: student@example.com
- **Password**: password123
- **Features**: Submit assignments, view grades, track progress

## 🔧 Configuration Options

### Email Configuration (Optional)
For email notifications, configure SMTP settings in `.env`:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password  # Use app password for Gmail
```

### OpenAI Configuration (Optional)
For enhanced AI grading, add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

### Plagiarism Threshold
Adjust detection sensitivity in `config.py`:
```python
PLAGIARISM_THRESHOLD = 0.91  # 91% similarity threshold
```

## 🧪 Testing the System

### 1. Create Assignments (Lecturer)
1. Login as lecturer
2. Navigate to Assignment Manager
3. Create new assignment with test cases
4. Publish to students

### 2. Submit Code (Student)
1. Login as student
2. View available assignments
3. Open code editor
4. Write and test solution
5. Submit for grading

### 3. Review Results
- Students: View grades and feedback
- Lecturers: Monitor submissions and analytics

## 🚀 Deployment Considerations

### Production Setup
1. **Use production WSGI server** (Gunicorn, uWSGI)
2. **Configure reverse proxy** (Nginx, Apache)
3. **Set up SSL/TLS certificates**
4. **Use production MongoDB instance**
5. **Configure proper logging**
6. **Set secure environment variables**

### Security Recommendations
- Change default secret keys
- Use strong passwords
- Enable MongoDB authentication
- Implement rate limiting
- Regular security updates

## 🛠️ Troubleshooting

### Common Issues

#### MongoDB Connection Error
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

#### Port 5000 Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process or change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### Package Installation Errors
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Debug Mode
Enable debug mode in `.env`:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/forgot-password` - Password reset request

### Student Endpoints
- `GET /api/student/dashboard` - Dashboard data
- `GET /api/assignments/{id}` - Assignment details
- `POST /api/submissions/submit` - Submit assignment

### Lecturer Endpoints
- `GET /api/lecturer/dashboard` - Lecturer dashboard
- `POST /api/assignments/` - Create assignment
- `GET /api/assignments/{id}/submissions` - View submissions

### Code Execution
- `POST /api/submissions/compile` - Compile code
- `POST /api/submissions/run` - Execute code

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For technical support or questions:
1. Check this README
2. Review error logs
3. Verify MongoDB connection
4. Check environment configuration

---

**🎉 Congratulations! Your AI Grading System is ready to use!**

Visit http://localhost:5000 to get started.