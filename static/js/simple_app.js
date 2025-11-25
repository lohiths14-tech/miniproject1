// Simple JavaScript for AI Grading System (without redirect loops)

// Global variables
let currentUser = null;
let authToken = null;

// Initialize the application
$(document).ready(function() {
    console.log('Simple app initialized');
    setupEventListeners();
    // No authentication checks to prevent redirects
});

// Setup event listeners
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
}

// Logout function
function logout() {
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

// Form validation without redirects
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
    
    return isValid;
}

// Show field validation error
function showFieldError(input, message) {
    input.addClass('is-invalid');
    input.after(`<div class="invalid-feedback">${message}</div>`);
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
    }
};

// Export for use in other files
window.SimpleApp = {
    currentUser,
    authToken,
    showAlert,
    API
};