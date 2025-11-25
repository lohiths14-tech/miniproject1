// Main JavaScript file for AI Grading System

// Global variables
let currentUser = null;
let authToken = null;

// Initialize the application
$(document).ready(function() {
    initializeApp();
    checkAuthentication();
    setupEventListeners();
});

// Initialize application
function initializeApp() {
    // Load user data from localStorage
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
        currentUser = JSON.parse(storedUser);
        authToken = storedToken;
        updateNavigation();
    }
    
    // Setup AJAX defaults
    $.ajaxSetup({
        beforeSend: function(xhr) {
            if (authToken) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + authToken);
            }
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                handleUnauthorized();
            }
        }
    });
}

// Check authentication status
function checkAuthentication() {
    // Temporarily disable auth checks to prevent redirect loops
    return;
    
    const protectedPages = ['/student-dashboard', '/lecturer-dashboard', '/code-editor', '/assignment-manager'];
    const currentPath = window.location.pathname;
    
    if (protectedPages.includes(currentPath) && !authToken) {
        window.location.href = '/login';
        return;
    }
    
    if (authToken && (currentPath === '/login' || currentPath === '/signup')) {
        redirectToDashboard();
        return;
    }
}

// Setup global event listeners
function setupEventListeners() {
    // Logout functionality
    $(document).on('click', '#logoutBtn', function(e) {
        e.preventDefault();
        logout();
    });
    
    // Auto-hide alerts
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
    
    // Form validation
    $('form').on('submit', function() {
        return validateForm($(this));
    });
    
    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Update navigation based on user role
function updateNavigation() {
    if (!currentUser) return;
    
    const navbarNav = $('.navbar-nav');
    const userMenu = navbarNav.find('.navbar-nav:last');
    
    // Clear existing user menu
    userMenu.empty();
    
    // Add role-specific navigation
    if (currentUser.role === 'student') {
        navbarNav.first().append(`
            <li class="nav-item">
                <a class="nav-link" href="/student-dashboard">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/code-editor">
                    <i class="fas fa-code"></i> Code Editor
                </a>
            </li>
        `);
    } else if (currentUser.role === 'lecturer') {
        navbarNav.first().append(`
            <li class="nav-item">
                <a class="nav-link" href="/lecturer-dashboard">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/assignment-manager">
                    <i class="fas fa-tasks"></i> Assignments
                </a>
            </li>
        `);
    }
    
    // Add user dropdown
    userMenu.append(`
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user"></i> ${currentUser.username}
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#"><i class="fas fa-user-cog"></i> Profile</a></li>
                <li><a class="dropdown-item" href="#"><i class="fas fa-cog"></i> Settings</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" id="logoutBtn"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
            </ul>
        </li>
    `);
}

// Redirect to appropriate dashboard
function redirectToDashboard() {
    if (currentUser) {
        if (currentUser.role === 'student') {
            window.location.href = '/student-dashboard';
        } else {
            window.location.href = '/lecturer-dashboard';
        }
    }
}

// Handle unauthorized access
function handleUnauthorized() {
    showAlert('Session expired. Please login again.', 'warning');
    logout();
}

// Logout function
function logout() {
    // Make logout API call
    if (authToken) {
        $.ajax({
            url: '/api/auth/logout',
            method: 'POST',
            success: function() {
                console.log('Logged out successfully');
            },
            error: function() {
                console.log('Logout API call failed');
            }
        });
    }
    
    // Clear stored data
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    currentUser = null;
    authToken = null;
    
    // Redirect to home page
    window.location.href = '/';
}

// Show alert messages
function showAlert(message, type = 'info', duration = 5000) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#flash-messages').append(alertHtml);
    
    // Auto-hide after duration
    if (duration > 0) {
        setTimeout(function() {
            $('#flash-messages .alert:last').fadeOut(function() {
                $(this).remove();
            });
        }, duration);
    }
}

// Get alert icon based on type
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Form validation
function validateForm(form) {
    let isValid = true;
    
    // Clear previous validation
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Check required fields
    form.find('[required]').each(function() {
        const input = $(this);
        const value = input.val().trim();
        
        if (!value) {
            showFieldError(input, 'This field is required');
            isValid = false;
        }
    });
    
    // Email validation
    form.find('input[type="email"]').each(function() {
        const input = $(this);
        const email = input.val().trim();
        
        if (email && !isValidEmail(email)) {
            showFieldError(input, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Password validation
    form.find('input[name="password"]').each(function() {
        const input = $(this);
        const password = input.val();
        
        if (password && !isValidPassword(password)) {
            showFieldError(input, 'Password must be at least 8 characters with uppercase, lowercase, and digit');
            isValid = false;
        }
    });
    
    return isValid;
}

// Show field validation error
function showFieldError(input, message) {
    input.addClass('is-invalid');
    input.after(`<div class="invalid-feedback">${message}</div>`);
}

// Email validation
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Password validation
function isValidPassword(password) {
    return password.length >= 8 && 
           /[A-Z]/.test(password) && 
           /[a-z]/.test(password) && 
           /\d/.test(password);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
        const hours = Math.floor(diff / (1000 * 60 * 60));
        if (hours === 0) {
            const minutes = Math.floor(diff / (1000 * 60));
            return minutes <= 1 ? 'Just now' : `${minutes} minutes ago`;
        }
        return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    } else if (days === 1) {
        return 'Yesterday';
    } else if (days < 7) {
        return `${days} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Format time remaining
function formatTimeRemaining(deadline) {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diff = deadlineDate - now;
    
    if (diff <= 0) {
        return 'Overdue';
    }
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) {
        return `${days} days, ${hours} hours`;
    } else if (hours > 0) {
        return `${hours} hours, ${minutes} minutes`;
    } else {
        return `${minutes} minutes`;
    }
}

// Get difficulty badge HTML
function getDifficultyBadge(difficulty) {
    const badges = {
        'easy': '<span class="badge bg-success">Easy</span>',
        'medium': '<span class="badge bg-warning">Medium</span>',
        'hard': '<span class="badge bg-danger">Hard</span>',
        'expert': '<span class="badge bg-dark">Expert</span>'
    };
    return badges[difficulty.toLowerCase()] || '<span class="badge bg-secondary">Unknown</span>';
}

// Get score badge HTML
function getScoreBadge(score) {
    if (score >= 90) {
        return '<span class="badge bg-success">A</span>';
    } else if (score >= 80) {
        return '<span class="badge bg-info">B</span>';
    } else if (score >= 70) {
        return '<span class="badge bg-warning">C</span>';
    } else if (score >= 60) {
        return '<span class="badge bg-orange">D</span>';
    } else {
        return '<span class="badge bg-danger">F</span>';
    }
}

// Get plagiarism status HTML
function getPlagiarismStatus(passed) {
    if (passed) {
        return '<span class="badge bg-success"><i class="fas fa-check"></i> Clear</span>';
    } else {
        return '<span class="badge bg-danger"><i class="fas fa-exclamation-triangle"></i> Detected</span>';
    }
}

// Show loading overlay
function showLoading(container = 'body') {
    const loadingHtml = `
        <div class="loading-overlay d-flex justify-content-center align-items-center position-fixed top-0 start-0 w-100 h-100" style="background: rgba(0,0,0,0.5); z-index: 9999;">
            <div class="text-center text-white">
                <div class="spinner-border mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>Loading...</div>
            </div>
        </div>
    `;
    
    $(container).append(loadingHtml);
}

// Hide loading overlay
function hideLoading() {
    $('.loading-overlay').remove();
}

// API helper functions
const API = {
    get: function(url, success, error) {
        $.ajax({
            url: url,
            method: 'GET',
            success: success,
            error: error || function(xhr) {
                showAlert(xhr.responseJSON?.error || 'Request failed', 'danger');
            }
        });
    },
    
    post: function(url, data, success, error) {
        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: success,
            error: error || function(xhr) {
                showAlert(xhr.responseJSON?.error || 'Request failed', 'danger');
            }
        });
    },
    
    put: function(url, data, success, error) {
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: success,
            error: error || function(xhr) {
                showAlert(xhr.responseJSON?.error || 'Request failed', 'danger');
            }
        });
    },
    
    delete: function(url, success, error) {
        $.ajax({
            url: url,
            method: 'DELETE',
            success: success,
            error: error || function(xhr) {
                showAlert(xhr.responseJSON?.error || 'Request failed', 'danger');
            }
        });
    }
};

// Utility functions
const Utils = {
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showAlert('Copied to clipboard!', 'success', 2000);
        }).catch(function() {
            showAlert('Failed to copy to clipboard', 'danger', 2000);
        });
    }
};

// Export for use in other files
window.App = {
    currentUser,
    authToken,
    showAlert,
    API,
    Utils,
    formatDate,
    formatTimeRemaining,
    getDifficultyBadge,
    getScoreBadge,
    getPlagiarismStatus,
    showLoading,
    hideLoading
};