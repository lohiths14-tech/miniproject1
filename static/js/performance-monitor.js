/**
 * Performance Monitoring Utility
 * Tracks page load, API calls, and chart rendering performance
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoad: null,
            apiCalls: [],
            chartRenders: [],
            errors: []
        };
        this.init();
    }

    init() {
        // Monitor page load performance
        if (window.performance && window.performance.timing) {
            window.addEventListener('load', () => {
                setTimeout(() => this.capturePageLoadMetrics(), 0);
            });
        }

        // Monitor API calls
        this.interceptFetch();

        // Monitor errors
        window.addEventListener('error', (event) => {
            this.logError(event.error);
        });
    }

    capturePageLoadMetrics() {
        const timing = window.performance.timing;
        const navigation = window.performance.navigation;

        this.metrics.pageLoad = {
            // DNS lookup time
            dns: timing.domainLookupEnd - timing.domainLookupStart,

            // TCP connection time
            tcp: timing.connectEnd - timing.connectStart,

            // Request time
            request: timing.responseStart - timing.requestStart,

            // Response time
            response: timing.responseEnd - timing.responseStart,

            // DOM processing time
            domProcessing: timing.domComplete - timing.domLoading,

            // Total page load time
            total: timing.loadEventEnd - timing.navigationStart,

            // Time to first byte
            ttfb: timing.responseStart - timing.navigationStart,

            // DOM content loaded
            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,

            // Navigation type
            navigationType: this.getNavigationType(navigation.type)
        };

        this.reportMetrics();
    }

    getNavigationType(type) {
        const types = {
            0: 'navigate',
            1: 'reload',
            2: 'back_forward',
            255: 'reserved'
        };
        return types[type] || 'unknown';
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        const self = this;

        window.fetch = function (...args) {
            const startTime = performance.now();
            const url = args[0];

            return originalFetch.apply(this, args)
                .then(response => {
                    const endTime = performance.now();
                    const duration = endTime - startTime;

                    self.logApiCall({
                        url,
                        method: args[1]?.method || 'GET',
                        status: response.status,
                        duration,
                        timestamp: new Date().toISOString()
                    });

                    return response;
                })
                .catch(error => {
                    const endTime = performance.now();
                    const duration = endTime - startTime;

                    self.logApiCall({
                        url,
                        method: args[1]?.method || 'GET',
                        status: 'error',
                        duration,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });

                    throw error;
                });
        };
    }

    logApiCall(data) {
        this.metrics.apiCalls.push(data);

        // Keep only last 50 API calls
        if (this.metrics.apiCalls.length > 50) {
            this.metrics.apiCalls.shift();
        }

        // Log slow API calls (> 1 second)
        if (data.duration > 1000) {
            console.warn(`Slow API call detected: ${data.url} took ${data.duration.toFixed(2)}ms`);
        }
    }

    logChartRender(chartId, duration) {
        this.metrics.chartRenders.push({
            chartId,
            duration,
            timestamp: new Date().toISOString()
        });

        // Keep only last 20 chart renders
        if (this.metrics.chartRenders.length > 20) {
            this.metrics.chartRenders.shift();
        }
    }

    logError(error) {
        this.metrics.errors.push({
            message: error?.message || 'Unknown error',
            stack: error?.stack,
            timestamp: new Date().toISOString()
        });

        // Keep only last 10 errors
        if (this.metrics.errors.length > 10) {
            this.metrics.errors.shift();
        }
    }

    getMetrics() {
        return {
            ...this.metrics,
            summary: this.getSummary()
        };
    }

    getSummary() {
        const apiCalls = this.metrics.apiCalls;
        const chartRenders = this.metrics.chartRenders;

        return {
            pageLoad: this.metrics.pageLoad?.total || 0,
            apiCalls: {
                total: apiCalls.length,
                avgDuration: apiCalls.length > 0
                    ? apiCalls.reduce((sum, call) => sum + call.duration, 0) / apiCalls.length
                    : 0,
                errors: apiCalls.filter(call => call.status === 'error').length
            },
            chartRenders: {
                total: chartRenders.length,
                avgDuration: chartRenders.length > 0
                    ? chartRenders.reduce((sum, render) => sum + render.duration, 0) / chartRenders.length
                    : 0
            },
            errors: this.metrics.errors.length
        };
    }

    reportMetrics() {
        const summary = this.getSummary();

        console.group('📊 Performance Metrics');
        console.log('Page Load:', `${summary.pageLoad}ms`);
        console.log('API Calls:', summary.apiCalls.total, `(avg: ${summary.apiCalls.avgDuration.toFixed(2)}ms)`);
        console.log('Chart Renders:', summary.chartRenders.total, `(avg: ${summary.chartRenders.avgDuration.toFixed(2)}ms)`);
        console.log('Errors:', summary.errors);
        console.groupEnd();

        // Send to analytics if available
        if (window.gtag) {
            window.gtag('event', 'performance', {
                page_load: summary.pageLoad,
                api_avg_duration: summary.apiCalls.avgDuration,
                chart_avg_duration: summary.chartRenders.avgDuration
            });
        }
    }

    // Public method to display metrics in UI
    displayMetrics(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const summary = this.getSummary();
        const metrics = this.getMetrics();

        container.innerHTML = `
            <div class="performance-dashboard">
                <h3>Performance Metrics</h3>

                <div class="metric-card">
                    <div class="metric-label">Page Load Time</div>
                    <div class="metric-value">${summary.pageLoad}ms</div>
                    <div class="metric-status ${summary.pageLoad < 3000 ? 'good' : 'warning'}">
                        ${summary.pageLoad < 3000 ? '✓ Good' : '⚠ Slow'}
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">API Calls</div>
                    <div class="metric-value">${summary.apiCalls.total}</div>
                    <div class="metric-detail">
                        Avg: ${summary.apiCalls.avgDuration.toFixed(2)}ms<br>
                        Errors: ${summary.apiCalls.errors}
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Chart Renders</div>
                    <div class="metric-value">${summary.chartRenders.total}</div>
                    <div class="metric-detail">
                        Avg: ${summary.chartRenders.avgDuration.toFixed(2)}ms
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">Errors</div>
                    <div class="metric-value ${summary.errors > 0 ? 'error' : 'success'}">
                        ${summary.errors}
                    </div>
                </div>
            </div>
        `;
    }
}

// Initialize performance monitor
const performanceMonitor = new PerformanceMonitor();

// Expose to window for debugging
window.performanceMonitor = performanceMonitor;

// Add keyboard shortcut to view metrics (Ctrl+Shift+P)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        console.clear();
        performanceMonitor.reportMetrics();
        console.table(performanceMonitor.getMetrics().apiCalls);
    }
});
