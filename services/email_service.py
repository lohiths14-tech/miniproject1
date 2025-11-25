from flask import current_app
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        current_app.mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            sender=current_app.config['MAIL_USERNAME']
        )
        
        msg.html = template
        
        # Send email asynchronously
        thread = Thread(target=send_async_email, args=(current_app._get_current_object(), msg))
        thread.start()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_welcome_email(email, username, role):
    subject = "Welcome to AI Grading System"
    
    template = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Welcome to AI Grading System!</h2>
            
            <p>Hello <strong>{username}</strong>,</p>
            
            <p>Your account has been successfully created as a <strong>{role.title()}</strong>.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">What's Next?</h3>
                <ul>
                    {'<li>Browse assignments and start coding</li><li>Submit your solutions and get instant AI feedback</li><li>Track your progress and performance</li>' if role == 'student' else '<li>Create and manage assignments</li><li>Monitor student submissions and progress</li><li>Access detailed analytics and reports</li>'}
                </ul>
            </div>
            
            <p>You can access your dashboard at: <a href="http://localhost:5000">http://localhost:5000</a></p>
            
            <p>If you have any questions, feel free to contact our support team.</p>
            
            <p>Best regards,<br>AI Grading System Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated email. Please do not reply to this message.
            </p>
        </body>
    </html>
    """
    
    return send_email(subject, email, template)

def send_password_reset_email(email, username, reset_token):
    subject = "Password Reset - AI Grading System"
    
    reset_url = f"http://localhost:5000/reset-password?token={reset_token}"
    
    template = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Password Reset Request</h2>
            
            <p>Hello <strong>{username}</strong>,</p>
            
            <p>We received a request to reset your password for your AI Grading System account.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p>To reset your password, click the button below:</p>
                <a href="{reset_url}" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 10px 0;">Reset Password</a>
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{reset_url}</p>
            
            <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            
            <p>This reset link will expire in 24 hours for security reasons.</p>
            
            <p>Best regards,<br>AI Grading System Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated email. Please do not reply to this message.
            </p>
        </body>
    </html>
    """
    
    return send_email(subject, email, template)

def send_assignment_notification(email, username, assignment_title, deadline):
    subject = f"New Assignment: {assignment_title}"
    
    template = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">New Assignment Available</h2>
            
            <p>Hello <strong>{username}</strong>,</p>
            
            <p>A new assignment has been published and is ready for submission:</p>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="color: #2c3e50; margin-top: 0;">{assignment_title}</h3>
                <p><strong>Deadline:</strong> {deadline.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <p>Don't wait until the last minute! Start working on your solution early to ensure you have enough time for testing and refinement.</p>
            
            <a href="http://localhost:5000/student-dashboard" style="display: inline-block; background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 10px 0;">View Assignment</a>
            
            <p>Good luck with your submission!</p>
            
            <p>Best regards,<br>AI Grading System Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated email. Please do not reply to this message.
            </p>
        </body>
    </html>
    """
    
    return send_email(subject, email, template)

def send_submission_confirmation(email, username, assignment_title, score=None):
    subject = f"Submission Received: {assignment_title}"
    
    score_section = ""
    if score is not None:
        score_section = f"""
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #28a745;">
            <h4 style="color: #155724; margin-top: 0;">Your Score: {score}%</h4>
            <p style="color: #155724; margin-bottom: 0;">Great job! Your solution has been automatically graded.</p>
        </div>
        """
    
    template = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Submission Confirmed</h2>
            
            <p>Hello <strong>{username}</strong>,</p>
            
            <p>Your submission for <strong>{assignment_title}</strong> has been successfully received and processed.</p>
            
            {score_section}
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h4 style="color: #2c3e50; margin-top: 0;">What happens next?</h4>
                <ul>
                    <li>Your code has been automatically graded by our AI system</li>
                    <li>Plagiarism detection has been performed</li>
                    <li>Detailed feedback is available in your dashboard</li>
                </ul>
            </div>
            
            <a href="http://localhost:5000/student-dashboard" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 10px 0;">View Results</a>
            
            <p>Keep up the excellent work!</p>
            
            <p>Best regards,<br>AI Grading System Team</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated email. Please do not reply to this message.
            </p>
        </body>
    </html>
    """
    
    return send_email(subject, email, template)