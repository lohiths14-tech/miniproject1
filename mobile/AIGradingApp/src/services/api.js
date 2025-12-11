import axios from 'axios';

const API_BASE_URL = __DEV__
    ? 'http://localhost:5000'  // Development
    : 'https://your-production-url.com';  // Production

// API version prefix
const API_VERSION = '/api/v1';

class ApiService {
    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
                'API-Version': '1'  // Version header for negotiation
            }
        });

        // Request interceptor
        this.client.interceptors.request.use(
            config => {
                console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        // Response interceptor
        this.client.interceptors.response.use(
            response => response,
            error => {
                if (error.response?.status === 401) {
                    // Handle unauthorized - maybe redirect to login
                    console.log('Unauthorized - redirecting to login');
                }
                return Promise.reject(error);
            }
        );
    }

    setAuthToken(token) {
        if (token) {
            this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.client.defaults.headers.common['Authorization'];
        }
    }

    // ==================== Auth Endpoints ====================

    async login(email, password) {
        return this.client.post(`${API_VERSION}/auth/login`, { email, password });
    }

    async signup(data) {
        return this.client.post(`${API_VERSION}/auth/signup`, data);
    }

    async logout() {
        return this.client.post(`${API_VERSION}/auth/logout`);
    }

    async refreshToken() {
        return this.client.post(`${API_VERSION}/auth/refresh`);
    }

    async getProfile() {
        return this.client.get(`${API_VERSION}/auth/profile`);
    }

    async updateProfile(data) {
        return this.client.put(`${API_VERSION}/auth/profile`, data);
    }

    // ==================== Assignment Endpoints ====================

    async getAssignments(params = {}) {
        return this.client.get(`${API_VERSION}/assignments`, { params });
    }

    async getAssignment(id) {
        return this.client.get(`${API_VERSION}/assignments/${id}`);
    }

    async getAssignmentsByStatus(status) {
        return this.client.get(`${API_VERSION}/assignments`, { params: { status } });
    }

    // ==================== Submission Endpoints ====================

    async submitCode(assignmentId, code, language) {
        return this.client.post(`${API_VERSION}/submissions/submit`, {
            assignment_id: assignmentId,
            code,
            language
        });
    }

    async getMySubmissions(params = {}) {
        return this.client.get(`${API_VERSION}/submissions/my-submissions`, { params });
    }

    async getSubmission(id) {
        return this.client.get(`${API_VERSION}/submissions/${id}`);
    }

    async getSubmissionFeedback(id) {
        return this.client.get(`${API_VERSION}/submissions/${id}/feedback`);
    }

    // ==================== Gamification Endpoints ====================

    async getLeaderboard(params = {}) {
        return this.client.get(`${API_VERSION}/gamification/leaderboard`, { params });
    }

    async getMyAchievements() {
        return this.client.get(`${API_VERSION}/gamification/my-achievements`);
    }

    async getMyPoints() {
        return this.client.get(`${API_VERSION}/gamification/my-points`);
    }

    async getBadges() {
        return this.client.get(`${API_VERSION}/gamification/badges`);
    }

    async getMyBadges() {
        return this.client.get(`${API_VERSION}/gamification/my-badges`);
    }

    async getMyRank() {
        return this.client.get(`${API_VERSION}/gamification/my-rank`);
    }

    // ==================== Dashboard Endpoints ====================

    async getDashboardData() {
        return this.client.get(`${API_VERSION}/dashboard/student`);
    }

    async getStats() {
        return this.client.get(`${API_VERSION}/dashboard/stats`);
    }

    async getRecentActivity() {
        return this.client.get(`${API_VERSION}/dashboard/recent-activity`);
    }

    // ==================== Plagiarism Endpoints ====================

    async checkPlagiarism(submissionId) {
        return this.client.post(`${API_VERSION}/plagiarism/check`, {
            submission_id: submissionId
        });
    }

    async getPlagiarismReport(submissionId) {
        return this.client.get(`${API_VERSION}/plagiarism/report/${submissionId}`);
    }

    // ==================== Helper Methods ====================

    get(url, config) {
        return this.client.get(url, config);
    }

    post(url, data, config) {
        return this.client.post(url, data, config);
    }

    put(url, data, config) {
        return this.client.put(url, data, config);
    }

    patch(url, data, config) {
        return this.client.patch(url, data, config);
    }

    delete(url, config) {
        return this.client.delete(url, config);
    }
}

// Export singleton instance
const api = new ApiService();
export default api;

// Also export the class for testing purposes
export { ApiService };
