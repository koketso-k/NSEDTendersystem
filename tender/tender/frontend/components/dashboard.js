// components/dashboard.js
class DashboardComponent {
    static getHTML() {
        return `
            <div class="dashboard-section">
                <h1><i class="fas fa-home"></i> Dashboard</h1>
                <p class="text-center mt-2">Welcome to Tender Insight Hub - Your AI-powered procurement assistant</p>
                
                <div class="dashboard mt-3">
                    <div class="stats-card">
                        <i class="fas fa-search" style="color: #3498db;"></i>
                        <h3>Find Tenders</h3>
                        <p>Search and discover relevant opportunities using AI-powered filters</p>
                        <button class="btn btn-outline mt-2" id="quick-search">
                            <i class="fas fa-search"></i> Start Searching
                        </button>
                    </div>
                    
                    <div class="stats-card">
                        <i class="fas fa-briefcase" style="color: #27ae60;"></i>
                        <h3>My Workspace</h3>
                        <p>Manage your tender applications and track progress</p>
                        <button class="btn btn-outline mt-2" id="view-workspace">
                            <i class="fas fa-briefcase"></i> View Workspace
                        </button>
                    </div>
                    
                    <div class="stats-card">
                        <i class="fas fa-building" style="color: #e74c3c;"></i>
                        <h3>Company Profile</h3>
                        <p>Set up your business information for better matches</p>
                        <button class="btn btn-outline mt-2" id="setup-profile">
                            <i class="fas fa-building"></i> Setup Profile
                        </button>
                    </div>
                </div>

                <div class="results-section mt-3">
                    <h2><i class="fas fa-bullhorn"></i> Recent Tender Opportunities</h2>
                    <div id="recent-tenders" class="mt-2">
                        <div class="text-center" style="padding: 2rem; color: var(--light-text);">
                            <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                            <p>Loading recent tenders...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}