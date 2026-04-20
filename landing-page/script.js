/**
 * Praja Guide - Interaction & Neural Visualization
 */

document.addEventListener('DOMContentLoaded', () => {

    // 1. Smooth Reveal on Scroll (Intersection Observer)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');

                // Trigger counters if this is the hero stat section
                if (entry.target.classList.contains('hero-stats')) {
                    startCounters();
                }
            }
        });
    }, observerOptions);

    // Track elements for reveal
    const revealElements = [
        ...document.querySelectorAll('.glass-card'),
        ...document.querySelectorAll('.section-title'),
        ...document.querySelectorAll('.member-card'),
        document.querySelector('.hero-stats'),
        document.querySelector('.pipeline-flow')
    ];

    revealElements.forEach(el => {
        if (el) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
            revealObserver.observe(el);
        }
    });

    // Add revealed class style via JS (keeping CSS clean)
    const styleBlock = document.createElement('style');
    styleBlock.innerHTML = `.revealed { opacity: 1 !important; transform: translateY(0) !important; }`;
    document.head.appendChild(styleBlock);

    // 2. Counter Animation Logic
    const startCounters = () => {
        const counters = document.querySelectorAll('.stat-value');
        const speed = 200;

        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const suffix = counter.getAttribute('data-suffix') || '';
            const increment = target / speed;

            const updateCount = () => {
                const count = +counter.innerText.replace(/[^\d]/g, '');

                if (count < target) {
                    const nextVal = Math.ceil(count + increment);
                    counter.innerText = (nextVal > target ? target : nextVal) + suffix;
                    setTimeout(updateCount, 1);
                } else {
                    counter.innerText = target + suffix;
                }
            };

            // Only start if it's currently 0 or just placeholder
            if (counter.innerText === '0' || counter.innerText === '0' + suffix) {
                updateCount();
            }
        });
    };

    // 3. Mouse Parallax for Glass Orbs
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;

        const orb1 = document.querySelector('.orb-1');
        const orb2 = document.querySelector('.orb-2');

        if (orb1) {
            orb1.style.transform = `translate(${x * 50}px, ${y * 50}px) scale(1)`;
        }
        if (orb2) {
            orb2.style.transform = `translate(-${x * 30}px, -${y * 30}px) scale(1.1)`;
        }
    });

    // 4. Navbar Dynamic Styling
    const nav = document.querySelector('.glass-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            nav.style.background = 'rgba(6, 9, 16, 0.8)';
            nav.style.width = 'calc(100% - 80px)';
            nav.style.padding = '8px 32px';
        } else {
            nav.style.background = 'rgba(10, 15, 25, 0.4)';
            nav.style.width = 'calc(100% - 48px)';
            nav.style.padding = '12px 32px';
        }
    });

    // 5. Interactive Chart Dasharray setup
    // This allows the circular charts to animate correctly based on their stroke-dasharray
    const charts = document.querySelectorAll('.circular-chart .circle');
    charts.forEach(chart => {
        const valueStr = chart.getAttribute('stroke-dasharray');
        if (valueStr) {
            chart.style.strokeDasharray = '0, 100';
            setTimeout(() => {
                chart.style.strokeDasharray = valueStr;
                chart.style.transition = 'stroke-dasharray 1.5s ease-out';
            }, 500);
        }
    });

    console.log('🚀 Praja Guide AI Intelligence Console v2.0 Initialized');
});
