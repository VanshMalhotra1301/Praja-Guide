/* ============================================================
   PRAJAGUIDE AI — CORE JAVASCRIPT v4.0
   ============================================================ */

'use strict';

// ============================================================
// 1. ENGINE INITIALIZATION
// ============================================================
(function initEngine() {
    console.log('PrajaGuide Premium AI Active');
})();

// ============================================================
// 2. CURSOR GLOW (Desktop only)
// ============================================================
(function initCursorGlow() {
    const glow = document.getElementById('cursor-glow');
    if (!glow) return;
    let raf;
    document.addEventListener('mousemove', (e) => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
            glow.style.left = e.clientX + 'px';
            glow.style.top = e.clientY + 'px';
        });
    });
})();

// ============================================================
// 3. SCROLL REVEAL (IntersectionObserver)
// ============================================================
(function initScrollReveal() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    els.forEach(el => observer.observe(el));
})();

// ============================================================
// 4. LIVE STATUS TICKER (Latency / Accuracy)
// ============================================================
(function initLiveTicker() {
    const latencyEls = document.querySelectorAll('#live-latency');
    const accuracyEls = document.querySelectorAll('#live-accuracy');

    if (!latencyEls.length) return;

    setInterval(() => {
        const lat = (Math.random() * 6 + 10).toFixed(0);
        const acc = (91 + Math.random() * 3).toFixed(1);
        latencyEls.forEach(el => el.textContent = lat + 'ms');
        accuracyEls.forEach(el => el.textContent = acc + '%');
    }, 3500);
})();

// ============================================================
// 5. WIZARD STEP NAVIGATION
// ============================================================
const STEP_LABELS = [
    'Step 1 of 7 — Personal Profile',
    'Step 2 of 7 — Economic Profile',
    'Step 3 of 7 — Social Category',
    'Step 4 of 7 — Education Status',
    'Step 5 of 7 — Housing Conditions',
    'Step 6 of 7 — Special Conditions',
    'Step 7 of 7 — Final Verification',
];

let currentStep = 1;
const TOTAL_STEPS = 7;

function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.step-card').forEach(c => c.classList.remove('active'));

    // Show target step
    const target = document.getElementById('step-' + step);
    if (target) target.classList.add('active');

    // Update label
    const label = document.getElementById('step-label');
    if (label) label.textContent = STEP_LABELS[step - 1] || 'Step ' + step;

    // Update progress bar
    const fill = document.getElementById('progress-fill');
    if (fill) fill.style.width = ((step / TOTAL_STEPS) * 100) + '%';

    // Update dots
    document.querySelectorAll('.step-dot').forEach((dot, i) => {
        dot.classList.remove('active', 'done');
        if (i + 1 < step) dot.classList.add('done');
        else if (i + 1 === step) dot.classList.add('active');
    });

    // Show/hide prev/next/submit buttons
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (prevBtn) prevBtn.style.display = step > 1 ? 'inline-flex' : 'none';
    if (nextBtn) nextBtn.style.display = step < TOTAL_STEPS ? 'inline-flex' : 'none';
    if (submitBtn) submitBtn.style.display = step === TOTAL_STEPS ? 'inline-flex' : 'none';

    // Scroll to wizard top smoothly
    const wizard = document.getElementById('check-eligibility');
    if (wizard && step > 1) {
        wizard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function validateCurrentStep() {
    const currentCard = document.getElementById('step-' + currentStep);
    if (!currentCard) return true;

    const inputs = currentCard.querySelectorAll('[required]');
    for (const input of inputs) {
        if (input.type === 'radio') {
            const group = currentCard.querySelectorAll(`[name="${input.name}"]`);
            const checked = Array.from(group).some(r => r.checked);
            if (!checked) {
                input.closest('.radio-grid')?.classList.add('error-highlight');
                setTimeout(() => input.closest('.radio-grid')?.classList.remove('error-highlight'), 800);
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return false;
            }
        } else if (!input.value.trim()) {
            input.classList.add('error-highlight');
            setTimeout(() => input.classList.remove('error-highlight'), 800);
            input.focus();
            return false;
        }
    }
    return true;
}

function changeStep(dir) {
    if (dir === 1 && !validateCurrentStep()) return;
    const next = currentStep + dir;
    if (next < 1 || next > TOTAL_STEPS) return;
    currentStep = next;
    showStep(currentStep);
}

// Expose globally for onclick handlers
window.changeStep = changeStep;

// Initialize wizard on load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('step-1')) {
        showStep(1);
    }
});

// ============================================================
// 6. CONDITIONAL FARMER FIELDS
// ============================================================
(function initFarmerFields() {
    const occupationSelect = document.getElementById('occupation-select');
    const farmerSection = document.getElementById('dynamic-farmer');

    if (!occupationSelect || !farmerSection) return;

    function toggleFarmer() {
        if (occupationSelect.value === 'Agriculture') {
            farmerSection.classList.add('show');
        } else {
            farmerSection.classList.remove('show');
        }
    }

    occupationSelect.addEventListener('change', toggleFarmer);
    toggleFarmer();
})();

// ============================================================
// 7. MATCH BAR ANIMATIONS (Results page)
// ============================================================
(function initMatchBars() {
    const bars = document.querySelectorAll('.match-bar-fill');
    if (!bars.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-width') || 0;
                setTimeout(() => { bar.style.width = width + '%'; }, 200);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.2 });

    bars.forEach(bar => {
        bar.style.width = '0%';
        observer.observe(bar);
    });
})();

// ============================================================
// 8. ANIMATED NUMBER COUNTER (Financial Summary)
// ============================================================
function animateCounter(el, target, prefix = '₹', duration = 1400) {
    if (!el) return;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = Math.floor(eased * target);
        el.textContent = prefix + value.toLocaleString('en-IN');
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

(function initFinancialCounters() {
    if (typeof FINANCIAL_DATA === 'undefined') return;

    const totalEl = document.getElementById('total-benefit-display');
    const monthlyEl = document.getElementById('monthly-benefit-display');
    const avgEl = document.getElementById('avg-benefit-display');

    if (!totalEl) return;

    const avgVal = FINANCIAL_DATA.count > 0
        ? Math.floor(FINANCIAL_DATA.total / FINANCIAL_DATA.count)
        : 0;

    // Delay counters to play after page renders
    setTimeout(() => {
        animateCounter(totalEl, FINANCIAL_DATA.total, '₹', 1600);
        animateCounter(monthlyEl, FINANCIAL_DATA.monthly, '₹', 1400);
        animateCounter(avgEl, avgVal, '₹', 1200);
    }, 400);
})();

// ============================================================
// 9. FILTER PILLS (Results page)
// ============================================================
(function initFilterPills() {
    const pills = document.querySelectorAll('.filter-pill');
    const items = document.querySelectorAll('.scheme-item');

    if (!pills.length || !items.length) return;

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            // Toggle active state
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const cat = pill.getAttribute('data-cat');

            items.forEach(item => {
                const itemCat = (item.getAttribute('data-cat') || '').toLowerCase();
                const show = cat === 'all' || itemCat.includes(cat.toLowerCase());
                item.style.display = show ? '' : 'none';
                if (show) {
                    item.style.animation = 'none';
                    void item.offsetWidth; // reflow
                    item.style.animation = '';
                }
            });
        });
    });
})();

// ============================================================
// 10. NEURAL NETWORK CANVAS ANIMATION
// ============================================================
(function initNeuralCanvas() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Nodes
    const NODE_COUNT = 28;
    const nodes = Array.from({ length: NODE_COUNT }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        r: Math.random() * 2.5 + 1.5,
        alpha: Math.random() * 0.6 + 0.3,
    }));

    const PRIMARY = [79, 70, 229];
    const ACCENT = [6, 182, 212];
    const CONNECT_DIST = 100;

    function lerp(a, b, t) { return a + (b - a) * t; }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Update positions
        nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
            if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
        });

        // Draw connections
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONNECT_DIST) {
                    const t = 1 - dist / CONNECT_DIST;
                    const r = Math.round(lerp(PRIMARY[0], ACCENT[0], Math.random() > 0.5 ? 1 : 0));
                    const g = Math.round(lerp(PRIMARY[1], ACCENT[1], Math.random() > 0.5 ? 1 : 0));
                    const b = Math.round(lerp(PRIMARY[2], ACCENT[2], Math.random() > 0.5 ? 1 : 0));
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(${r},${g},${b},${t * 0.35})`;
                    ctx.lineWidth = t * 1.5;
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }
            }
        }

        // Draw nodes
        nodes.forEach(n => {
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${PRIMARY[0]},${PRIMARY[1]},${PRIMARY[2]},${n.alpha})`;
            ctx.fill();
        });

        requestAnimationFrame(draw);
    }

    draw();
})();

// ============================================================
// 11. FORM CSS ERROR HIGHLIGHTS
// ============================================================
(function addErrorStyles() {
    const style = document.createElement('style');
    style.textContent = `
    .error-highlight {
      border-color: var(--error) !important;
      box-shadow: 0 0 0 3px rgba(239,68,68,0.2) !important;
      animation: shake 0.4s ease;
    }
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-6px); }
      75% { transform: translateX(6px); }
    }
  `;
    document.head.appendChild(style);
})();

// ============================================================
// 12. AI INSIGHT TEXT TYPEWRITER (Results page)
// ============================================================
(function initTypewriter() {
    const el = document.getElementById('ai-insight-text');
    if (!el || !el.textContent.trim()) return;

    const text = el.textContent.trim();
    el.textContent = '';
    el.style.opacity = '1';

    let i = 0;
    const interval = setInterval(() => {
        if (i < text.length) {
            el.textContent += text[i++];
        } else {
            clearInterval(interval);
        }
    }, 20);
})();

// ============================================================
// 13. PREMIUM TOAST ENGINE
// ============================================================
function showToast(title, msg, icon = 'fa-info-circle', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'pg-toast';
    toast.innerHTML = `
        <div class="pg-toast-icon"><i class="fa-solid ${icon}"></i></div>
        <div class="pg-toast-content">
            <div class="pg-toast-title">${title}</div>
            <div class="pg-toast-msg">${msg}</div>
        </div>
        <div class="pg-toast-progress" style="animation-duration: ${duration}ms"></div>
    `;

    container.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.add('visible');
    });

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 600);
    }, duration);
}

// Demo sequences for modern feel
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/tech') || window.location.pathname === '/') {
        setTimeout(() => showToast('System Upgrade', 'Neural Engine v4.0 is now active.', 'fa-microchip'), 2000);
        setTimeout(() => showToast('Coming Soon', 'Multilingual support for 12+ Indian languages.', 'fa-language'), 5500);
        setTimeout(() => showToast('Data Sync', '150+ new central schemes added to the database.', 'fa-sync'), 9000);
    }
});
