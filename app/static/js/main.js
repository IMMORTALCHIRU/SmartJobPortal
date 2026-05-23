// Smart Job Portal - Main JS

// Auto-dismiss flash messages
document.querySelectorAll('.flash-messages .alert').forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
    }, 5000);
});

// Sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('show');
}
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
}

// Option label selection
document.querySelectorAll('.option-label').forEach(label => {
    label.addEventListener('click', function() {
        const card = this.closest('.question-card');
        if (card) {
            card.querySelectorAll('.option-label').forEach(l => l.classList.remove('selected'));
        }
        this.classList.add('selected');
        const radio = this.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
    });
});

// Password show/hide toggle
document.querySelectorAll('[data-toggle-password]').forEach(btn => {
    btn.addEventListener('click', function() {
        const target = document.querySelector(this.dataset.togglePassword);
        if (!target) return;
        if (target.type === 'password') {
            target.type = 'text';
            this.innerHTML = '<img src="https://img.icons8.com/?size=100&id=vtdMC1xSaMXw&format=png&color=000000" alt="" style="width:18px;height:18px">';
        } else {
            target.type = 'password';
            this.innerHTML = '<img src="https://img.icons8.com/?size=100&id=85130&format=png&color=000000" alt="" style="width:18px;height:18px">';
        }
    });
});

// Skills tag input helper
function initSkillsInput(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const val = this.value.trim();
            if (val && !this.value.split(',').map(s => s.trim()).includes(val)) {
                if (this.value && !this.value.endsWith(',')) this.value += ', ';
            }
        }
    });
}

// Animate numbers (stat counters)
function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent.replace(/\D/g,''));
    if (isNaN(target)) return;
    let current = 0;
    const step = Math.ceil(target / 50);
    const interval = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString() + (el.dataset.suffix || '');
        if (current >= target) clearInterval(interval);
    }, 30);
}

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.querySelectorAll('[data-counter]').forEach(animateCounter);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

document.querySelectorAll('.stats-section').forEach(el => observer.observe(el));
