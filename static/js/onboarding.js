/**
 * Interactive Onboarding System
 * Uses Intro.js for step-by-step product tours
 */

// Onboarding configuration for different user roles
const onboardingConfig = {
    student: {
        steps: [
            {
                element: '.dashboard-welcome',
                intro: '👋 Welcome to the AI-Powered Grading System! Let\'s take a quick tour.',
                position: 'bottom'
            },
            {
                element: '.assignments-section',
                intro: '📚 Here you\'ll find all your assignments. Click on any assignment to start coding!',
                position: 'right'
            },
            {
                element: '.code-editor-link',
                intro: '💻 Our advanced code editor supports Python, Java, C++, C, and JavaScript with syntax highlighting and real-time execution.',
                position: 'bottom'
            },
            {
                element: '.progress-tracker',
                intro: '📊 Track your progress, scores, and improvement over time with detailed analytics.',
                position: 'left'
            },
            {
                element: '.gamification-section',
                intro: '🏆 Earn points, unlock achievements, and climb the leaderboard as you complete assignments!',
                position: 'top'
            },
            {
                element: '.profile-menu',
                intro: '⚙️ Access your profile, settings, and view your achievements here.',
                position: 'bottom'
            }
        ],
        options: {
            showProgress: true,
            showBullets: true,
            exitOnOverlayClick: false,
            disableInteraction: true,
            nextLabel: 'Next →',
            prevLabel: '← Back',
            doneLabel: 'Get Started! 🚀'
        }
    },

    lecturer: {
        steps: [
            {
                intro: '👨‍🏫 Welcome, Professor! Let\'s explore the lecturer dashboard.',
                position: 'bottom'
            },
            {
                element: '.create-assignment-btn',
                intro: '➕ Create new assignments with custom test cases, deadlines, and grading criteria.',
                position: 'bottom'
            },
            {
                element: '.submissions-panel',
                intro: '📝 Monitor student submissions in real-time. AI automatically grades and provides detailed feedback.',
                position: 'right'
            },
            {
                element: '.plagiarism-dashboard',
                intro: '🛡️ Advanced plagiarism detection with cross-language support. Identify similar code patterns instantly.',
                position: 'left'
            },
            {
                element: '.analytics-section',
                intro: '📊 Comprehensive analytics: score distributions, submission trends, and class performance metrics.',
                position: 'top'
            },
            {
                element: '.leaderboard-view',
                intro: '🏆 View class rankings and top performers to encourage healthy competition.',
                position: 'bottom'
            }
        ],
        options: {
            showProgress: true,
            showBullets: true,
            exitOnOverlayClick: false,
            nextLabel: 'Next →',
            prevLabel: '← Back',
            doneLabel: 'Start Teaching! 🎓'
        }
    }
};

// Initialize onboarding
function initializeOnboarding() {
    // Check if user has completed onboarding
    const userRole = getUserRole();
    const onboardingKey = `onboarding_completed_${userRole}`;

    if (!localStorage.getItem(onboardingKey)) {
        // Show onboarding on first login
        setTimeout(() => {
            startOnboarding(userRole);
        }, 1000); // Delay to ensure DOM is ready
    }
}

// Get user role from session
function getUserRole() {
    // Try to get from session storage first
    const role = sessionStorage.getItem('user_role');
    if (role) return role;

    // Fallback: detect from page URL or elements
    if (window.location.pathname.includes('student')) return 'student';
    if (window.location.pathname.includes('lecturer')) return 'lecturer';

    return 'student'; // Default
}

// Start onboarding tour
function startOnboarding(role = 'student') {
    const config = onboardingConfig[role];
    if (!config) {
        console.error(`No onboarding configuration for role: ${role}`);
        return;
    }

    // Initialize Intro.js
    const intro = introJs();

    // Set steps
    intro.setOptions({
        steps: config.steps,
        ...config.options
    });

    // Event handlers
    intro.oncomplete(() => {
        markOnboardingComplete(role);
        showCelebration();
    });

    intro.onexit(() => {
        // Ask if user wants to skip onboarding
        if (confirm('Would you like to skip the tour? You can restart it anytime from settings.')) {
            markOnboardingComplete(role);
        }
    });

    intro.start();
}

// Mark onboarding as completed
function markOnboardingComplete(role) {
    const onboardingKey = `onboarding_completed_${role}`;
    localStorage.setItem(onboardingKey, 'true');
    localStorage.setItem(`onboarding_completed_date_${role}`, new Date().toISOString());
}

// Show celebration animation on completion
function showCelebration() {
    // Create celebration overlay
    const celebration = document.createElement('div');
    celebration.className = 'onboarding-celebration';
    celebration.innerHTML = `
        <div class="celebration-content">
            <div class="celebration-icon">🎉</div>
            <h2>You're All Set!</h2>
            <p>Start exploring and make the most of your learning journey!</p>
            <button class="btn btn-primary btn-lg" onclick="this.parentElement.parentElement.remove()">
                Let's Go! 🚀
            </button>
        </div>
    `;

    document.body.appendChild(celebration);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        celebration.classList.add('fade-out');
        setTimeout(() => celebration.remove(), 500);
    }, 5000);
}

// Restart onboarding (from settings menu)
function restartOnboarding() {
    const role = getUserRole();
    const onboardingKey = `onboarding_completed_${role}`;
    localStorage.removeItem(onboardingKey);
    startOnboarding(role);
}

// Skip onboarding (for users who don't want the tour)
function skipOnboarding() {
    const role = getUserRole();
    markOnboardingComplete(role);
}

// Check if specific feature needs highlighting
function highlightFeature(featureName) {
    const highlights = {
        'code-editor': {
            element: '.code-editor-link',
            intro: '💡 Try our powerful code editor with AI-powered suggestions!',
            position: 'bottom'
        },
        'gamification': {
            element: '.gamification-section',
            intro: '🎮 New achievement unlocked! Check out the gamification section.',
            position: 'top'
        },
        'plagiarism': {
            element: '.plagiarism-dashboard',
            intro: '🔍 Advanced plagiarism detection is now available!',
            position: 'left'
        }
    };

    const highlight = highlights[featureName];
    if (!highlight) return;

    const intro = introJs();
    intro.setOptions({
        steps: [highlight],
        showProgress: false,
        showBullets: false,
        exitOnOverlayClick: true,
        nextLabel: 'Got it! ✓'
    });
    intro.start();
}

// Progressive disclosure: Show hints for unused features
function showFeatureHints() {
    const hints = [
        {
            element: '.collaboration-feature',
            hint: '💡 Did you know? You can collaborate with classmates in real-time!',
            hintPosition: 'middle-right'
        },
        {
            element: '.progress-tracker',
            hint: '📈 Track your improvement over time with detailed analytics.',
            hintPosition: 'middle-left'
        },
        {
            element: '.achievements-badge',
            hint: '🏆 Unlock more achievements by completing assignments!',
            hintPosition: 'top-middle'
        }
    ];

    introJs().setOptions({
        hints: hints,
        hintButtonLabel: 'Got it!'
    }).showHints();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if Intro.js is loaded
    if (typeof introJs === 'undefined') {
        console.warn('Intro.js library not loaded. Loading from CDN...');
        loadIntroJs(() => {
            initializeOnboarding();
        });
        return;
    }

    initializeOnboarding();

    // Show hints after 30 seconds if user hasn't explored much
    setTimeout(() => {
        const hasExplored = localStorage.getItem('user_has_explored');
        if (!hasExplored) {
            showFeatureHints();
            localStorage.setItem('user_has_explored', 'true');
        }
    }, 30000);
});

// Load Intro.js from CDN if not already loaded
function loadIntroJs(callback) {
    // Load CSS
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://cdnjs.cloudflare.com/ajax/libs/intro.js/7.2.0/introjs.min.css';
    document.head.appendChild(css);

    // Load JS
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/intro.js/7.2.0/intro.min.js';
    script.onload = callback;
    document.head.appendChild(script);
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        startOnboarding,
        restartOnboarding,
        skipOnboarding,
        highlightFeature,
        showFeatureHints
    };
}
