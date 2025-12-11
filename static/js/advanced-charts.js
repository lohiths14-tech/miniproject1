/**
 * Advanced Charts and Data Visualizations
 * Uses D3.js and Chart.js for interactive, beautiful charts
 */

// Color schemes
const colorSchemes = {
    primary: ['#667eea', '#764ba2', '#f093fb', '#4facfe'],
    success: ['#11998e', '#38ef7d', '#3cba92', '#0ba360'],
    warning: ['#f2994a', '#f2c94c', '#ff9966', '#ff5e62'],
    performance: ['#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
};

/**
 * Performance Trend Chart (Line Chart with D3.js)
 */
class PerformanceTrendChart {
    constructor(containerId, data) {
        this.container = d3.select(`#${containerId}`);
        this.data = data;
        this.margin = { top: 40, right: 60, bottom: 60, left: 60 };
        this.init();
    }

    init() {
        const containerNode = this.container.node();
        this.width = containerNode.getBoundingClientRect().width - this.margin.left - this.margin.right;
        this.height = 400 - this.margin.top - this.margin.bottom;

        // Clear existing
        this.container.html('');

        // Create SVG
        this.svg = this.container.append('svg')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

        this.render();
    }

    render() {
        // Parse dates
        this.data.forEach(d => {
            d.date = new Date(d.date);
            d.score = +d.score;
        });

        // Scales
        const x = d3.scaleTime()
            .domain(d3.extent(this.data, d => d.date))
            .range([0, this.width]);

        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([this.height, 0]);

        // Gradient for line
        const gradient = this.svg.append('defs')
            .append('linearGradient')
            .attr('id', 'line-gradient')
            .attr('gradientUnits', 'userSpaceOnUse')
            .attr('x1', 0).attr('y1', y(0))
            .attr('x2', 0).attr('y2', y(100));

        gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#667eea');

        gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#764ba2');

        // Line generator
        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.score))
            .curve(d3.curveMonotoneX);

        // Area generator for gradient fill
        const area = d3.area()
            .x(d => x(d.date))
            .y0(this.height)
            .y1(d => y(d.score))
            .curve(d3.curveMonotoneX);

        // Add gradient area
        this.svg.append('path')
            .datum(this.data)
            .attr('class', 'area')
            .attr('d', area)
            .style('fill', 'url(#line-gradient)')
            .style('opacity', 0.3);

        // Add line
        const path = this.svg.append('path')
            .datum(this.data)
            .attr('class', 'line')
            .attr('d', line)
            .style('fill', 'none')
            .style('stroke', 'url(#line-gradient)')
            .style('stroke-width', 3);

        // Animate line drawing
        const totalLength = path.node().getTotalLength();
        path
            .attr('stroke-dasharray', totalLength + ' ' + totalLength)
            .attr('stroke-dashoffset', totalLength)
            .transition()
            .duration(2000)
            .ease(d3.easeLinear)
            .attr('stroke-dashoffset', 0);

        // Add dots
        this.svg.selectAll('.dot')
            .data(this.data)
            .enter().append('circle')
            .attr('class', 'dot')
            .attr('cx', d => x(d.date))
            .attr('cy', d => y(d.score))
            .attr('r', 0)
            .style('fill', '#fff')
            .style('stroke', '#667eea')
            .style('stroke-width', 2)
            .transition()
            .delay((d, i) => i * 100)
            .duration(500)
            .attr('r', 5);

        // Add tooltip
        const tooltip = d3.select('body').append('div')
            .attr('class', 'chart-tooltip')
            .style('opacity', 0);

        this.svg.selectAll('.dot')
            .on('mouseover', function (event, d) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('r', 8);

                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);

                tooltip.html(`
                    <strong>${d.assignment || 'Assignment'}</strong><br/>
                    Score: ${d.score}%<br/>
                    ${d.date.toLocaleDateString()}
                `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', function () {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('r', 5);

                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });

        // Add axes
        this.svg.append('g')
            .attr('transform', `translate(0,${this.height})`)
            .call(d3.axisBottom(x).ticks(5))
            .selectAll('text')
            .style('fill', '#64748b')
            .style('font-size', '12px');

        this.svg.append('g')
            .call(d3.axisLeft(y).ticks(5))
            .selectAll('text')
            .style('fill', '#64748b')
            .style('font-size', '12px');

        // Add grid lines
        this.svg.append('g')
            .attr('class', 'grid')
            .attr('opacity', 0.1)
            .call(d3.axisLeft(y)
                .ticks(5)
                .tickSize(-this.width)
                .tickFormat(''));

        // Add labels
        this.svg.append('text')
            .attr('x', this.width / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', 'bold')
            .style('fill', '#1e293b')
            .text('Performance Trend');
    }
}

/**
 * Code Complexity Heatmap (D3.js)
 */
class ComplexityHeatmap {
    constructor(containerId, data) {
        this.container = d3.select(`#${containerId}`);
        this.data = data;
        this.margin = { top: 40, right: 60, bottom: 60, left: 100 };
        this.init();
    }

    init() {
        const containerNode = this.container.node();
        this.width = containerNode.getBoundingClientRect().width - this.margin.left - this.margin.right;
        this.height = 300 - this.margin.top - this.margin.bottom;

        this.container.html('');

        this.svg = this.container.append('svg')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

        this.render();
    }

    render() {
        const assignments = Array.from(new Set(this.data.map(d => d.assignment)));
        const metrics = ['Complexity', 'Best Practices', 'Performance'];

        const x = d3.scaleBand()
            .domain(metrics)
            .range([0, this.width])
            .padding(0.1);

        const y = d3.scaleBand()
            .domain(assignments)
            .range([0, this.height])
            .padding(0.1);

        const color = d3.scaleSequential()
            .domain([0, 100])
            .interpolator(d3.interpolateRgb('#fee', '#e11'));

        // Add cells
        this.svg.selectAll('.cell')
            .data(this.data)
            .enter().append('rect')
            .attr('class', 'cell')
            .attr('x', d => x(d.metric))
            .attr('y', d => y(d.assignment))
            .attr('width', x.bandwidth())
            .attr('height', y.bandwidth())
            .style('fill', d => color(d.value))
            .style('opacity', 0)
            .transition()
            .duration(1000)
            .delay((d, i) => i * 50)
            .style('opacity', 1);

        // Add axes
        this.svg.append('g')
            .call(d3.axisLeft(y))
            .selectAll('text')
            .style('font-size', '12px')
            .style('fill', '#64748b');

        this.svg.append('g')
            .attr('transform', `translate(0,${this.height})`)
            .call(d3.axisBottom(x))
            .selectAll('text')
            .style('font-size', '12px')
            .style('fill', '#64748b');
    }
}

/**
 * Animated Leaderboard (Chart.js + Custom Animations)
 */
class AnimatedLeaderboard {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.init();
    }

    init() {
        this.container.innerHTML = '';

        const leaderboardHTML = this.data.map((student, index) => `
            <div class="leaderboard-item" style="animation-delay: ${index * 0.1}s">
                <div class="rank rank-${index + 1}">#${index + 1}</div>
                <div class="student-info">
                    <div class="student-name">${student.name}</div>
                    <div class="student-stats">${student.submissions} submissions</div>
                </div>
                <div class="points-container">
                    <div class="points-bar" style="width: 0%" data-width="${(student.points / this.data[0].points) * 100}%"></div>
                    <div class="points-value">${student.points.toLocaleString()} pts</div>
                </div>
                ${index < 3 ? `<div class="trophy trophy-${index + 1}">🏆</div>` : ''}
            </div>
        `).join('');

        this.container.innerHTML = leaderboardHTML;

        // Animate progress bars
        setTimeout(() => {
            this.container.querySelectorAll('.points-bar').forEach(bar => {
                bar.style.width = bar.dataset.width;
            });
        }, 100);
    }
}

/**
 * Dynamic Chart Manager
 * Handles real-time updates, auto-refresh, and data synchronization
 */
class DynamicChartManager {
    constructor() {
        this.charts = new Map();
        this.refreshIntervals = new Map();
        this.isVisible = true;
        this.setupVisibilityListener();
    }

    setupVisibilityListener() {
        document.addEventListener('visibilitychange', () => {
            this.isVisible = !document.hidden;
            if (this.isVisible) {
                this.refreshAllCharts();
            }
        });
    }

    registerChart(id, chartInstance, refreshInterval = 30000) {
        this.charts.set(id, chartInstance);

        if (refreshInterval > 0) {
            const interval = setInterval(() => {
                if (this.isVisible) {
                    this.refreshChart(id);
                }
            }, refreshInterval);
            this.refreshIntervals.set(id, interval);
        }
    }

    async refreshChart(id) {
        const chart = this.charts.get(id);
        if (!chart || !chart.refresh) return;

        try {
            await chart.refresh();
        } catch (error) {
            console.error(`Failed to refresh chart ${id}:`, error);
        }
    }

    refreshAllCharts() {
        this.charts.forEach((chart, id) => {
            this.refreshChart(id);
        });
    }

    destroy() {
        this.refreshIntervals.forEach(interval => clearInterval(interval));
        this.refreshIntervals.clear();
        this.charts.clear();
    }
}

// Global chart manager instance
const chartManager = new DynamicChartManager();

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
});

function initializeCharts() {
    // Check if D3 is loaded
    if (typeof d3 === 'undefined') {
        loadLibrary('https://d3js.org/d3.v7.min.js', initializeCharts);
        return;
    }

    // Initialize performance trend with auto-refresh
    if (document.getElementById('performance-trend-chart')) {
        loadPerformanceChart();
    }

    // Initialize complexity heatmap with auto-refresh
    if (document.getElementById('complexity-heatmap')) {
        loadComplexityHeatmap();
    }

    // Initialize animated leaderboard with auto-refresh
    if (document.getElementById('animated-leaderboard')) {
        loadLeaderboard();
    }

    // Add refresh button listeners
    setupRefreshButtons();
}

async function loadPerformanceChart() {
    const container = document.getElementById('performance-trend-chart');
    showLoadingState(container);

    try {
        const response = await fetch('/api/dashboard/performance-data');
        const data = await response.json();
        const chart = new PerformanceTrendChart('performance-trend-chart', data.trend || getDemoData());

        // Add refresh method
        chart.refresh = async function () {
            const response = await fetch('/api/dashboard/performance-data');
            const newData = await response.json();
            this.data = newData.trend || getDemoData();
            this.render();
        };

        chartManager.registerChart('performance-trend', chart, 60000); // Refresh every 60s
    } catch (error) {
        console.warn('Using demo data for performance chart:', error);
        const chart = new PerformanceTrendChart('performance-trend-chart', getDemoData());
        chartManager.registerChart('performance-trend', chart, 0); // No auto-refresh for demo
    }
}

async function loadComplexityHeatmap() {
    const container = document.getElementById('complexity-heatmap');
    showLoadingState(container);

    try {
        const response = await fetch('/api/dashboard/complexity-data');
        const data = await response.json();
        const chart = new ComplexityHeatmap('complexity-heatmap', data.complexity || getComplexityData());

        chart.refresh = async function () {
            const response = await fetch('/api/dashboard/complexity-data');
            const newData = await response.json();
            this.data = newData.complexity || getComplexityData();
            this.render();
        };

        chartManager.registerChart('complexity-heatmap', chart, 120000); // Refresh every 2 min
    } catch (error) {
        console.warn('Using demo data for complexity heatmap:', error);
        const chart = new ComplexityHeatmap('complexity-heatmap', getComplexityData());
        chartManager.registerChart('complexity-heatmap', chart, 0);
    }
}

async function loadLeaderboard() {
    const container = document.getElementById('animated-leaderboard');
    showLoadingState(container);

    try {
        const response = await fetch('/api/gamification/leaderboard');
        const data = await response.json();
        const chart = new AnimatedLeaderboard('animated-leaderboard', data.data || getLeaderboardDemo());

        chart.refresh = async function () {
            const response = await fetch('/api/gamification/leaderboard');
            const newData = await response.json();
            this.data = newData.data || getLeaderboardDemo();
            this.init();
        };

        chartManager.registerChart('leaderboard', chart, 30000); // Refresh every 30s
    } catch (error) {
        console.warn('Using demo data for leaderboard:', error);
        const chart = new AnimatedLeaderboard('animated-leaderboard', getLeaderboardDemo());
        chartManager.registerChart('leaderboard', chart, 0);
    }
}

function setupRefreshButtons() {
    document.querySelectorAll('[data-refresh-chart]').forEach(button => {
        button.addEventListener('click', () => {
            const chartId = button.dataset.refreshChart;
            chartManager.refreshChart(chartId);

            // Visual feedback
            button.classList.add('refreshing');
            setTimeout(() => button.classList.remove('refreshing'), 1000);
        });
    });
}

function showLoadingState(container) {
    const loadingHTML = `
        <div class="chart-loading">
            <div class="spinner"></div>
            <p>Loading chart data...</p>
        </div>
    `;
    container.innerHTML = loadingHTML;
}

// Demo data generators
function getDemoData() {
    const data = [];
    const now = new Date();
    for (let i = 10; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i * 3);
        data.push({
            date: date.toISOString(),
            score: 60 + Math.random() * 35,
            assignment: `Assignment ${10 - i}`
        });
    }
    return data;
}

function getComplexityData() {
    const assignments = ['Factorial', 'Fibonacci', 'Binary Search', 'Sorting'];
    const metrics = ['Complexity', 'Best Practices', 'Performance'];
    const data = [];

    assignments.forEach(assignment => {
        metrics.forEach(metric => {
            data.push({
                assignment,
                metric,
                value: 20 + Math.random() * 80
            });
        });
    });

    return data;
}

function getLeaderboardDemo() {
    return [
        { name: 'Alice Johnson', points: 2450, submissions: 15 },
        { name: 'Bob Smith', points: 2100, submissions: 14 },
        { name: 'Carol White', points: 1980, submissions: 13 },
        { name: 'David Brown', points: 1750, submissions: 12 },
        { name: 'Eve Davis', points: 1620, submissions: 11 }
    ];
}

function loadLibrary(src, callback) {
    const script = document.createElement('script');
    script.src = src;
    script.onload = callback;
    document.head.appendChild(script);
}
