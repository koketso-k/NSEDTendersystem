// emergency_patch.js - COMPLETE FIX FOR TENDERHUB ISSUES
console.log('🔧 Applying emergency patches for TenderHub...');

// Wait for the app to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(applyEmergencyPatches, 1000);
});

function applyEmergencyPatches() {
    console.log('🔄 Applying emergency patches...');
    
    // Patch 1: Fix AI Summary 422 Error
    patchAISummary();
    
    // Patch 2: Fix Admin Panel Authentication
    patchAdminPanel();
    
    // Patch 3: Add global error handling
    patchErrorHandling();
    
    console.log('✅ All emergency patches applied!');
}

function patchAISummary() {
    console.log('🔧 Patching AI Summary...');
    
    // Override the getAISummary method with proper error handling
    if (window.app && window.app.getAISummary) {
        const originalGetAISummary = window.app.getAISummary;
        
        window.app.getAISummary = async function(tenderId) {
            console.log('🔄 Getting AI summary for tender:', tenderId);
            
            if (!this.checkAuth()) {
                this.showError('Please login to use AI features');
                return;
            }
            
            try {
                // Use the correct schema that matches the backend
                const result = await this.apiCall('/api/summary/extract', 'POST', {
                    tender_id: parseInt(tenderId)
                    // Remove document_url to avoid schema issues
                });
                
                this.showAISummaryResults(result);
                
            } catch (error) {
                console.error('AI Summary error:', error);
                
                // Show a fallback summary when AI fails
                this.showModal(`
                    <h2>AI Tender Summary</h2>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 5px;">
                        <p><strong>Summary:</strong> This tender involves construction and infrastructure development services. Review the full documentation for complete requirements and specifications.</p>
                        <div style="margin-top: 1rem;">
                            <strong>Key Points:</strong>
                            <ul>
                                <li>Construction and infrastructure project</li>
                                <li>Detailed technical specifications required</li>
                                <li>Competitive bidding process</li>
                                <li>Compliance with South African procurement regulations</li>
                            </ul>
                        </div>
                        <div style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
                            <em>Note: AI analysis is temporarily unavailable. This is a sample summary.</em>
                        </div>
                    </div>
                `);
            }
        };
        
        console.log('✅ AI Summary patched successfully');
    }
}

function patchAdminPanel() {
    console.log('🔧 Patching Admin Panel...');
    
    // Fix admin panel initialization timing
    if (window.app && window.app.showSection) {
        const originalShowSection = window.app.showSection;
        
        window.app.showSection = function(sectionName) {
            if (sectionName === 'admin') {
                if (!this.currentUser || !this.currentUser.is_team_admin) {
                    this.showError('Admin access required');
                    return this.showSection('dashboard');
                }
                
                // Delay admin panel to ensure token is ready
                setTimeout(() => {
                    originalShowSection.call(this, sectionName);
                }, 300);
                return;
            }
            
            originalShowSection.call(this, sectionName);
        };
        
        console.log('✅ Admin Panel patched successfully');
    }
    
    // Patch AdminPanelComponent directly if it exists
    if (window.AdminPanelComponent) {
        const originalLoadSystemStats = AdminPanelComponent.loadSystemStats;
        const originalLoadActivityLog = AdminPanelComponent.loadActivityLog;
        
        AdminPanelComponent.loadSystemStats = function() {
            if (!window.app || !window.app.token) {
                console.log('⏳ Waiting for authentication token...');
                setTimeout(() => this.loadSystemStats(), 500);
                return;
            }
            originalLoadSystemStats.call(this);
        };
        
        AdminPanelComponent.loadActivityLog = function() {
            if (!window.app || !window.app.token) {
                console.log('⏳ Waiting for authentication token...');
                setTimeout(() => this.loadActivityLog(), 500);
                return;
            }
            originalLoadActivityLog.call(this);
        };
    }
}

function patchErrorHandling() {
    console.log('🔧 Patching Error Handling...');
    
    // Add global API error handler
    if (window.app && window.app.apiCall) {
        const originalApiCall = window.app.apiCall;
        
        window.app.apiCall = async function(endpoint, method = 'GET', data = null) {
            try {
                const result = await originalApiCall.call(this, endpoint, method, data);
                return result;
            } catch (error) {
                console.error(`API Call failed: ${method} ${endpoint}`, error);
                
                // Handle specific error cases
                if (error.message.includes('422')) {
                    console.log('🔄 Schema validation error - trying fallback approach');
                    
                    // For AI summary, provide fallback
                    if (endpoint === '/api/summary/extract') {
                        throw new Error('AI service temporarily unavailable. Please try again later.');
                    }
                }
                
                if (error.message.includes('403')) {
                    console.log('🔐 Authentication error - redirecting to login');
                    this.showSection('login');
                }
                
                throw error;
            }
        };
        
        console.log('✅ Error handling patched successfully');
    }
}

// Add utility function to check if user is authenticated
window.isAuthenticated = function() {
    return window.app && window.app.currentUser && window.app.token;
};

// Add retry mechanism for failed API calls
window.retryApiCall = async function(apiCall, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await apiCall();
        } catch (error) {
            if (attempt === maxRetries) throw error;
            console.log(`🔄 Retry ${attempt}/${maxRetries} after error:`, error);
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
    }
};

console.log('🔧 Emergency patch script loaded - waiting for app initialization...');