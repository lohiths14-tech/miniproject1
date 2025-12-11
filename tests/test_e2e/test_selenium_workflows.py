"""
End-to-End Testing with Selenium
Tests complete user workflows from login to submission
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Base URL for testing
BASE_URL = "http://localhost:5000"

@pytest.fixture
def driver():
    """Setup Chrome driver for E2E tests"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for CI/CD
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

class TestAuthenticationFlow:
    """Test complete authentication workflows"""

    def test_login_flow(self, driver):
        """Test student login flow"""
        driver.get(f"{BASE_URL}/login")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )

        # Fill login form
        email_input.send_keys("student@example.com")
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys("password123")

        # Submit form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # Wait for redirect to dashboard
        wait.until(EC.url_contains("/dashboard"))

        # Verify dashboard loaded
        assert "dashboard" in driver.current_url.lower()
        assert driver.find_element(By.CSS_SELECTOR, ".welcome-message")

    def test_logout_flow(self, driver):
        """Test logout functionality"""
        # Login first
        self.test_login_flow(driver)

        # Find and click logout button
        logout_btn = driver.find_element(By.ID, "logout-btn")
        logout_btn.click()

        # Verify redirected to login
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("/login"))
        assert "login" in driver.current_url

    def test_signup_flow(self, driver):
        """Test new user signup"""
        driver.get(f"{BASE_URL}/signup")

        wait = WebDriverWait(driver, 10)
        name_input = wait.until(EC.presence_of_element_located((By.ID, "name")))

        # Fill signup form
        name_input.send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys(f"test{int(time.time())}@example.com")
        driver.find_element(By.ID, "password").send_keys("SecurePass123!")
        driver.find_element(By.ID, "confirm_password").send_keys("SecurePass123!")

        # Select role
        role_select = driver.find_element(By.ID, "role")
        role_select.send_keys("Student")

        # Submit
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify success
        wait.until(lambda d: "dashboard" in d.current_url or "login" in d.current_url)

class TestCodeSubmissionFlow:
    """Test complete code submission workflow"""

    def login_as_student(self, driver):
        """Helper to login"""
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys("student@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard"))

    def test_submit_code(self, driver):
        """Test submitting code for grading"""
        self.login_as_student(driver)

        # Navigate to code editor
        driver.get(f"{BASE_URL}/code-editor")

        wait = WebDriverWait(driver, 10)
        code_editor = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".code-editor textarea"))
        )

        # Write code
        test_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
        code_editor.clear()
        code_editor.send_keys(test_code)

        # Select language
        language_select = driver.find_element(By.ID, "language")
        language_select.send_keys("Python")

        # Submit
        submit_btn = driver.find_element(By.ID, "submit-code-btn")
        submit_btn.click()

        # Wait for results
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".grading-results"))
        )

        # Verify score displayed
        score_element = driver.find_element(By.CSS_SELECTOR, ".score-value")
        assert score_element.text  # Score should be present

    def test_submit_invalid_code(self, driver):
        """Test submitting invalid code (syntax error)"""
        self.login_as_student(driver)
        driver.get(f"{BASE_URL}/code-editor")
        wait = WebDriverWait(driver, 10)
        code_editor = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".code-editor textarea")))

        # Submit syntax error
        code_editor.clear()
        code_editor.send_keys("def syntax_error(:")
        driver.find_element(By.ID, "language").send_keys("Python")
        driver.find_element(By.ID, "submit-code-btn").click()

        # Verify error message
        error_msg = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message")))
        assert error_msg.is_displayed()


    def test_view_submission_history(self, driver):
        """Test viewing submission history"""
        self.login_as_student(driver)

        # Navigate to submissions
        driver.get(f"{BASE_URL}/submissions")

        wait = WebDriverWait(driver, 10)
        submissions_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".submissions-table"))
        )

        # Verify table has data
        rows = driver.find_elements(By.CSS_SELECTOR, ".submissions-table tbody tr")
        assert len(rows) > 0  # Should have at least one submission

class TestGamificationFlow:
    """Test gamification features"""

    def login_as_student(self, driver):
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys("student@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard"))

    def test_view_achievements(self, driver):
        """Test viewing achievements"""
        self.login_as_student(driver)

        driver.get(f"{BASE_URL}/gamification")

        wait = WebDriverWait(driver, 10)
        achievements_section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".achievements-grid"))
        )

        # Verify achievements displayed
        badges = driver.find_elements(By.CSS_SELECTOR, ".achievement-badge")
        assert len(badges) > 0

    def test_view_leaderboard(self, driver):
        """Test viewing leaderboard"""
        self.login_as_student(driver)

        driver.get(f"{BASE_URL}/leaderboard")

        wait = WebDriverWait(driver, 10)
        leaderboard = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".leaderboard-list"))
        )

        # Verify leaderboard entries
        entries = driver.find_elements(By.CSS_SELECTOR, ".leaderboard-item")
        assert len(entries) > 0

        # Verify rank is displayed
        rank = driver.find_element(By.CSS_SELECTOR, ".leaderboard-item .rank")
        assert rank.text

class TestLecturerFlow:
    """Test lecturer workflows"""

    def login_as_lecturer(self, driver):
        driver.get(f"{BASE_URL}/login")
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys("lecturer@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard"))

    def test_create_assignment(self, driver):
        """Test creating a new assignment"""
        self.login_as_lecturer(driver)

        driver.get(f"{BASE_URL}/create-assignment")

        wait = WebDriverWait(driver, 10)
        title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))

        # Fill assignment form
        title_input.send_keys("Test Assignment")
        driver.find_element(By.ID, "description").send_keys("Test description")
        driver.find_element(By.ID, "deadline").send_keys("2025-12-31")

        # Submit
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify success
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".success-message"))
        )

    def test_view_plagiarism_report(self, driver):
        """Test viewing plagiarism dashboard"""
        self.login_as_lecturer(driver)

        driver.get(f"{BASE_URL}/plagiarism-dashboard")

        wait = WebDriverWait(driver, 10)
        dashboard = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".plagiarism-dashboard"))
        )

        # Verify dashboard elements
        assert driver.find_element(By.CSS_SELECTOR, ".similarity-heatmap")

class TestResponsiveness:
    """Test responsive design"""

    def test_mobile_view(self, driver):
        """Test mobile viewport"""
        driver.set_window_size(375, 667)  # iPhone SE size

        driver.get(BASE_URL)

        # Verify mobile menu exists
        mobile_menu = driver.find_element(By.CSS_SELECTOR, ".mobile-menu-toggle")
        assert mobile_menu.is_displayed()

    def test_tablet_view(self, driver):
        """Test tablet viewport"""
        driver.set_window_size(768, 1024)  # iPad size

        driver.get(BASE_URL)

        # Verify layout adapts
        assert driver.find_element(By.CSS_SELECTOR, ".container")

    def test_desktop_view(self, driver):
        """Test desktop viewport"""
        driver.set_window_size(1920, 1080)

        driver.get(BASE_URL)

        # Verify full layout
        assert driver.find_element(By.CSS_SELECTOR, ".sidebar")

    def test_dark_mode_toggle(self, driver):
        """Test dark mode toggle functionality"""
        driver.get(BASE_URL)

        # Find toggle button
        toggle_btn = driver.find_element(By.ID, "theme-toggle")
        html = driver.find_element(By.TAG_NAME, "html")

        # Initial state (should be light or saved)
        initial_theme = html.get_attribute("data-theme") or "light"

        # Click toggle
        toggle_btn.click()

        # Verify theme changed
        expected_theme = "dark" if initial_theme == "light" else "light"
        assert html.get_attribute("data-theme") == expected_theme

        # Verify persistence (reload page)
        driver.refresh()
        html = driver.find_element(By.TAG_NAME, "html")
        assert html.get_attribute("data-theme") == expected_theme


class TestAccessibility:
    """Test accessibility features"""

    def test_keyboard_navigation(self, driver):
        """Test keyboard-only navigation"""
        driver.get(f"{BASE_URL}/login")

        # Tab through form
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)  # Focus email
        body.send_keys(Keys.TAB)  # Focus password
        body.send_keys(Keys.TAB)  # Focus submit button

        # Verify focus indicators
        active_element = driver.switch_to.active_element
        assert active_element.tag_name == "button"

    def test_aria_labels(self, driver):
        """Test ARIA labels presence"""
        driver.get(BASE_URL)

        # Check for ARIA labels on interactive elements
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for button in buttons:
            # Should have either aria-label or text content
            assert button.get_attribute("aria-label") or button.text

@pytest.mark.e2e
class TestCompleteUserJourney:
    """Test complete user journey from signup to submission"""

    def test_student_complete_journey(self, driver):
        """Test complete student workflow"""
        # 1. Signup
        driver.get(f"{BASE_URL}/signup")
        wait = WebDriverWait(driver, 10)

        unique_email = f"student{int(time.time())}@example.com"
        wait.until(EC.presence_of_element_located((By.ID, "name"))).send_keys("Test Student")
        driver.find_element(By.ID, "email").send_keys(unique_email)
        driver.find_element(By.ID, "password").send_keys("Pass123!")
        driver.find_element(By.ID, "confirm_password").send_keys("Pass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 2. Login
        time.sleep(2)
        driver.get(f"{BASE_URL}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(unique_email)
        driver.find_element(By.ID, "password").send_keys("Pass123!")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 3. View Dashboard
        wait.until(EC.url_contains("/dashboard"))
        assert driver.find_element(By.CSS_SELECTOR, ".dashboard")

        # 4. Submit Code
        driver.get(f"{BASE_URL}/code-editor")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".code-editor textarea")))
        driver.find_element(By.CSS_SELECTOR, ".code-editor textarea").send_keys("print('Hello')")
        driver.find_element(By.ID, "submit-code-btn").click()

        # 5. View Results
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".grading-results")))

        # 6. Check Leaderboard
        driver.get(f"{BASE_URL}/leaderboard")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".leaderboard-list")))

        # 7. Logout
        driver.find_element(By.ID, "logout-btn").click()
        wait.until(EC.url_contains("/login"))

        print("✅ Complete student journey successful!")
