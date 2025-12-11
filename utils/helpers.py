import hashlib
import re
import secrets
import string
from datetime import datetime, timedelta


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, "Password is valid"


def generate_secure_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_string(text):
    """Generate SHA-256 hash of a string"""
    return hashlib.sha256(text.encode()).hexdigest()


def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except:
            return dt

    if not isinstance(dt, datetime):
        return str(dt)

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 7:
        return dt.strftime("%B %d, %Y")
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"


def calculate_time_remaining(deadline):
    """Calculate time remaining until deadline"""
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except:
            return "Invalid date"

    if not isinstance(deadline, datetime):
        return "Invalid date"

    now = datetime.utcnow()
    diff = deadline - now

    if diff.total_seconds() < 0:
        return "Overdue"

    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60

    if days > 0:
        return f"{days} days, {hours} hours"
    elif hours > 0:
        return f"{hours} hours, {minutes} minutes"
    else:
        return f"{minutes} minutes"


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")
    # Ensure it's not empty
    if not filename:
        filename = "unnamed_file"
    return filename


def truncate_text(text, max_length=100):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def calculate_grade_letter(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def get_difficulty_color(difficulty):
    """Get color code for difficulty level"""
    colors = {
        "easy": "#28a745",  # Green
        "medium": "#ffc107",  # Yellow
        "hard": "#dc3545",  # Red
        "expert": "#6f42c1",  # Purple
    }
    return colors.get(difficulty.lower(), "#6c757d")  # Default gray


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def clean_code_output(output):
    """Clean and format code execution output"""
    if not output:
        return ""

    # Remove ANSI escape sequences
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    output = ansi_escape.sub("", output)

    # Normalize line endings
    output = output.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive empty lines
    lines = output.split("\n")
    cleaned_lines = []
    previous_empty = False

    for line in lines:
        line = line.rstrip()
        if line == "":
            if not previous_empty:
                cleaned_lines.append(line)
            previous_empty = True
        else:
            cleaned_lines.append(line)
            previous_empty = False

    return "\n".join(cleaned_lines).strip()


def validate_test_case(test_case):
    """Validate test case format"""
    if not isinstance(test_case, dict):
        return False, "Test case must be a dictionary"

    if "input" not in test_case:
        return False, "Test case must have 'input' field"

    if "expected_output" not in test_case:
        return False, "Test case must have 'expected_output' field"

    if not isinstance(test_case["input"], str):
        return False, "Test case input must be a string"

    if not isinstance(test_case["expected_output"], str):
        return False, "Test case expected_output must be a string"

    return True, "Valid test case"


def escape_html(text):
    """Escape HTML characters in text"""
    if not text:
        return ""

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }

    return "".join(html_escape_table.get(c, c) for c in text)


def generate_assignment_code(title):
    """Generate a unique assignment code"""
    # Clean title and take first 3 words
    words = re.findall(r"\w+", title.upper())[:3]
    code_prefix = "".join(word[:2] for word in words)

    # Add timestamp-based suffix
    timestamp = int(datetime.utcnow().timestamp())
    code_suffix = str(timestamp)[-4:]

    return f"{code_prefix}{code_suffix}"


def parse_programming_language(filename):
    """Parse programming language from filename extension"""
    extension_map = {
        ".py": "python",
        ".java": "java",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "c",
        ".js": "javascript",
        ".ts": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
    }

    if not filename or "." not in filename:
        return "python"  # Default

    extension = "." + filename.split(".")[-1].lower()
    return extension_map.get(extension, "python")


def get_language_template(language):
    """Get starter code template for a programming language"""
    templates = {
        "python": """# Write your solution here
def main():
    # Your code goes here
    pass

if __name__ == "__main__":
    main()
""",
        "java": """public class Main {
    public static void main(String[] args) {
        // Your code goes here
        
    }
}
""",
        "cpp": """#include <iostream>
using namespace std;

int main() {
    // Your code goes here
    
    return 0;
}
""",
        "c": """#include <stdio.h>

int main() {
    // Your code goes here
    
    return 0;
}
""",
        "javascript": """// Write your solution here
function main() {
    // Your code goes here
    
}

main();
""",
    }

    return templates.get(language, templates["python"])


def calculate_performance_metrics(submissions):
    """Calculate performance metrics from submissions"""
    if not submissions:
        return {
            "total_submissions": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "pass_rate": 0,
            "average_time": 0,
        }

    scores = [s.get("score", 0) for s in submissions]
    times = [s.get("execution_time", 0) for s in submissions]
    passing_scores = [s for s in scores if s >= 60]  # Assuming 60% is passing

    return {
        "total_submissions": len(submissions),
        "average_score": sum(scores) / len(scores),
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "pass_rate": (len(passing_scores) / len(scores)) * 100,
        "average_time": sum(times) / len(times) if times else 0,
    }
