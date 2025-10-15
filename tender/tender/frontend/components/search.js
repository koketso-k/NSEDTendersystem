// components/search.js - UPDATED WITH AI SUMMARY BUTTON
class SearchComponent {
    static getHTML() {
        return `
            <div class="search-section">
                <h2><i class="fas fa-search"></i> Find Tender Opportunities</h2>
                <form id="searchForm" class="search-form">
                    <div class="form-group">
                        <label for="keywords"><i class="fas fa-key"></i> Keywords</label>
                        <input type="text" id="keywords" placeholder="e.g., road construction, security services">
                    </div>
                    <div class="form-group">
                        <label for="province"><i class="fas fa-map-marker-alt"></i> Province</label>
                        <select id="province">
                            <option value="">All Provinces</option>
                            <option value="Gauteng">Gauteng</option>
                            <option value="Western Cape">Western Cape</option>
                            <option value="KwaZulu-Natal">KwaZulu-Natal</option>
                            <option value="Eastern Cape">Eastern Cape</option>
                            <option value="Limpopo">Limpopo</option>
                            <option value="Mpumalanga">Mpumalanga</option>
                            <option value="North West">North West</option>
                            <option value="Free State">Free State</option>
                            <option value="Northern Cape">Northern Cape</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="budgetMin"><i class="fas fa-money-bill"></i> Min Budget (R)</label>
                        <input type="number" id="budgetMin" placeholder="Minimum amount" min="0">
                    </div>
                    <div class="form-group">
                        <label for="budgetMax"><i class="fas fa-money-bill-wave"></i> Max Budget (R)</label>
                        <input type="number" id="budgetMax" placeholder="Maximum amount" min="0">
                    </div>
                    <div class="form-group">
                        <label for="buyer"><i class="fas fa-building"></i> Buyer Organization</label>
                        <input type="text" id="buyer" placeholder="e.g., Department of Public Works">
                    </div>
                    <div class="form-group">
                        <label for="deadline"><i class="fas fa-clock"></i> Deadline Within (days)</label>
                        <select id="deadline">
                            <option value="">Any time</option>
                            <option value="7">7 days</option>
                            <option value="30">30 days</option>
                            <option value="60">60 days</option>
                            <option value="90">90 days</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn">
                            <i class="fas fa-search"></i> Search Tenders
                        </button>
                        <button type="button" class="btn btn-outline" id="clear-search">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                </form>
            </div>
            <div class="results-section">
                <div class="section-header">
                    <h2><i class="fas fa-list"></i> Search Results</h2>
                    <div class="results-count" id="results-count">No search performed</div>
                </div>
                <div id="searchResults"></div>
            </div>
        `;
    }

    static displayResults(tenders, app) {
        const resultsDiv = document.getElementById('searchResults');
        const countDiv = document.getElementById('results-count');
        
        if (!tenders || tenders.length === 0) {
            resultsDiv.innerHTML = `
                <div class="text-center" style="padding: 3rem; color: var(--light-text);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <h3>No tenders found</h3>
                    <p>Try adjusting your search criteria or try different keywords</p>
                </div>
            `;
            countDiv.textContent = '0 results found';
            return;
        }

        countDiv.textContent = `${tenders.length} result${tenders.length === 1 ? '' : 's'} found`;

        resultsDiv.innerHTML = tenders.map(tender => `
            <div class="tender-card" data-tender-id="${tender.id}">
                <div class="tender-header">
                    <div style="flex: 1;">
                        <h3 class="tender-title">${this.escapeHtml(tender.title)}</h3>
                        <div class="tender-meta">
                            <span><i class="fas fa-building"></i> ${this.escapeHtml(tender.buyer_organization || 'Not specified')}</span>
                            <span><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(tender.province || 'National')}</span>
                            <span><i class="fas fa-clock"></i> ${tender.submission_deadline ? new Date(tender.submission_deadline).toLocaleDateString() : 'Not specified'}</span>
                            <span><i class="fas fa-money-bill-wave"></i> ${this.escapeHtml(tender.budget_range || 'Budget not specified')}</span>
                        </div>
                    </div>
                </div>
                <p class="tender-description">${this.escapeHtml(tender.description || 'No description available.')}</p>
                <div class="tender-actions">
                    <button class="btn btn-success" onclick="app.addToWorkspace(${tender.id})" data-tender-id="${tender.id}">
                        <i class="fas fa-plus"></i> Add to Workspace
                    </button>
                    <button class="btn btn-warning" onclick="app.checkReadiness(${tender.id})" data-tender-id="${tender.id}">
                        <i class="fas fa-chart-line"></i> Check Readiness
                    </button>
                    <button class="btn btn-secondary" onclick="app.getAISummary(${tender.id})" data-tender-id="${tender.id}">
                        <i class="fas fa-robot"></i> AI Summary
                    </button>
                    ${tender.source_url ? `
                        <a href="${tender.source_url}" target="_blank" class="btn btn-outline">
                            <i class="fas fa-external-link-alt"></i> View Original
                        </a>
                    ` : ''}
                </div>
            </div>
        `).join('');
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

    // Optional: Method to clear search form
    static clearSearchForm() {
        document.getElementById('searchForm').reset();
        document.getElementById('results-count').textContent = 'No search performed';
        document.getElementById('searchResults').innerHTML = '';
    }
}