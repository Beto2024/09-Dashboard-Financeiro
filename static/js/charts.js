/**
 * charts.js — Chart.js Dashboard Charts
 */

const CHART_DEFAULTS = {
    color: '#8b949e',
    gridColor: 'rgba(48, 54, 61, 0.8)',
    fontFamily: "'Segoe UI', system-ui, sans-serif",
};

Chart.defaults.color = CHART_DEFAULTS.color;
Chart.defaults.font.family = CHART_DEFAULTS.fontFamily;

function buildChartOptions(type, extras = {}) {
    const base = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: CHART_DEFAULTS.color, padding: 16, boxWidth: 12 },
            },
            tooltip: {
                backgroundColor: '#1c2128',
                borderColor: '#30363d',
                borderWidth: 1,
                titleColor: '#e6edf3',
                bodyColor: '#8b949e',
                callbacks: {
                    label: function(ctx) {
                        const val = ctx.parsed.y ?? ctx.parsed;
                        return ` R$ ${Number(val).toLocaleString('pt-BR', {minimumFractionDigits:2})}`;
                    }
                }
            }
        }
    };

    if (type === 'bar' || type === 'line') {
        base.scales = {
            x: {
                grid: { color: CHART_DEFAULTS.gridColor },
                ticks: { color: CHART_DEFAULTS.color },
            },
            y: {
                grid: { color: CHART_DEFAULTS.gridColor },
                ticks: {
                    color: CHART_DEFAULTS.color,
                    callback: val => 'R$ ' + Number(val).toLocaleString('pt-BR', {minimumFractionDigits:0}),
                },
                beginAtZero: true,
            }
        };
    }

    if (type === 'pie' || type === 'doughnut') {
        base.plugins.tooltip.callbacks.label = function(ctx) {
            const val = ctx.parsed;
            return ` ${ctx.label}: R$ ${Number(val).toLocaleString('pt-BR', {minimumFractionDigits:2})}`;
        };
        base.plugins.legend.position = 'bottom';
    }

    return Object.assign(base, extras);
}

async function fetchJSON(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('Chart fetch error:', url, err);
        return null;
    }
}

let chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

async function initDashboardCharts(month, year) {
    // 1. Expenses by Category (Pie)
    const catCanvas = document.getElementById('expensesByCategoryChart');
    if (catCanvas) {
        const data = await fetchJSON(`/api/chart/expenses-by-category?month=${month}&year=${year}`);
        if (data) {
            destroyChart('expenses');
            chartInstances['expenses'] = new Chart(catCanvas, {
                type: 'doughnut',
                data: data,
                options: buildChartOptions('pie', {
                    cutout: '55%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: CHART_DEFAULTS.color, padding: 12, boxWidth: 12, font: { size: 11 } }
                        }
                    }
                })
            });
        } else {
            catCanvas.parentElement.innerHTML = '<p class="text-muted text-center py-5">Sem dados de despesas no período.</p>';
        }
    }

    // 2. Monthly Comparison (Bar)
    const barCanvas = document.getElementById('monthlyComparisonChart');
    if (barCanvas) {
        const data = await fetchJSON(`/api/chart/monthly-comparison?year=${year}`);
        if (data) {
            destroyChart('monthly');
            chartInstances['monthly'] = new Chart(barCanvas, {
                type: 'bar',
                data: data,
                options: buildChartOptions('bar', {
                    plugins: {
                        legend: { labels: { color: CHART_DEFAULTS.color, padding: 16, boxWidth: 12 } }
                    }
                })
            });
        }
    }

    // 3. Balance Evolution (Line)
    const lineCanvas = document.getElementById('balanceEvolutionChart');
    if (lineCanvas) {
        const data = await fetchJSON(`/api/chart/balance-evolution?year=${year}`);
        if (data) {
            destroyChart('balance');
            chartInstances['balance'] = new Chart(lineCanvas, {
                type: 'line',
                data: data,
                options: buildChartOptions('line', {
                    plugins: {
                        legend: { labels: { color: CHART_DEFAULTS.color, padding: 16, boxWidth: 12 } }
                    }
                })
            });
        }
    }
}
