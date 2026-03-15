/**
 * app.js — Frontend logic: sidebar, date display, delete modal
 */

document.addEventListener('DOMContentLoaded', function () {
    // Current date display
    const dateEl = document.getElementById('currentDate');
    if (dateEl) {
        const now = new Date();
        dateEl.textContent = now.toLocaleDateString('pt-BR', {
            weekday: 'short', day: '2-digit', month: 'short', year: 'numeric'
        });
    }

    // Sidebar toggle (desktop collapse / mobile open)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    // Create overlay for mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    function isMobile() {
        return window.innerWidth <= 768;
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            if (isMobile()) {
                sidebar.classList.toggle('mobile-open');
                overlay.classList.toggle('active');
            } else {
                sidebar.classList.toggle('collapsed');
                if (sidebar.classList.contains('collapsed')) {
                    mainContent.style.marginLeft = 'var(--sidebar-collapsed-width)';
                } else {
                    mainContent.style.marginLeft = 'var(--sidebar-width)';
                }
            }
        });

        overlay.addEventListener('click', function () {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');
        });
    }

    // Set today as default date for new transaction form
    const dateInputs = document.querySelectorAll('input[type="date"]:not([value])');
    dateInputs.forEach(function (input) {
        const today = new Date().toISOString().split('T')[0];
        input.value = today;
    });

    // Auto-hide alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});

// Delete confirmation modal
function confirmDelete(id, description) {
    const modal = document.getElementById('deleteModal');
    const nameEl = document.getElementById('deleteTransactionName');
    const form = document.getElementById('deleteForm');

    if (modal && nameEl && form) {
        nameEl.textContent = description;
        form.action = `/transactions/${id}/delete`;
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}
