// components/workspace.js - COMPLETE WITH AI SUMMARY BUTTON
class WorkspaceComponent {
    static getHTML() {
        return `
            <div class="workspace-section">
                <h2><i class="fas fa-briefcase"></i> My Workspace</h2>
                <p>Manage your tender applications and track your progress</p>
                
                <div class="status-filters">
                    <button class="status-filter active" data-status="all">All Tenders</button>
                    <button class="status-filter" data-status="interested">Interested</button>
                    <button class="status-filter" data-status="pending">Pending</button>
                    <button class="status-filter" data-status="submitted">Submitted</button>
                    <button class="status-filter" data-status="not_eligible">Not Eligible</button>
                </div>
                
                <div class="workspace-stats" id="workspaceStats" style="display: none; margin-bottom: 1rem;">
                    <div class="stats-row">
                        <span class="stat-item"><strong id="totalCount">0</strong> Total</span>
                        <span class="stat-item"><strong id="interestedCount">0</strong> Interested</span>
                        <span class="stat-item"><strong id="submittedCount">0</strong> Submitted</span>
                        <span class="stat-item"><strong id="pendingCount">0</strong> Pending</span>
                    </div>
                </div>
                
                <div id="workspaceResults">
                    <div class="text-center" style="padding: 2rem; color: var(--light-text);">
                        <i class="fas fa-briefcase" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <h3>No tenders in workspace</h3>
                        <p>Add tenders from the search page to get started</p>
                    </div>
                </div>
            </div>
        `;
    }

    static displayTenders(tenders, app) {
        const resultsDiv = document.getElementById('workspaceResults');
        const statsDiv = document.getElementById('workspaceStats');
        
        if (!tenders || tenders.length === 0) {
            resultsDiv.innerHTML = `
                <div class="text-center" style="padding: 2rem; color: var(--light-text);">
                    <i class="fas fa-briefcase" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <h3>No tenders in workspace</h3>
                    <p>Add tenders from the search page to get started</p>
                </div>
            `;
            statsDiv.style.display = 'none';
            return;
        }

        // Calculate statistics
        const stats = {
            total: tenders.length,
            interested: tenders.filter(t => t.status === 'interested').length,
            submitted: tenders.filter(t => t.status === 'submitted').length,
            pending: tenders.filter(t => t.status === 'pending').length,
            not_eligible: tenders.filter(t => t.status === 'not_eligible').length
        };

        // Update statistics display
        document.getElementById('totalCount').textContent = stats.total;
        document.getElementById('interestedCount').textContent = stats.interested;
        document.getElementById('submittedCount').textContent = stats.submitted;
        document.getElementById('pendingCount').textContent = stats.pending;
        statsDiv.style.display = 'block';

        resultsDiv.innerHTML = tenders.map(wt => `
            <div class="tender-card" data-workspace-id="${wt.id}">
                <div class="tender-header">
                    <div style="flex: 1;">
                        <h3 class="tender-title">${this.escapeHtml(wt.tender.title)}</h3>
                        <div class="tender-meta">
                            <span><i class="fas fa-building"></i> ${this.escapeHtml(wt.tender.buyer_organization || 'Not specified')}</span>
                            <span><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(wt.tender.province || 'National')}</span>
                            <span><i class="fas fa-clock"></i> ${wt.tender.submission_deadline ? new Date(wt.tender.submission_deadline).toLocaleDateString() : 'Not specified'}</span>
                            <span class="status-badge" style="background: ${WorkspaceComponent.getStatusColor(wt.status)}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">
                                ${wt.status.replace('_', ' ').toUpperCase()}
                            </span>
                        </div>
                    </div>
                    ${wt.match_score ? `<div class="match-score">${Math.round(wt.match_score)}%</div>` : 
                    `<button class="btn btn-sm btn-info" onclick="app.checkReadiness(${wt.tender.id})" 
                        ${!app.companyProfile ? 'disabled' : ''}>
                        <i class="fas fa-chart-line"></i> Get Score
                    </button>`}
                </div>
                <p class="tender-description">${this.escapeHtml(wt.tender.description || 'No description available.')}</p>
                ${wt.notes ? `<div class="workspace-notes">
                    <strong>Notes:</strong> ${this.escapeHtml(wt.notes)}
                </div>` : ''}
                <div class="tender-actions">
                    <select class="status-select" data-workspace-id="${wt.id}">
                        <option value="pending" ${wt.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="interested" ${wt.status === 'interested' ? 'selected' : ''}>Interested</option>
                        <option value="submitted" ${wt.status === 'submitted' ? 'selected' : ''}>Submitted</option>
                        <option value="not_eligible" ${wt.status === 'not_eligible' ? 'selected' : ''}>Not Eligible</option>
                    </select>
                    <button class="btn btn-outline" onclick="app.checkReadiness(${wt.tender.id})" ${!app.companyProfile ? 'disabled title="Setup company profile first"' : ''}>
                        <i class="fas fa-chart-line"></i> Re-check Readiness
                    </button>
                    <button class="btn btn-secondary" onclick="app.getAISummary(${wt.tender.id})" ${app.currentUser?.plan_tier === 'free' ? 'disabled title="AI Summary not available on Free plan"' : ''}>
                        <i class="fas fa-robot"></i> AI Summary
                    </button>
                    ${wt.tender.source_url ? `
                        <a href="${wt.tender.source_url}" target="_blank" class="btn btn-outline">
                            <i class="fas fa-external-link-alt"></i> View Original
                        </a>
                    ` : ''}
                    <button class="btn btn-danger" onclick="app.removeFromWorkspace(${wt.id})" title="Remove from workspace">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `).join('');

        // Add event listeners for status changes
        this.attachStatusChangeListeners(app);
    }

    static attachStatusChangeListeners(app) {
        document.querySelectorAll('.status-select').forEach(select => {
            // Remove existing listeners to prevent duplicates
            select.replaceWith(select.cloneNode(true));
        });

        // Re-attach listeners to new elements
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const workspaceId = parseInt(e.target.getAttribute('data-workspace-id'));
                const newStatus = e.target.value;
                if (workspaceId && newStatus) {
                    app.updateWorkspaceStatus(workspaceId, newStatus);
                }
            });
        });
    }

    static getStatusColor(status) {
        const colors = {
            'pending': '#f39c12',      // Orange
            'interested': '#3498db',   // Blue
            'submitted': '#27ae60',    // Green
            'not_eligible': '#e74c3c'  // Red
        };
        return colors[status] || '#7f8c8d'; // Gray for unknown status
    }

    // Helper method to prevent XSS
    static escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Method to update filter buttons
    static updateFilterButtons(activeStatus) {
        document.querySelectorAll('.status-filter').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-status') === activeStatus) {
                btn.classList.add('active');
            }
        });
    }
}