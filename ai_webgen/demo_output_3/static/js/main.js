// Main JavaScript functionality for Flask App
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
            }
            form.classList.add('was-validated');
        });
    });

    // AJAX form handling
    const ajaxForms = document.querySelectorAll('[data-ajax="true"]');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            handleAjaxForm(form);
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search="true"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function() {
            performSearch(input.value, input.dataset.target);
        }, 300));
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states for buttons
    const loadingButtons = document.querySelectorAll('[data-loading="true"]');
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            showLoadingState(button);
        });
    });

    // Confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = button.dataset.confirm;
            if (!confirm(message)) {
                event.preventDefault();
                return false;
            }
        });
    });
});

// Helper Functions
function handleAjaxForm(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('[type="submit"]');
    
    showLoadingState(submitButton);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Success!', 'success');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showAlert(data.error || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error occurred', 'danger');
    })
    .finally(() => {
        hideLoadingState(submitButton);
    });
}

function showLoadingState(button) {
    if (button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        button.dataset.originalText = originalText;
    }
}

function hideLoadingState(button) {
    if (button && button.dataset.originalText) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
        delete button.dataset.originalText;
    }
}

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHtml;
    
    container.insertBefore(alertDiv.firstElementChild, container.firstElementChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function performSearch(query, target) {
    if (!query.trim()) return;
    
    // Basic search implementation
    const items = document.querySelectorAll(target || '[data-searchable]');
    const searchTerm = query.toLowerCase();
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const isVisible = text.includes(searchTerm);
        item.style.display = isVisible ? '' : 'none';
    });
}

// API Helper Functions
const API = {
    get: function(url) {
        return fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json());
    },
    
    post: function(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(response => response.json());
    },
    
    delete: function(url) {
        return fetch(url, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(response => response.json());
    }
};

// Utility functions
const Utils = {
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success');
        }).catch(() => {
            showAlert('Failed to copy to clipboard', 'danger');
        });
    }
};

// Export for use in other scripts
window.FlaskApp = {
    API,
    Utils,
    showAlert,
    showLoadingState,
    hideLoadingState
};
