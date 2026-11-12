/* ============================================
   K&G Farms - Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {

    // ---- Auto-dismiss alerts after 5 seconds ----
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ---- Confirm delete actions ----
    const deleteForms = document.querySelectorAll('form[onsubmit]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this record? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ---- Set today's date on empty date inputs ----
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });

    // ---- Auto-calculate sale total ----
    const qtyInput = document.getElementById('qty');
    const priceInput = document.getElementById('price');
    const discInput = document.getElementById('disc');
    const totalDisplay = document.getElementById('totalDisplay');

    if (qtyInput && priceInput && totalDisplay) {
        function updateTotal() {
            const qty = parseFloat(qtyInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const disc = parseFloat(discInput ? discInput.value : 0) || 0;
            const total = (qty * price) - disc;
            totalDisplay.value = 'NGN ' + total.toLocaleString('en-NG', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            });
        }
        qtyInput.addEventListener('input', updateTotal);
        priceInput.addEventListener('input', updateTotal);
        if (discInput) discInput.addEventListener('input', updateTotal);
    }

    // ---- Highlight low stock rows ----
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(function(row) {
        if (row.classList.contains('table-danger')) {
            row.style.borderLeft = '4px solid #d32f2f';
        }
    });

    // ---- Add tooltip to action buttons ----
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    // ---- Print button functionality ----
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }

    // ---- Search/Filter tables (client-side) ----
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('dataTable');
            if (!table) return;
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    // ---- Number formatting for currency inputs ----
    const currencyInputs = document.querySelectorAll('input[data-currency]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const val = parseFloat(this.value);
            if (!isNaN(val)) {
                this.value = val.toFixed(2);
            }
        });
    });

    // ---- Show loading spinner on form submit ----
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving...';
            }
        });
    });

    console.log('K&G Farms Dashboard loaded successfully!');
});
