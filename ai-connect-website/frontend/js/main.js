// ===================================
//   Main JavaScript Functionality
// ===================================

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeScrollEffects();
    initializeFormHandlers();
    initializeBlogFunctionality();
    initializeContactPage();
    initializeAnimations();
    initializeTheme();
});

// ===================================
//   Navigation Functions
// ===================================

function initializeNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });
    }

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navToggle?.classList.remove('active');
            navMenu?.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.navbar') && navMenu?.classList.contains('active')) {
            navToggle?.classList.remove('active');
            navMenu?.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Active navigation highlighting
    highlightActiveNav();
}

function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const linkPath = new URL(link.href).pathname;
        
        if (linkPath === currentPath || 
            (currentPath === '/' && linkPath.includes('index.html')) ||
            (currentPath.includes(linkPath.replace('.html', '')) && linkPath !== '/')) {
            link.classList.add('active');
        }
    });
}

// ===================================
//   Scroll Effects
// ===================================

function initializeScrollEffects() {
    // Header scroll effect
    const header = document.querySelector('.header');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            header?.classList.add('header-hidden');
        } else {
            // Scrolling up
            header?.classList.remove('header-hidden');
        }
        
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^=\"#\"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .post-card, .team-member, .value-card').forEach(el => {
        observer.observe(el);
    });
}

// ===================================
//   Form Handlers
// ===================================

function initializeFormHandlers() {
    // Newsletter forms
    document.querySelectorAll('.newsletter-form, .newsletter-form-inline').forEach(form => {
        form.addEventListener('submit', handleNewsletterSubmit);
    });

    // Character counter for textareas
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const counter = textarea.parentElement.querySelector('.char-counter #char-count') || 
                       textarea.parentElement.querySelector('#char-count');
        
        if (counter) {
            textarea.addEventListener('input', function() {
                counter.textContent = this.value.length;
                
                // Visual feedback for approaching limit
                const percentage = (this.value.length / this.maxLength) * 100;
                if (percentage > 80) {
                    counter.style.color = 'var(--warning-color)';
                } else if (percentage > 95) {
                    counter.style.color = 'var(--error-color)';
                } else {
                    counter.style.color = 'var(--text-muted)';
                }
            });
        }
    });

    // Input validation
    document.querySelectorAll('input[required], textarea[required], select[required]').forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('invalid')) {
                validateField(this);
            }
        });
    });
}

function handleNewsletterSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.querySelector('input[type=\"email\"]').value;
    
    if (!isValidEmail(email)) {
        showNotification('Please enter a valid email address.', 'error');
        return;
    }
    
    // Simulate API call
    showLoading(true);
    
    setTimeout(() => {
        showLoading(false);
        showNotification('Thank you for subscribing! You will receive our latest updates.', 'success');
        form.reset();
    }, 1500);
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove existing error styling
    field.classList.remove('invalid');
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }

    // Email validation
    if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address.';
    }

    // Phone validation
    if (field.type === 'tel' && value && !isValidPhone(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid phone number.';
    }

    if (!isValid) {
        field.classList.add('invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = errorMessage;
        field.parentElement.appendChild(errorDiv);
    }

    return isValid;
}

// ===================================
//   Blog Functionality
// ===================================

function initializeBlogFunctionality() {
    if (!document.querySelector('.blog-posts')) return;

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchPosts();
            }, 300);
        });
    }

    // Category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterPosts);
    }
}

function searchPosts() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const posts = document.querySelectorAll('.post-card');
    let visibleCount = 0;

    posts.forEach(post => {
        const title = post.querySelector('.post-title')?.textContent.toLowerCase() || '';
        const excerpt = post.querySelector('.post-excerpt')?.textContent.toLowerCase() || '';
        const category = post.querySelector('.post-category')?.textContent.toLowerCase() || '';
        
        const matches = title.includes(searchTerm) || 
                       excerpt.includes(searchTerm) || 
                       category.includes(searchTerm);
        
        if (matches) {
            post.style.display = 'block';
            visibleCount++;
        } else {
            post.style.display = 'none';
        }
    });

    // Show/hide no results message
    const noResults = document.getElementById('no-results');
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

function filterPosts() {
    const selectedCategory = document.getElementById('category-filter')?.value || 'all';
    const posts = document.querySelectorAll('.post-card');
    let visibleCount = 0;

    posts.forEach(post => {
        const postCategory = post.getAttribute('data-category');
        
        if (selectedCategory === 'all' || postCategory === selectedCategory) {
            post.style.display = 'block';
            visibleCount++;
        } else {
            post.style.display = 'none';
        }
    });

    // Show/hide no results message
    const noResults = document.getElementById('no-results');
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    // Clear search when filtering
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
}

function loadMorePosts() {
    // Simulate loading more posts
    showLoading(true);
    
    setTimeout(() => {
        showLoading(false);
        showNotification('No more posts available at this time.', 'info');
        
        // Hide the load more button
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = 'none';
        }
    }, 1000);
}

// ===================================
//   Contact Page
// ===================================

function initializeContactPage() {
    const contactForm = document.getElementById('contact-form');
    if (!contactForm) return;

    // Character counter for message field
    const messageField = document.getElementById('message');
    const charCount = document.getElementById('char-count');
    
    if (messageField && charCount) {
        messageField.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });
    }

    // Form submission
    contactForm.addEventListener('submit', handleContactSubmit);
}

async function handleContactSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Validate all required fields
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        showNotification('Please fill in all required fields correctly.', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class=\"fas fa-spinner fa-spin\"></i> Sending...';
    submitBtn.disabled = true;
    
    try {
        // Send form data to backend
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                company: formData.get('company'),
                subject: formData.get('subject'),
                message: formData.get('message'),
                newsletter: formData.get('newsletter') === 'on'
            })
        });
        
        if (response.ok) {
            showFormSuccess();
        } else {
            throw new Error('Failed to send message');
        }
    } catch (error) {
        console.error('Contact form error:', error);
        showFormError('There was a problem sending your message. Please try again or contact us directly.');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function showFormSuccess() {
    const form = document.getElementById('contact-form');
    const success = document.getElementById('form-success');
    
    if (form && success) {
        form.style.display = 'none';
        success.style.display = 'block';
    }
}

function showFormError(message) {
    const errorDiv = document.getElementById('form-error');
    const errorMessage = document.getElementById('error-message');
    
    if (errorDiv && errorMessage) {
        errorMessage.textContent = message;
        errorDiv.style.display = 'block';
        
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function resetForm() {
    const form = document.getElementById('contact-form');
    const success = document.getElementById('form-success');
    
    if (form && success) {
        form.style.display = 'block';
        success.style.display = 'none';
        form.reset();
        
        // Clear character counter
        const charCount = document.getElementById('char-count');
        if (charCount) {
            charCount.textContent = '0';
        }
    }
}

function hideError() {
    const errorDiv = document.getElementById('form-error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// ===================================
//   FAQ Functionality
// ===================================

function toggleFaq(button) {
    const faqItem = button.closest('.faq-item');
    const isActive = faqItem.classList.contains('active');
    
    // Close all FAQ items
    document.querySelectorAll('.faq-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Open clicked item if it wasn't already open
    if (!isActive) {
        faqItem.classList.add('active');
    }
}

// ===================================
//   Animation & Effects
// ===================================

function initializeAnimations() {
    // Add CSS classes for animations
    const style = document.createElement('style');
    style.textContent = `
        .fade-in {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in.active {
            opacity: 1;
            transform: translateY(0);
        }
        
        .header-hidden {
            transform: translateY(-100%);
            transition: transform 0.3s ease;
        }
        
        .invalid {
            border-color: var(--error-color) !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
        }
        
        .error-message {
            color: var(--error-color);
            font-size: var(--font-size-sm);
            margin-top: var(--spacing-xs);
        }
    `;
    document.head.appendChild(style);
}

// ===================================
//   Theme Management
// ===================================

function initializeTheme() {
    // Load saved theme preference
    const savedTheme = localStorage.getItem('ai-connect-theme') || 'light';
    applyTheme(savedTheme);
    
    // Theme toggle buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const theme = this.getAttribute('data-theme');
            applyTheme(theme);
            localStorage.setItem('ai-connect-theme', theme);
        });
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update active button
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-theme') === theme);
    });
    
    if (theme === 'dark') {
        document.documentElement.style.setProperty('--bg-primary', '#1e293b');
        document.documentElement.style.setProperty('--bg-secondary', '#0f172a');
        document.documentElement.style.setProperty('--bg-card', '#334155');
        document.documentElement.style.setProperty('--text-primary', '#f8fafc');
        document.documentElement.style.setProperty('--text-secondary', '#cbd5e1');
        document.documentElement.style.setProperty('--border-color', '#475569');
    } else {
        // Reset to light theme variables
        document.documentElement.style.removeProperty('--bg-primary');
        document.documentElement.style.removeProperty('--bg-secondary');
        document.documentElement.style.removeProperty('--bg-card');
        document.documentElement.style.removeProperty('--text-primary');
        document.documentElement.style.removeProperty('--text-secondary');
        document.documentElement.style.removeProperty('--border-color');
    }
}

// ===================================
//   Utility Functions
// ===================================

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class=\"notification-content\">
            <i class=\"fas ${getNotificationIcon(type)}\"></i>
            <span>${message}</span>
            <button class=\"notification-close\" onclick=\"this.parentElement.parentElement.remove()\">
                <i class=\"fas fa-times\"></i>
            </button>
        </div>
    `;
    
    // Add notification styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                padding: var(--spacing-md);
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-lg);
                animation: slideIn 0.3s ease;
                max-width: 400px;
            }
            
            .notification-success {
                background: var(--success-color);
                color: white;
            }
            
            .notification-error {
                background: var(--error-color);
                color: white;
            }
            
            .notification-warning {
                background: var(--warning-color);
                color: white;
            }
            
            .notification-info {
                background: var(--primary-color);
                color: white;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
            }
            
            .notification-close {
                background: none;
                border: none;
                color: inherit;
                cursor: pointer;
                margin-left: auto;
                padding: var(--spacing-xs);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-triangle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

// ===================================
//   Global Event Handlers
// ===================================

// Handle keyboard navigation
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Close mobile menu
        const navMenu = document.getElementById('nav-menu');
        const navToggle = document.getElementById('nav-toggle');
        if (navMenu?.classList.contains('active')) {
            navToggle?.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        // Close chatbot
        const chatbotContainer = document.getElementById('chatbot-container');
        if (chatbotContainer?.classList.contains('active')) {
            chatbotContainer.classList.remove('active');
        }
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    // Close mobile menu on resize to desktop
    if (window.innerWidth > 768) {
        const navMenu = document.getElementById('nav-menu');
        const navToggle = document.getElementById('nav-toggle');
        navMenu?.classList.remove('active');
        navToggle?.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// Export functions for global use
window.toggleFaq = toggleFaq;
window.loadMorePosts = loadMorePosts;
window.resetForm = resetForm;
window.hideError = hideError;
window.filterPosts = filterPosts;
window.searchPosts = searchPosts;