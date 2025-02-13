// Add animations to buttons with btn-animate class
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn-animate');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
            this.style.transition = 'all 0.2s';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        button.addEventListener('click', function() {
            this.style.transform = 'translateY(1px)';
            setTimeout(() => {
                this.style.transform = 'translateY(0)';
            }, 200);
        });
    });
});

// Add fade-out to flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('[role="alert"]');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease-in-out';
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 3000);
    });
});

// Delete confirmation modal handling
function confirmDelete(type, id, description) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const modalText = document.getElementById('deleteModalText');
    const modalContent = modal.querySelector('.modal-content');
    
    modalText.innerHTML = `Are you sure you want to delete <strong>${description}</strong>?<br>This action cannot be undone.`;
    form.action = `/${type}/${id}/delete`;
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        modalContent.classList.add('show');
    }, 50);
}

function hideDeleteModal() {
    const modal = document.getElementById('deleteModal');
    const modalContent = modal.querySelector('.modal-content');
    modalContent.classList.remove('show');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

// Close modal when clicking outside
document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) {
        hideDeleteModal();
    }
});

function showPaymentModal(loanId, suggestedAmount) {
    const modal = document.getElementById('paymentModal');
    const form = document.getElementById('paymentForm');
    const amountInput = document.getElementById('paymentAmount');
    const notesInput = document.getElementById('paymentNotes');
    const typeSelect = document.getElementById('paymentType');
    
    // Clear any previous form data
    form.reset();

    form.action = `/loan/${loanId}/pay`;
    updateAmountPlaceholder();  // Set initial placeholder based on payment type
    amountInput.min = 0;
    
    // Clear notes
    notesInput.value = '';
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.querySelector('.modal-content').classList.add('show');
        amountInput.focus();
    }, 50);
}

function hidePaymentModal() {
    const modal = document.getElementById('paymentModal');
    modal.querySelector('.modal-content').classList.remove('show');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

function updateAmountPlaceholder() {
    const typeSelect = document.getElementById('paymentType');
    const amountInput = document.getElementById('paymentAmount');
    
    switch(typeSelect.value) {
        case 'PRINCIPAL':
            amountInput.placeholder = 'Enter principal payment amount';
            break;
        case 'INTEREST':
            amountInput.placeholder = 'Enter interest payment amount';
            break;
        case 'PENALTY':
            amountInput.placeholder = 'Enter penalty amount';
            break;
    }
}

async function generateShareLink(loanId) {
    try {
        const response = await fetch(`/loan/${loanId}/share`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        
        // Copy to clipboard
        await navigator.clipboard.writeText(data.share_url);
        
        // Show success message
        const flashContainer = document.querySelector('main');
        const alert = document.createElement('div');
        alert.className = 'bg-green-100 border-green-400 text-green-700 px-4 py-3 rounded relative mb-4';
        alert.setAttribute('role', 'alert');
        alert.innerHTML = 'Share link copied to clipboard!';
        flashContainer.insertBefore(alert, flashContainer.firstChild);
        
        // Remove the alert after 3 seconds
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-in-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
        
    } catch (error) {
        console.error('Error generating share link:', error);
    }
}

// Show/hide sections based on screen size
function handleResponsiveDisplay() {
    const isMobile = window.innerWidth < 1024; // lg breakpoint
    const sections = document.querySelectorAll('.view-section');
    
    if (isMobile) {
        // On mobile, show only the first section initially
        sections.forEach((section, index) => {
            section.classList.toggle('hidden', index !== 0);
        });
    } else {
        // On desktop, show all sections
        sections.forEach(section => {
            section.classList.remove('hidden');
        });
    }
}

// Initialize and add event listeners
document.addEventListener('DOMContentLoaded', function() {
    handleResponsiveDisplay();
    window.addEventListener('resize', handleResponsiveDisplay);
});

function calculateEMI() {
    const principal = parseFloat(document.getElementById('amount').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest_rate').value) || 0;
    const termMonths = parseInt(document.getElementById('term_months').value) || 0;
    
    if (principal > 0 && interestRate > 0 && termMonths > 0) {
        // Principal Component = Loan Amount / Term(Months)
        const principalComponent = principal / termMonths;
        
        // Interest Component = Loan Amount * Interest Rate / 12
        const interestComponent = (principal * interestRate) / 1200; // Divided by 1200 (12 * 100) to convert percentage
        
        // Total Monthly EMI = Principal Component + Interest Component
        const emi = principalComponent + interestComponent;
        
        // Update the form fields
        document.getElementById('monthly_principal').value = principalComponent.toFixed(2);
        document.getElementById('monthly_interest').value = interestComponent.toFixed(2);
        document.getElementById('monthly_emi').value = emi.toFixed(2);
        
        // Add visual feedback
        const emiBreakdown = document.querySelector('.bg-gray-50');
        emiBreakdown.classList.add('animate-pulse');
        setTimeout(() => {
            emiBreakdown.classList.remove('animate-pulse');
        }, 500);
    } else {
        // Clear the fields if input is invalid
        document.getElementById('monthly_principal').value = '';
        document.getElementById('monthly_interest').value = '';
        document.getElementById('monthly_emi').value = '';
    }
}

// Add event listeners for real-time calculation
document.addEventListener('DOMContentLoaded', function() {
    const inputs = ['amount', 'interest_rate', 'term_months'];
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', calculateEMI);
        }
    });
}); 