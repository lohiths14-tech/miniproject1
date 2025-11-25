// ========================================
// AI Grading System - Premium UI JavaScript
// Dark Mode, Animations, Accessibility
// ========================================

class PremiumUI {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.setupThemeToggle();
        this.setupAnimations();
        this.setupAccessibility();
        this.setupToasts();
        this.setupLoadingStates();
    }

    // ========================================
    // Dark Mode Functionality
    // ========================================

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const icon = this.theme === 'dark' ? '☀️' : '🌙';
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) toggle.innerHTML = icon;
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
        this.showToast('Theme changed to ' + this.theme + ' mode', 'success');
    }

    setupThemeToggle() {
        // Create theme toggle button if it doesn't exist
        if (!document.querySelector('.theme-toggle')) {
            const toggle = document.createElement('button');
            toggle.className = 'theme-toggle';
            toggle.setAttribute('aria-label', 'Toggle dark mode');
            toggle.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
            toggle.onclick = () => this.toggleTheme();
            document.body.appendChild(toggle);
        }
    }

    // ========================================
    // Animation System
    // ========================================

    setupAnimations() {
        // Fade in elements on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all cards and dashboard elements
        document.querySelectorAll('.card, .dashboard-card').forEach(el => {
            observer.observe(el);
        });

        // Add hover effects to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                ripple.style.cssText = `
          position: absolute;
          width: 20px;
          height: 20px;
          background: rgba(255,255,255,0.5);
          border-radius: 50%;
          transform: translate(-50%, -50%);
          left: ${x}px;
          top: ${y}px;
          animation: ripple 0.6s ease-out;
          pointer-events: none;
        `;

                this.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    // ========================================
    // Toast Notifications
    // ========================================

    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 24px;">${icons[type]}</span>
        <div>
          <strong style="display: block; margin-bottom: 4px;">
            ${type.charAt(0).toUpperCase() + type.slice(1)}
          </strong>
          <span>${message}</span>
        </div>
        <button onclick="this.parentElement.parentElement.remove()"
                style="margin-left: auto; background: none; border: none; cursor: pointer; font-size: 20px;">
          ×
        </button>
      </div>
    `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // ========================================
    // Loading States
    // ========================================

    setupLoadingStates() {
        // Add loading spinner to async buttons
        document.querySelectorAll('[data-loading]').forEach(btn => {
            btn.addEventListener('click', function () {
                if (this.classList.contains('loading')) return;

                this.classList.add('loading');
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner"></span> Loading...';

                // Simulate async operation
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    }

    // ========================================
    // Accessibility Features
    // ========================================

    setupAccessibility() {
        // Add skip to content link
        if (!document.querySelector('.skip-to-content')) {
            const skip = document.createElement('a');
            skip.href = '#main-content';
            skip.className = 'skip-to-content';
            skip.textContent = 'Skip to main content';
            document.body.insertBefore(skip, document.body.firstChild);
        }

        // Add ARIA labels to interactive elements
        document.querySelectorAll('button:not([aria-label])').forEach(btn => {
            if (!btn.getAttribute('aria-label') && btn.textContent) {
                btn.setAttribute('aria-label', btn.textContent.trim());
            }
        });

        // Keyboard navigation for cards
        document.querySelectorAll('.card').forEach(card => {
            if (!card.hasAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
            }
        });

        // Announce page changes to screen readers
        this.setupLiveRegion();
    }

    setupLiveRegion() {
        if (!document.querySelector('[role="status"]')) {
            const liveRegion = document.createElement('div');
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.className = 'sr-only';
            liveRegion.id = 'live-region';
            document.body.appendChild(liveRegion);
        }
    }

    announce(message) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => liveRegion.textContent = '', 1000);
        }
    }

    // ========================================
    // Progress Indicators
    // ========================================

    updateProgress(selector, percentage) {
        const progressBar = document.querySelector(selector);
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
        }
    }

    // ========================================
    // Achievement Unlock Animation
    // ========================================

    unlockAchievement(achievementName, icon, description) {
        const achievement = document.createElement('div');
        achievement.className = 'toast achievement-unlock success';
        achievement.innerHTML = `
      <div style="text-align: center;">
        <div style="font-size: 48px; margin-bottom: 8px;">${icon}</div>
        <strong style="display: block; font-size: 18px; margin-bottom: 4px;">
          Achievement Unlocked!
        </strong>
        <div style="font-weight: 600; color: var(--warning-color);">
          ${achievementName}
        </div>
        <small>${description}</small>
      </div>
    `;

        document.body.appendChild(achievement);
        this.announce(`Achievement unlocked: ${achievementName}`);

        setTimeout(() => achievement.remove(), 5000);
    }

    // ========================================
    // Smooth Scroll
    // ========================================

    smoothScrollTo(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
}

// ========================================
// Initialize Premium UI
// ========================================

const premiumUI = new PremiumUI();

// Expose global functions
window.showToast = (msg, type, duration) => premiumUI.showToast(msg, type, duration);
window.unlockAchievement = (name, icon, desc) => premiumUI.unlockAchievement(name, icon, desc);
window.updateProgress = (selector, pct) => premiumUI.updateProgress(selector, pct);

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes ripple {
    from {
      width: 0;
      height: 0;
      opacity: 1;
    }
    to {
      width: 300px;
      height: 300px;
      opacity: 0;
    }
  }

  @keyframes fadeOut {
    to {
      opacity: 0;
      transform: translateY(-20px);
    }
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
`;
document.head.appendChild(style);

// Log initialization
console.log('✨ Premium UI Loaded - Version 2.0');
console.log('🎨 Dark mode available - Click the toggle in the top right');
console.log('♿ Accessibility features enabled');
console.log('🚀 Smooth animations active');
