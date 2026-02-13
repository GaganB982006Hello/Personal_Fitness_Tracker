// Section Navigation
const sections = {
    dashboard: {
        title: "Health Dashboard",
        desc: "Overview of your fitness metrics and statistics."
    },
    predict: {
        title: "Calorie Predictor",
        desc: "Calculate estimated energy expenditure during exercise."
    },
    about: {
        title: "About FitPredict",
        desc: "Learn more about the technology and algorithms."
    }
};

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('main section').forEach(section => {
        section.classList.remove('active');
    });

    // Update nav links
    document.querySelectorAll('.sidebar nav a').forEach(link => {
        link.classList.remove('active');
        if (link.textContent.toLowerCase().includes(sectionId)) {
            link.classList.add('active');
        }
    });

    // Show selected section
    const targetSection = document.getElementById(`${sectionId}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update headers
    document.getElementById('section-title').textContent = sections[sectionId].title;
    document.getElementById('section-desc').textContent = sections[sectionId].desc;
}

// Global chart instances
let charts = {};

// Fetch Stats and Render Charts
async function loadStats() {
    console.log('Loading statistics...');
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.ok}`);
        const stats = await response.json();

        console.log('Stats received:', stats);

        // Update Stat Cards with protection
        if (document.getElementById('avg-calories')) document.getElementById('avg-calories').textContent = `${Math.round(stats.avg_calories || 0)} kcal`;
        if (document.getElementById('avg-duration')) document.getElementById('avg-duration').textContent = `${Math.round(stats.avg_duration || 0)} min`;
        if (document.getElementById('avg-heart-rate')) document.getElementById('avg-heart-rate').textContent = `${Math.round(stats.avg_heart_rate || 0)} bpm`;
        if (document.getElementById('total-records')) document.getElementById('total-records').textContent = (stats.total_records || 0).toLocaleString();

        if (typeof Chart !== 'undefined') {
            renderCharts(stats);
            loadTrends();
        } else {
            console.warn('Chart.js not loaded. Check your internet connection.');
            // Fallback for user: show message
            document.querySelectorAll('.canvas-wrapper').forEach(wrapper => {
                wrapper.innerHTML = '<div class="no-chart-msg">Please check your internet connection to load charts.</div>';
            });
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function renderCharts(stats) {
    // Age Distribution Chart
    const ageCtx = document.getElementById('ageChart').getContext('2d');
    if (charts.age) charts.age.destroy();
    charts.age = new Chart(ageCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(stats.age_dist),
            datasets: [{
                label: 'Population Count',
                data: Object.values(stats.age_dist),
                backgroundColor: 'rgba(131, 58, 180, 0.6)',
                borderColor: '#833ab4',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // BMI Distribution Chart
    const bmiCtx = document.getElementById('bmiChart').getContext('2d');
    if (charts.bmi) charts.bmi.destroy();
    charts.bmi = new Chart(bmiCtx, {
        type: 'pie',
        data: {
            labels: Object.keys(stats.bmi_dist),
            datasets: [{
                data: Object.values(stats.bmi_dist),
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#f87171'],
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function loadTrends() {
    try {
        const response = await fetch('/api/historical-data?days=7');
        const data = await response.json();
        renderTrendCharts(data);
    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

// Render Trend Charts with Robustness
function renderTrendCharts(data) {
    if (!data || !data.dates) {
        console.error('Missing trend data dates');
        return;
    }

    const labels = data.dates.map(d => d.split('-').slice(1).join('/'));

    const chartConfigs = [
        { id: 'stepsChart', key: 'steps', type: 'bar', label: 'Steps', color: '#3b82f6' },
        { id: 'heartRateTrendChart', key: 'heart_rate', type: 'line', label: 'Heart Rate', color: '#f87171' },
        { id: 'caloriesTrendChart', key: 'calories', type: 'line', label: 'Calories', color: '#ec4899', fill: true },
        { id: 'sleepChart', key: 'sleep_hours', type: 'bar', label: 'Slept (h)', color: '#833ab4' },
        { id: 'healthInsightsChart', key: 'spo2', type: 'line', label: 'SpO2 %', color: '#3b82f6' }
    ];

    chartConfigs.forEach(cfg => {
        try {
            const canvas = document.getElementById(cfg.id);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            if (charts[cfg.key]) charts[cfg.key].destroy();

            charts[cfg.key] = new Chart(ctx, {
                type: cfg.type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: cfg.label,
                        data: data[cfg.id === 'healthInsightsChart' ? 'spo2' : cfg.key],
                        borderColor: cfg.color,
                        backgroundColor: cfg.fill ? cfg.color + '33' : cfg.color,
                        fill: cfg.fill || false,
                        tension: 0.4,
                        borderRadius: cfg.type === 'bar' ? 4 : 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8', font: { size: 10 } } } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } }
                    }
                }
            });
        } catch (err) {
            console.error(`Error rendering chart ${cfg.id}:`, err);
        }
    });

    // Special case for multi-dataset healthInsightsChart (re-handling to add stress)
    try {
        const healthCanvas = document.getElementById('healthInsightsChart');
        if (healthCanvas) {
            const hCtx = healthCanvas.getContext('2d');
            if (charts['health_full']) charts['health_full'].destroy();
            charts['health_full'] = new Chart(hCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'SpO2 %', data: data.spo2, borderColor: '#3b82f6', tension: 0.2 },
                        { label: 'Stress', data: data.stress, borderColor: '#f59e0b', tension: 0.2 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }
    } catch (e) { console.error('Error rendering full health chart:', e); }

    // Special case for Active vs Inactive
    try {
        const activeCanvas = document.getElementById('activeTimeChart');
        if (activeCanvas) {
            const aCtx = activeCanvas.getContext('2d');
            if (charts.active) charts.active.destroy();
            charts.active = new Chart(aCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Active', 'Inactive'],
                    datasets: [{ data: [65, 35], backgroundColor: ['#10b981', '#1e293b'], borderWidth: 0 }]
                },
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } }
            });
        }
    } catch (e) { console.error('Error rendering active chart:', e); }
}

// Prediction Form Handling
document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Show loading state
    const submitBtn = e.target.querySelector('.submit-btn');
    const originalBtnHtml = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        // Counter animation for calories
        const display = document.getElementById('calories-result');
        const targetValue = result.calories;
        animateValue(display, 0, targetValue, 1000);

        // Highlight the result card
        const resultCard = document.getElementById('prediction-result');
        resultCard.style.borderColor = '#fd1d1d';
        setTimeout(() => resultCard.style.borderColor = '', 2000);

    } catch (error) {
        console.error('Prediction error:', error);
        alert('Failed to calculate calories. Please check your inputs.');
    } finally {
        submitBtn.innerHTML = originalBtnHtml;
        submitBtn.disabled = false;
    }
});

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = (progress * (end - start) + start).toFixed(2);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    // Pre-select dashboard
    showSection('dashboard');

    // Handle animation delays from data attributes
    document.querySelectorAll('.animate-up').forEach(el => {
        const delay = el.getAttribute('data-delay');
        if (delay) el.style.setProperty('--delay', delay);
    });

    // Update Fitness Score (Simulated for results section)
    const score = 80 + Math.floor(Math.random() * 15);
    document.getElementById('fitness-score').textContent = `${score}/100`;
});
