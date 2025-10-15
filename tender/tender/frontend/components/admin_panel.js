// frontend/components/admin_panel.js - ADMIN PANEL COMPONENT
class AdminPanelComponent {
    static getHTML() {
        return `
            <div class="admin-section">
                <h2><i class="fas fa-cogs"></i> Admin Panel</h2>
                <p>System administration and management dashboard</p>
                
                <div class="admin-stats-grid">
                    <div class="admin-stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-info">
                            <h3 id="admin-total-users">0</h3>
                            <p>Total Users</p>
                        </div>
                    </div>
                    
                    <div class="admin-stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-building"></i>
                        </div>
                        <div class="stat-info">
                            <h3 id="admin-total-teams">0</h3>
                            <p>Total Teams</p>
                        </div>
                    </div>
                    
                    <div class="admin-stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-file-contract"></i>
                        </div>
                        <div class="stat-info">
                            <h3 id="admin-total-tenders">0</h3>
                            <p>Total Tenders</p>
                        </div>
                    </div>
                    
                    <div class="admin-stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <div class="stat-info">
                            <h3 id="admin-workspace-entries">0</h3>
                            <p>Workspace Entries</p>
                        </div>
                    </div>
                </div>

                <div class="admin-actions-section">
                    <div class="admin-action-card">
                        <h3><i class="fas fa-sync-alt"></i> Data Management</h3>
                        <div class="action-buttons">
                            <button class="btn btn-warning" id="admin-sync-tenders">
                                <i class="fas fa-sync"></i> Sync Tenders
                            </button>
                            <button class="btn btn-info" id="admin-refresh-data">
                                <i class="fas fa-redo"></i> Refresh Stats
                            </button>
                        </div>
                    </div>
                    
                    <div class="admin-action-card">
                        <h3><i class="fas fa-chart-bar"></i> Analytics</h3>
                        <div class="action-buttons">
                            <button class="btn btn-outline" id="admin-view-analytics">
                                <i class="fas fa-chart-pie"></i> View Analytics
                            </button>
                            <button class="btn btn-outline" id="admin-export-data">
                                <i class="fas fa-download"></i> Export Data
                            </button>
                        </div>
                    </div>
                </div>

                <div class="recent-activity-section">
                    <h3><i class="fas fa-history"></i> Recent System Activity</h3>
                    <div id="admin-activity-list" class="activity-list">
                        <div class="loading-activity">
                            <i class="fas fa-spinner fa-spin"></i>
                            <p>Loading activity...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    static updateStats(stats) {
        if (!stats) return;
        
        // Update stat cards
        document.getElementById('admin-total-users').textContent = stats.users || 0;
        document.getElementById('admin-total-teams').textContent = stats.teams || 0;
        document.getElementById('admin-total-tenders').textContent = stats.tenders || 0;
        document.getElementById('admin-workspace-entries').textContent = stats.workspace_entries || 0;
    }

    static updateActivityLog(activities) {
        const activityList = document.getElementById('admin-activity-list');
        if (!activityList) return;
        
        if (!activities || activities.length === 0) {
            activityList.innerHTML = `
                <div class="no-activity">
                    <i class="fas fa-inbox"></i>
                    <p>No recent activity</p>
                </div>
            `;
            return;
        }
        
        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-user-circle"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-header">
                        <strong>${AdminPanelComponent.escapeHtml(activity.user_name || 'System')}</strong>
                        <span class="activity-time">${new Date(activity.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="activity-action">
                        ${AdminPanelComponent.escapeHtml(activity.action || 'Performed action')}
                    </div>
                    ${activity.details ? `
                        <div class="activity-details">
                            ${AdminPanelComponent.escapeHtml(JSON.stringify(activity.details))}
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    static attachHandlers(app) {
        // Sync tenders
        document.getElementById('admin-sync-tenders')?.addEventListener('click', () => {
            app.syncTenders();
        });
        
        // Refresh data
        document.getElementById('admin-refresh-data')?.addEventListener('click', () => {
            app.loadAdminStats();
            app.loadActivityLog();
        });
        
        // View analytics
        document.getElementById('admin-view-analytics')?.addEventListener('click', () => {
            app.showSection('analytics');
        });
        
        // Export data
        document.getElementById('admin-export-data')?.addEventListener('click', () => {
            app.exportData();
        });
    }

    static escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}