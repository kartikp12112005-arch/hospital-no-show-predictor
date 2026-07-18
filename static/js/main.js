/* ==========================================================================
   Smart Hospital No-Show Predictor — main.js
   Handles: dark mode toggle, predict-form UX, scroll reveals, and every
   Chart.js visualization across Result / Dashboard / Analytics / Model
   Comparison pages. Every function guards on element existence so this
   single file can safely run on every page.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initDarkMode();
    initPredictFormUX();
    initScrollReveal();
    initAutoDismissAlerts();
    initDownloadReportButton();

    initProbabilityChart();
    initDashboardCharts();
    initAnalyticsCharts();
    initModelComparisonChart();
});

/* --------------------------------------------------------------------
   Dark mode toggle — preference persisted in localStorage
   -------------------------------------------------------------------- */
function initDarkMode() {
    const toggleBtn = document.getElementById("darkModeToggle");
    const root = document.documentElement;
    const STORAGE_KEY = "medipredict-theme";

    const applyTheme = (theme) => {
        root.setAttribute("data-bs-theme", theme);
        if (toggleBtn) {
            const icon = toggleBtn.querySelector("i");
            if (icon) {
                icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
            }
        }
    };

    const savedTheme = localStorage.getItem(STORAGE_KEY);
    if (savedTheme) {
        applyTheme(savedTheme);
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const current = root.getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
            const next = current === "dark" ? "light" : "dark";
            applyTheme(next);
            localStorage.setItem(STORAGE_KEY, next);
        });
    }
}

/* --------------------------------------------------------------------
   Predict form: loading spinner + basic client-side validation feedback.
   Server-side validation (utils/validators.py) remains authoritative;
   this only improves perceived responsiveness.
   -------------------------------------------------------------------- */
function initPredictFormUX() {
    const form = document.getElementById("predictForm");
    const submitBtn = document.getElementById("predictSubmitBtn");
    if (!form || !submitBtn) return;

    form.addEventListener("submit", (event) => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add("was-validated");
            return;
        }
        submitBtn.classList.add("is-loading");
        submitBtn.setAttribute("disabled", "disabled");
        // Form still submits normally (full page reload to /predict).
    });
}

/* --------------------------------------------------------------------
   Fade/slide-in reveal for major section blocks as they scroll into view
   -------------------------------------------------------------------- */
function initScrollReveal() {
    const targets = document.querySelectorAll(".section-block, .feature-card, .mini-stat-card");
    if (!targets.length || !("IntersectionObserver" in window)) return;

    targets.forEach((el) => el.classList.add("reveal-on-scroll"));

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    targets.forEach((el) => observer.observe(el));
}

/* --------------------------------------------------------------------
   Auto-dismiss flash messages after a few seconds
   -------------------------------------------------------------------- */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            if (window.bootstrap && bootstrap.Alert) {
                const instance = bootstrap.Alert.getOrCreateInstance(alert);
                instance.close();
            }
        }, 6000);
    });
}

/* --------------------------------------------------------------------
   PDF report download button (result page)
   -------------------------------------------------------------------- */
function initDownloadReportButton() {
    const btn = document.getElementById("downloadReportBtn");
    if (!btn) return;
    btn.addEventListener("click", () => {
        window.location.href = "/report/download";
    });
}

/* --------------------------------------------------------------------
   Shared Chart.js theme so every chart looks consistent
   -------------------------------------------------------------------- */
const CHART_COLORS = {
    blue: "#1768ac",
    blueBright: "#2ec4e6",
    green: "#2fae79",
    red: "#e4572e",
    grid: "#e1eaf2",
    ink: "#4a5b78",
};

function baseChartOptions(overrides = {}) {
    return Object.assign(
        {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { labels: { color: CHART_COLORS.ink, font: { family: "Inter" } } },
            },
            scales: {
                x: { grid: { color: CHART_COLORS.grid }, ticks: { color: CHART_COLORS.ink } },
                y: { grid: { color: CHART_COLORS.grid }, ticks: { color: CHART_COLORS.ink } },
            },
        },
        overrides
    );
}

/* --------------------------------------------------------------------
   Result page: Attend vs No-Show probability doughnut
   -------------------------------------------------------------------- */
function initProbabilityChart() {
    const canvas = document.getElementById("probabilityChart");
    if (!canvas || typeof Chart === "undefined") return;

    const attend = parseFloat(canvas.dataset.attend || "0");
    const noShow = parseFloat(canvas.dataset.noshow || "0");

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Probability of Attending", "Probability of No-Show"],
            datasets: [
                {
                    data: [attend, noShow],
                    backgroundColor: [CHART_COLORS.green, CHART_COLORS.red],
                    borderWidth: 0,
                },
            ],
        },
        options: {
            responsive: true,
            cutout: "68%",
            plugins: {
                legend: { position: "bottom", labels: { color: CHART_COLORS.ink } },
            },
        },
    });
}

/* --------------------------------------------------------------------
   Dashboard: pie, bar, and live trend line chart
   -------------------------------------------------------------------- */
function initDashboardCharts() {
    if (typeof Chart === "undefined") return;

    const pieCanvas = document.getElementById("dashboardPieChart");
    if (pieCanvas) {
        const attend = parseInt(pieCanvas.dataset.attend || "0", 10);
        const noShow = parseInt(pieCanvas.dataset.noshow || "0", 10);
        new Chart(pieCanvas, {
            type: "pie",
            data: {
                labels: ["Attend", "No-Show"],
                datasets: [{ data: [attend, noShow], backgroundColor: [CHART_COLORS.green, CHART_COLORS.red] }],
            },
            options: { plugins: { legend: { position: "bottom", labels: { color: CHART_COLORS.ink } } } },
        });
    }

    const barCanvas = document.getElementById("dashboardBarChart");
    if (barCanvas) {
        const attend = parseInt(barCanvas.dataset.attend || "0", 10);
        const noShow = parseInt(barCanvas.dataset.noshow || "0", 10);
        new Chart(barCanvas, {
            type: "bar",
            data: {
                labels: ["Attend", "No-Show"],
                datasets: [
                    {
                        label: "Predictions",
                        data: [attend, noShow],
                        backgroundColor: [CHART_COLORS.blue, CHART_COLORS.red],
                        borderRadius: 6,
                    },
                ],
            },
            options: baseChartOptions({ plugins: { legend: { display: false } } }),
        });
    }

    const lineCanvas = document.getElementById("dashboardLineChart");
    if (lineCanvas) {
        fetch("/api/dashboard-trend")
            .then((res) => res.json())
            .then((data) => {
                new Chart(lineCanvas, {
                    type: "line",
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                label: "Attend",
                                data: data.attend,
                                borderColor: CHART_COLORS.green,
                                backgroundColor: "transparent",
                                tension: 0.35,
                            },
                            {
                                label: "No-Show",
                                data: data.no_show,
                                borderColor: CHART_COLORS.red,
                                backgroundColor: "transparent",
                                tension: 0.35,
                            },
                        ],
                    },
                    options: baseChartOptions(),
                });
            })
            .catch(() => {
                /* Silently ignore — dashboard still functions without the trend chart. */
            });
    }
}

/* --------------------------------------------------------------------
   Analytics page: gender, age, disease, SMS-effect, monthly trend
   -------------------------------------------------------------------- */
function initAnalyticsCharts() {
    if (typeof Chart === "undefined") return;

    const parseStats = (canvas) => {
        try {
            return JSON.parse(canvas.dataset.stats || "{}");
        } catch (e) {
            return {};
        }
    };

    const genderCanvas = document.getElementById("genderChart");
    if (genderCanvas) {
        const stats = parseStats(genderCanvas);
        new Chart(genderCanvas, {
            type: "doughnut",
            data: {
                labels: Object.keys(stats),
                datasets: [{ data: Object.values(stats), backgroundColor: [CHART_COLORS.blue, "#f28fb1"] }],
            },
            options: { plugins: { legend: { position: "bottom", labels: { color: CHART_COLORS.ink } } } },
        });
    }

    const ageCanvas = document.getElementById("ageChart");
    if (ageCanvas) {
        const stats = parseStats(ageCanvas);
        new Chart(ageCanvas, {
            type: "bar",
            data: {
                labels: Object.keys(stats),
                datasets: [{ label: "Patients", data: Object.values(stats), backgroundColor: CHART_COLORS.blueBright, borderRadius: 6 }],
            },
            options: baseChartOptions({ plugins: { legend: { display: false } } }),
        });
    }

    const diseaseCanvas = document.getElementById("diseaseChart");
    if (diseaseCanvas) {
        const stats = parseStats(diseaseCanvas);
        new Chart(diseaseCanvas, {
            type: "bar",
            data: {
                labels: Object.keys(stats),
                datasets: [{ label: "Patients", data: Object.values(stats), backgroundColor: CHART_COLORS.blue, borderRadius: 6 }],
            },
            options: baseChartOptions({ indexAxis: "y", plugins: { legend: { display: false } } }),
        });
    }

    const smsCanvas = document.getElementById("smsChart");
    if (smsCanvas) {
        const stats = parseStats(smsCanvas);
        const labels = Object.keys(stats).map((k) => (k === "1" ? "SMS Received" : "No SMS"));
        new Chart(smsCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{ label: "Attendance Rate (%)", data: Object.values(stats), backgroundColor: [CHART_COLORS.green, CHART_COLORS.red], borderRadius: 6 }],
            },
            options: baseChartOptions({ plugins: { legend: { display: false } } }),
        });
    }

    const monthlyCanvas = document.getElementById("monthlyTrendChart");
    if (monthlyCanvas) {
        const stats = parseStats(monthlyCanvas);
        new Chart(monthlyCanvas, {
            type: "line",
            data: {
                labels: Object.keys(stats),
                datasets: [
                    {
                        label: "Attendance Rate (%)",
                        data: Object.values(stats),
                        borderColor: CHART_COLORS.blue,
                        backgroundColor: "rgba(23, 104, 172, 0.1)",
                        fill: true,
                        tension: 0.35,
                    },
                ],
            },
            options: baseChartOptions(),
        });
    }
}

/* --------------------------------------------------------------------
   Model Comparison page: grouped bar chart across all four models
   -------------------------------------------------------------------- */
function initModelComparisonChart() {
    const canvas = document.getElementById("modelComparisonChart");
    if (!canvas || typeof Chart === "undefined") return;

    let results;
    try {
        results = JSON.parse(canvas.dataset.results || "{}");
    } catch (e) {
        return;
    }

    const modelNames = Object.keys(results);
    const metricKeys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"];
    const metricLabels = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"];
    const metricColors = [CHART_COLORS.blue, CHART_COLORS.blueBright, "#7c5cff", CHART_COLORS.green, "#f2a541"];

    const datasets = metricKeys.map((key, i) => ({
        label: metricLabels[i],
        data: modelNames.map((name) => results[name][key]),
        backgroundColor: metricColors[i],
        borderRadius: 4,
    }));

    new Chart(canvas, {
        type: "bar",
        data: { labels: modelNames, datasets },
        options: baseChartOptions({ plugins: { legend: { position: "bottom", labels: { color: CHART_COLORS.ink } } } }),
    });
}
