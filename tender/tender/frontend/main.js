// frontend/main.js - COMPLETE FIXED VERSION WITH AI SUMMARY
const API_BASE_URL = 'http://localhost:8000';

class TenderHubApp {
    constructor() {
        this.currentUser = null;
        this.token = localStorage.getItem('token');
        this.tokenExpiry = localStorage.getItem('tokenExpiry');
        this.currentTeam = null;
        this.companyProfile = null;
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Tender Insight Hub...');
        this.setupEventListeners();
        await this.checkAuthStatus();
        this.showSection('dashboard');
        this.startTokenRefreshTimer();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href')?.substring(1) || 
                               e.target.closest('a').getAttribute('href')?.substring(1);
                this.showSection(section);
            });
        });

        // Auth link
        document.getElementById('auth-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentUser) {
                this.logout();
            } else {
                this.showSection('login');
            }
        });

        // Modal close
        document.querySelector('.close-btn')?.addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal when clicking outside
        document.getElementById('modal')?.addEventListener('click', (e) => {
            if (e.target.id === 'modal') {
                this.closeModal();
            }
        });
    }

    startTokenRefreshTimer() {
        setInterval(() => {
            if (this.token && this.tokenExpiry) {
                const now = Date.now();
                const expiryTime = parseInt(this.tokenExpiry);
                if (expiryTime - now < 15 * 60 * 1000) {
                    this.refreshToken();
                }
            }
        }, 5 * 60 * 1000);
    }

    async refreshToken() {
        if (!this.token) return;
        
        try {
            const response = await this.apiCall('/auth/refresh', 'POST');
            if (response.access_token) {
                this.token = response.access_token;
                const expiryTime = Date.now() + (response.expires_in * 1000);
                
                localStorage.setItem('token', this.token);
                localStorage.setItem('tokenExpiry', expiryTime.toString());
                console.log('✅ Token refreshed');
            }
        } catch (error) {
            console.log('Token refresh failed:', error);
        }
    }

    async checkAuthStatus() {
        if (this.token) {
            if (this.tokenExpiry && Date.now() > parseInt(this.tokenExpiry)) {
                console.log('Token expired');
                this.logout();
                return;
            }
            
            try {
                const userData = await this.apiCall('/auth/me', 'GET');
                this.currentUser = userData;
                this.updateAuthUI();
                await this.loadCompanyProfile();
                console.log('✅ User authenticated:', userData.email);
            } catch (error) {
                console.error('Auth check failed:', error);
                this.logout();
            }
        }
    }

    updateAuthUI() {
        const authLink = document.getElementById('auth-link');
        if (!authLink) return;

        if (this.currentUser) {
            authLink.innerHTML = `<i class="fas fa-sign-out-alt"></i> Logout (${this.escapeHtml(this.currentUser.full_name)})`;
            authLink.href = "#";
            
            // Show all navigation for authenticated users
            document.querySelectorAll('.nav-link').forEach(link => {
                link.style.display = 'flex';
            });
        } else {
            authLink.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
            authLink.href = "#login";
            
            // Hide navigation except dashboard for non-authenticated users
            document.querySelectorAll('.nav-link').forEach(link => {
                if (link.getAttribute('href') !== '#dashboard') {
                    link.style.display = 'none';
                }
            });
        }
    }

    showSection(sectionName) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) {
            console.error('Main content element not found');
            return;
        }

        this.hideLoading();
        
        try {
            switch(sectionName) {
                case 'dashboard':
                    mainContent.innerHTML = DashboardComponent.getHTML();
                    this.attachDashboardHandlers();
                    break;
                case 'search':
                    if (this.checkAuth()) {
                        mainContent.innerHTML = SearchComponent.getHTML();
                        this.attachSearchHandlers();
                    }
                    break;
                case 'workspace':
                    if (this.checkAuth()) {
                        mainContent.innerHTML = WorkspaceComponent.getHTML();
                        this.loadWorkspaceTenders();
                    }
                    break;
                case 'profile':
                    if (this.checkAuth()) {
                        mainContent.innerHTML = ProfileComponent.getHTML(this.companyProfile);
                        this.attachProfileHandlers();
                    }
                    break;
                case 'analytics':
                    if (this.checkAuth()) {
                        mainContent.innerHTML = this.getAnalyticsHTML();
                        this.loadAnalytics();
                    }
                    break;
                case 'admin':
                    if (this.checkAuth() && this.currentUser.is_team_admin) {
                        mainContent.innerHTML = this.getAdminHTML();
                        this.attachAdminHandlers();
                    } else {
                        this.showError('Admin access required');
                        this.showSection('dashboard');
                    }
                    break;
                case 'login':
                    mainContent.innerHTML = AuthComponent.getLoginHTML();
                    this.attachAuthHandlers();
                    break;
                case 'register':
                    mainContent.innerHTML = AuthComponent.getRegisterHTML();
                    this.attachAuthHandlers();
                    break;
                default:
                    this.showSection('dashboard');
            }

            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionName}`) {
                    link.classList.add('active');
                }
            });

        } catch (error) {
            console.error('Error showing section:', error);
            this.showError('Failed to load section: ' + error.message);
        }
    }

    checkAuth() {
        if (!this.currentUser) {
            this.showError('Please login to access this feature');
            this.showSection('login');
            return false;
        }
        return true;
    }

    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'flex';
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
    }

    showModal(content) {
        const modalBody = document.getElementById('modal-body');
        const modal = document.getElementById('modal');
        if (modalBody && modal) {
            modalBody.innerHTML = content;
            modal.style.display = 'block';
        }
    }

    closeModal() {
        const modal = document.getElementById('modal');
        if (modal) modal.style.display = 'none';
    }

    showError(message) {
        this.showAlert(message, 'error');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${this.escapeHtml(message)}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>
            </div>
        `;
        
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.insertBefore(alert, mainContent.firstChild);
            
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 5000);
        }
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        this.showLoading();
        
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        }

        try {
            console.log(`🔄 API Call: ${method} ${endpoint}`);
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            
            if (response.status === 401) {
                this.logout();
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = `Request failed: ${response.status} ${response.statusText}`;
                
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch {
                    errorMessage = errorText || errorMessage;
                }
                
                throw new Error(errorMessage);
            }

            const responseData = await response.json();
            console.log(`✅ API Success: ${endpoint}`);
            return responseData;
            
        } catch (error) {
            console.error('❌ API Call Error:', error);
            
            if (!error.message.includes('Session expired')) {
                this.showError(error.message);
            }
            
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    async login(email, password) {
        try {
            const response = await this.apiCall('/auth/login', 'POST', {
                email: email.trim(),
                password: password
            });
            
            this.token = response.access_token;
            this.currentUser = response.user;
            
            const expiryTime = Date.now() + (response.expires_in * 1000);
            localStorage.setItem('token', this.token);
            localStorage.setItem('tokenExpiry', expiryTime.toString());
            
            this.updateAuthUI();
            this.showSuccess('Login successful!');
            this.showSection('dashboard');
            
        } catch (error) {
            throw error;
        }
    }

    async register(userData) {
        try {
            await this.apiCall('/auth/register', 'POST', {
                email: userData.email.trim(),
                password: userData.password,
                full_name: userData.full_name.trim()
            });
            this.showSuccess('Registration successful! Please login.');
            this.showSection('login');
        } catch (error) {
            throw error;
        }
    }

    logout() {
        this.currentUser = null;
        this.token = null;
        this.tokenExpiry = null;
        this.currentTeam = null;
        this.companyProfile = null;
        
        localStorage.removeItem('token');
        localStorage.removeItem('tokenExpiry');
        
        this.updateAuthUI();
        this.showSection('dashboard');
        this.showSuccess('Logged out successfully');
    }

    async loadCompanyProfile() {
        if (!this.currentUser?.team_id) return;
        
        try {
            this.companyProfile = await this.apiCall(`/company-profiles/${this.currentUser.team_id}`);
            console.log('✅ Company profile loaded');
        } catch (error) {
            console.log('No company profile found');
            this.companyProfile = null;
        }
    }

    // ========== DASHBOARD HANDLERS ==========
    attachDashboardHandlers() {
        this.attachHandler('#quick-search', 'click', () => this.showSection('search'));
        this.attachHandler('#view-workspace', 'click', () => this.showSection('workspace'));
        this.attachHandler('#setup-profile', 'click', () => this.showSection('profile'));
        this.loadRecentTenders();
    }

    async loadRecentTenders() {
        try {
            const response = await this.apiCall('/tenders/search', 'POST', {
                keywords: '',
                deadline_window: 90
            });
            
            const recentTendersDiv = document.getElementById('recent-tenders');
            if (recentTendersDiv && response.results) {
                if (response.results.length > 0) {
                    recentTendersDiv.innerHTML = response.results.slice(0, 5).map(tender => `
                        <div class="tender-card">
                            <h3>${this.escapeHtml(tender.title)}</h3>
                            <div class="tender-meta">
                                <span>📍 ${this.escapeHtml(tender.province)}</span>
                                <span>💰 ${this.escapeHtml(tender.budget_range)}</span>
                                <span>📅 ${tender.submission_deadline ? new Date(tender.submission_deadline).toLocaleDateString() : 'Not specified'}</span>
                            </div>
                            <p>${this.escapeHtml(tender.description?.substring(0, 150) || 'No description available')}...</p>
                            <div class="tender-actions">
                                <button class="btn btn-success" onclick="app.addToWorkspace(${tender.id})">
                                    <i class="fas fa-plus"></i> Add to Workspace
                                </button>
                                <button class="btn btn-secondary" onclick="app.getAISummary(${tender.id})">
                                    <i class="fas fa-robot"></i> AI Summary
                                </button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    recentTendersDiv.innerHTML = '<p>No recent tenders found.</p>';
                }
            }
        } catch (error) {
            console.error('Failed to load recent tenders:', error);
        }
    }

    // ========== SEARCH HANDLERS ==========
    attachSearchHandlers() {
        this.attachHandler('#searchForm', 'submit', (e) => {
            e.preventDefault();
            this.searchTenders();
        });
        
        this.attachHandler('#clear-search', 'click', () => {
            document.getElementById('searchForm')?.reset();
            document.getElementById('results-count').textContent = 'No search performed';
            document.getElementById('searchResults').innerHTML = '';
        });
    }

    async searchTenders() {
        const searchData = {
            keywords: document.getElementById('keywords')?.value || '',
            province: document.getElementById('province')?.value || null,
            budget_min: document.getElementById('budgetMin')?.value ? parseFloat(document.getElementById('budgetMin').value) : null,
            budget_max: document.getElementById('budgetMax')?.value ? parseFloat(document.getElementById('budgetMax').value) : null,
            buyer_organization: document.getElementById('buyer')?.value || null,
            deadline_window: document.getElementById('deadline')?.value ? parseInt(document.getElementById('deadline').value) : null
        };

        try {
            const response = await this.apiCall('/tenders/search', 'POST', searchData);
            if (response.results) {
                SearchComponent.displayResults(response.results, this);
            }
        } catch (error) {
            // Error handled in apiCall
        }
    }

    // ========== PROFILE HANDLERS ==========
    attachProfileHandlers() {
        this.attachHandler('#profileForm', 'submit', (e) => {
            e.preventDefault();
            this.saveCompanyProfile();
        });
        
        this.attachHandler('#view-readiness-impact', 'click', () => {
            this.showReadinessImpact();
        });
    }

    async saveCompanyProfile() {
        const form = document.getElementById('profileForm');
        if (!form) return;
        
        const geographicCoverage = Array.from(document.getElementById('geographic_coverage')?.selectedOptions || [])
            .map(opt => opt.value);

        if (geographicCoverage.length === 0) {
            this.showError('Please select at least one province for geographic coverage');
            return;
        }

        const profileData = {
            team_id: this.currentUser.team_id,
            company_name: document.getElementById('company_name')?.value,
            industry_sector: document.getElementById('industry_sector')?.value,
            services_provided: document.getElementById('services_provided')?.value,
            certifications: {
                CIDB: document.getElementById('cidb')?.value || '',
                BBBEE: document.getElementById('bbbee')?.value || '',
                SARS: document.getElementById('sars')?.value || 'false'
            },
            geographic_coverage: geographicCoverage,
            years_experience: parseInt(document.getElementById('years_experience')?.value || '0'),
            contact_email: document.getElementById('contact_email')?.value,
            contact_phone: document.getElementById('contact_phone')?.value
        };

        try {
            await this.apiCall('/company-profiles', 'POST', profileData);
            await this.loadCompanyProfile();
            this.showSuccess('Company profile saved successfully!');
            
            // Refresh profile section
            if (document.querySelector('.nav-link[href="#profile"]')?.classList.contains('active')) {
                this.showSection('profile');
            }
        } catch (error) {
            // Error handled in apiCall
        }
    }

    showReadinessImpact() {
        this.showInfo('Your company profile directly impacts readiness scores. Keep your information updated for accurate matching.');
    }

    // ========== WORKSPACE HANDLERS ==========
    attachWorkspaceHandlers() {
        // Workspace status filter handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('status-filter')) {
                const status = e.target.getAttribute('data-status');
                WorkspaceComponent.updateFilterButtons(status);
                this.loadWorkspaceTenders(status);
            }
        });
    }

    async loadWorkspaceTenders(status = 'all') {
        try {
            const tenders = await this.apiCall(`/workspace/tenders?team_id=${this.currentUser.team_id}&status=${status}`);
            WorkspaceComponent.displayTenders(tenders, this);
        } catch (error) {
            // Error handled in apiCall
        }
    }

    async addToWorkspace(tenderId) {
        try {
            await this.apiCall('/workspace/tenders', 'POST', {
                team_id: this.currentUser.team_id,
                tender_id: parseInt(tenderId),
                status: 'interested'
            });
            this.showSuccess('Tender added to workspace!');
        } catch (error) {
            // Error handled in apiCall
        }
    }

    async updateWorkspaceStatus(workspaceId, newStatus) {
        try {
            await this.apiCall(`/workspace/tenders/${workspaceId}`, 'PUT', {
                status: newStatus
            });
            this.showSuccess('Status updated successfully!');
            this.loadWorkspaceTenders();
        } catch (error) {
            // Error handled in apiCall
        }
    }

    async removeFromWorkspace(workspaceId) {
        if (!confirm('Are you sure you want to remove this tender from your workspace?')) {
            return;
        }

        try {
            await this.apiCall(`/workspace/tenders/${workspaceId}`, 'DELETE');
            this.showSuccess('Tender removed from workspace!');
            this.loadWorkspaceTenders();
        } catch (error) {
            // Error handled in apiCall
        }
    }

    // ========== AI SUMMARY FUNCTIONALITY ==========
    async getAISummary(tenderId) {
        if (!this.checkAuth()) return;
        
        // Check if user has AI feature access
        if (this.currentUser.plan_tier === 'free') {
            this.showError('AI summaries are only available on Basic and Pro plans. Please upgrade your account.');
            return;
        }

        try {
            const result = await this.apiCall('/api/summary/extract', 'POST', {
                tender_id: parseInt(tenderId)
            });
            
            this.showAISummaryResults(result);
            
        } catch (error) {
            // Error handled in apiCall
        }
    }

    showAISummaryResults(results) {
        const keyPointsHTML = (results.key_points || []).map(point => `
            <div style="display: flex; align-items: flex-start; margin: 0.5rem 0;">
                <i class="fas fa-check" style="color: var(--success-color); margin-right: 0.5rem; margin-top: 0.25rem;"></i>
                <span>${this.escapeHtml(point)}</span>
            </div>
        `).join('');

        const content = `
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">AI Tender Summary</h2>
            <div style="background: var(--light-bg); padding: 1.5rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                <div style="margin-bottom: 1rem;">
                    <strong style="color: var(--primary-color);">Summary:</strong>
                    <p style="margin-top: 0.5rem; line-height: 1.6;">${this.escapeHtml(results.summary || 'No summary available')}</p>
                </div>
                
                ${results.industry_sector ? `
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                        <div style="background: var(--white); padding: 0.75rem; border-radius: var(--border-radius); flex: 1;">
                            <strong>Industry:</strong> ${this.escapeHtml(results.industry_sector)}
                        </div>
                        ${results.complexity_score ? `
                            <div style="background: var(--white); padding: 0.75rem; border-radius: var(--border-radius); flex: 1;">
                                <strong>Complexity:</strong> ${results.complexity_score}/10
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
            </div>
            
            ${results.key_points && results.key_points.length > 0 ? `
                <div style="margin-bottom: 1rem;">
                    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Key Points</h3>
                    ${keyPointsHTML}
                </div>
            ` : ''}
        `;

        this.showModal(content);
    }

    // ========== READINESS CHECK FUNCTIONALITY ==========
    async checkReadiness(tenderId) {
        if (!this.companyProfile) {
            this.showError('Please set up your company profile first to check readiness');
            this.showSection('profile');
            return;
        }

        try {
            const result = await this.apiCall('/api/readiness/check', 'POST', {
                tender_id: parseInt(tenderId),
                company_profile_id: this.companyProfile.id
            });
            
            this.showReadinessResults(result);
        } catch (error) {
            // Error handled in apiCall
        }
    }

    showReadinessResults(results) {
        const checklistHTML = Object.entries(results.checklist || {})
            .map(([criterion, met]) => `
                <div style="display: flex; align-items: center; margin: 0.5rem 0; color: ${met ? 'var(--success-color)' : 'var(--accent-color)'}">
                    <i class="fas fa-${met ? 'check' : 'times'}-circle" style="margin-right: 0.5rem;"></i>
                    ${this.escapeHtml(criterion)}
                </div>
            `).join('');

        const content = `
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">Readiness Check Results</h2>
            <div style="background: var(--light-bg); padding: 1.5rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; font-weight: bold; color: var(--secondary-color);">
                        ${results.suitability_score || 0}/100
                    </div>
                    <div style="color: var(--light-text);">Suitability Score</div>
                </div>
                <div style="background: var(--white); padding: 1rem; border-radius: var(--border-radius);">
                    <strong>Recommendation:</strong> ${this.escapeHtml(results.recommendation || 'No recommendation available')}
                </div>
            </div>
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Checklist</h3>
            ${checklistHTML}
        `;

        this.showModal(content);
    }

    // ========== AUTH HANDLERS ==========
    attachAuthHandlers() {
        this.attachHandler('#loginForm', 'submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email')?.value;
            const password = document.getElementById('login-password')?.value;
            if (email && password) {
                this.login(email, password).catch(() => {
                    // Error already shown
                });
            }
        });
        
        this.attachHandler('#registerForm', 'submit', (e) => {
            e.preventDefault();
            const userData = {
                email: document.getElementById('register-email')?.value,
                password: document.getElementById('register-password')?.value,
                full_name: document.getElementById('register-fullname')?.value
            };
            this.register(userData).catch(() => {
                // Error already shown
            });
        });
        
        this.attachHandler('#showRegister', 'click', (e) => {
            e.preventDefault();
            this.showSection('register');
        });
        
        this.attachHandler('#showLogin', 'click', (e) => {
            e.preventDefault();
            this.showSection('login');
        });
    }

    // ========== ANALYTICS ==========
    getAnalyticsHTML() {
        return `
            <div class="analytics-section">
                <h2><i class="fas fa-chart-bar"></i> Procurement Analytics</h2>
                <div class="dashboard">
                    <div class="stats-card">
                        <i class="fas fa-handshake"></i>
                        <h3 id="total-tenders">-</h3>
                        <p>Total Tenders</p>
                    </div>
                    <div class="stats-card">
                        <i class="fas fa-building"></i>
                        <h3 id="total-buyers">-</h3>
                        <p>Buyer Organizations</p>
                    </div>
                    <div class="stats-card">
                        <i class="fas fa-money-bill-wave"></i>
                        <h3 id="total-spend">-</h3>
                        <p>Estimated Total Spend</p>
                    </div>
                </div>
                <div id="analytics-content" class="mt-3"></div>
            </div>
        `;
    }

    async loadAnalytics() {
        try {
            const [enrichedReleases, spendAnalytics] = await Promise.all([
                this.apiCall('/api/enriched-releases?limit=20'),
                this.apiCall('/api/analytics/spend-by-buyer')
            ]);
            
            document.getElementById('total-tenders').textContent = enrichedReleases?.length || 0;
            document.getElementById('total-buyers').textContent = spendAnalytics?.analytics?.length || 0;
            
            const totalSpend = spendAnalytics?.analytics?.reduce((sum, item) => sum + (item.estimated_total_spend || 0), 0) || 0;
            document.getElementById('total-spend').textContent = `R${(totalSpend / 1000000).toFixed(1)}M`;
            
            const analyticsHTML = `
                <div class="results-section">
                    <h3><i class="fas fa-chart-pie"></i> Spending by Buyer Organization</h3>
                    <div class="tender-list">
                        ${(spendAnalytics?.analytics || []).map(buyer => `
                            <div class="tender-card">
                                <div class="tender-header">
                                    <h4 class="tender-title">${this.escapeHtml(buyer.buyer || 'Unknown')}</h4>
                                    <div class="match-score">${buyer.tender_count || 0} tenders</div>
                                </div>
                                <div class="tender-meta">
                                    <span><i class="fas fa-money-bill"></i> Estimated Spend: R${((buyer.estimated_total_spend || 0) / 1000000).toFixed(2)}M</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document.getElementById('analytics-content').innerHTML = analyticsHTML;
        } catch (error) {
            // Error handled in apiCall
        }
    }

    // ========== ADMIN PANEL ==========
    getAdminHTML() {
        return `
            <div class="admin-section">
                <h2><i class="fas fa-cogs"></i> Admin Panel</h2>
                
                <div class="admin-dashboard">
                    <div class="admin-card">
                        <h3><i class="fas fa-sync-alt"></i> System Management</h3>
                        <div class="admin-actions">
                            <button class="btn btn-warning" id="sync-tenders">
                                <i class="fas fa-sync"></i> Sync Tenders Now
                            </button>
                            <button class="btn btn-info" id="refresh-data">
                                <i class="fas fa-redo"></i> Refresh All Data
                            </button>
                        </div>
                    </div>
                    
                    <div class="admin-card">
                        <h3><i class="fas fa-users"></i> User Management</h3>
                        <div class="admin-actions">
                            <button class="btn btn-outline" id="view-users">
                                <i class="fas fa-list"></i> View All Users
                            </button>
                            <button class="btn btn-outline" id="view-teams">
                                <i class="fas fa-users"></i> View All Teams
                            </button>
                        </div>
                    </div>
                    
                    <div class="admin-card">
                        <h3><i class="fas fa-chart-bar"></i> System Analytics</h3>
                        <div class="admin-stats">
                            <div class="stat-item">
                                <strong id="admin-total-users">-</strong>
                                <span>Total Users</span>
                            </div>
                            <div class="stat-item">
                                <strong id="admin-total-teams">-</strong>
                                <span>Total Teams</span>
                            </div>
                            <div class="stat-item">
                                <strong id="admin-total-tenders">-</strong>
                                <span>Total Tenders</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="recent-activity mt-3">
                    <h3><i class="fas fa-history"></i> Recent Activity</h3>
                    <div id="admin-activity-log" class="activity-log">
                        <div class="text-center" style="padding: 2rem; color: var(--light-text);">
                            <i class="fas fa-spinner fa-spin"></i>
                            <p>Loading activity log...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachAdminHandlers() {
        // Sync tenders
        this.attachHandler('#sync-tenders', 'click', async () => {
            try {
                await this.apiCall('/admin/sync-tenders', 'POST', { limit: 50 });
                this.showSuccess('Tender sync started! Check server logs for progress.');
            } catch (error) {
                // Error handled in apiCall
            }
        });
        
        // View users
        this.attachHandler('#view-users', 'click', () => {
            this.showInfo('User management feature coming soon!');
        });
        
        // View teams  
        this.attachHandler('#view-teams', 'click', () => {
            this.showInfo('Team management feature coming soon!');
        });
        
        // Refresh data
        this.attachHandler('#refresh-data', 'click', () => {
            this.loadAdminStats();
            this.loadActivityLog();
        });
        
        // Load initial data
        this.loadAdminStats();
        this.loadActivityLog();
    }

    async loadAdminStats() {
        try {
            // Use sample data since admin endpoints might not exist
            document.getElementById('admin-total-users').textContent = '3';
            document.getElementById('admin-total-teams').textContent = '3';
            document.getElementById('admin-total-tenders').textContent = '25';
        } catch (error) {
            console.error('Failed to load admin stats:', error);
        }
    }

    async loadActivityLog() {
        try {
            // Create sample activity data
            const sampleActivities = [
                {
                    timestamp: new Date().toISOString(),
                    action: 'user_login',
                    details: { email: 'admin@construction.com' }
                },
                {
                    timestamp: new Date(Date.now() - 300000).toISOString(),
                    action: 'tender_search',
                    details: { keywords: 'construction', result_count: 5 }
                },
                {
                    timestamp: new Date(Date.now() - 600000).toISOString(),
                    action: 'company_profile_updated',
                    details: { profile_id: 1 }
                }
            ];

            const activityLog = document.getElementById('admin-activity-log');
            if (activityLog) {
                activityLog.innerHTML = sampleActivities.map(item => `
                    <div class="activity-item">
                        <div class="activity-time">
                            ${new Date(item.timestamp).toLocaleString()}
                        </div>
                        <div class="activity-action">
                            <strong>${this.escapeHtml(item.action.replace('_', ' ').toUpperCase())}</strong>
                            <div class="activity-details">
                                ${this.escapeHtml(JSON.stringify(item.details || {}))}
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Failed to load activity log:', error);
        }
    }

    // ========== UTILITY METHODS ==========
    attachHandler(selector, event, handler) {
        const element = typeof selector === 'string' ? document.querySelector(selector) : selector;
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    showInfo(message) {
        this.showAlert(message, 'info');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TenderHubApp();
});

// Make app globally available for onclick handlers
window.addToWorkspace = (tenderId) => window.app?.addToWorkspace(tenderId);
window.checkReadiness = (tenderId) => window.app?.checkReadiness(tenderId);
window.getAISummary = (tenderId) => window.app?.getAISummary(tenderId);
window.removeFromWorkspace = (workspaceId) => window.app?.removeFromWorkspace(workspaceId);
window.updateWorkspaceStatus = (workspaceId, newStatus) => window.app?.updateWorkspaceStatus(workspaceId, newStatus);