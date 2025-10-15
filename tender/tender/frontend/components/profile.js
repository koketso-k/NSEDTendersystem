// components/profile.js
class ProfileComponent {
    static getHTML(companyProfile) {
        const profile = companyProfile || {};
        
        // Helper to safely get nested values
        const getCertification = (cert) => {
            if (!profile.certifications) return '';
            if (typeof profile.certifications === 'string') {
                try {
                    const certs = JSON.parse(profile.certifications);
                    return certs[cert] || '';
                } catch {
                    return '';
                }
            }
            return profile.certifications[cert] || '';
        };

        // Helper to check geographic coverage
        const hasCoverage = (province) => {
            if (!profile.geographic_coverage) return false;
            if (Array.isArray(profile.geographic_coverage)) {
                return profile.geographic_coverage.includes(province);
            }
            if (typeof profile.geographic_coverage === 'string') {
                try {
                    const coverage = JSON.parse(profile.geographic_coverage);
                    return Array.isArray(coverage) && coverage.includes(province);
                } catch {
                    return false;
                }
            }
            return false;
        };

        return `
            <div class="profile-section">
                <h2><i class="fas fa-building"></i> Company Profile</h2>
                <p>Set up your company information to get better tender recommendations and readiness scores</p>
                
                ${profile.id ? `
                    <div class="profile-status" style="background: var(--success-color); color: white; padding: 0.5rem 1rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                        <i class="fas fa-check-circle"></i> Profile saved! Your readiness scores will now be more accurate.
                    </div>
                ` : ''}
                
                <form id="profileForm" class="profile-form mt-3">
                    <div class="form-group">
                        <label for="company_name">Company Name *</label>
                        <input type="text" id="company_name" name="company_name" 
                               value="${this.escapeHtml(profile.company_name || '')}" 
                               placeholder="Enter your company's legal name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="industry_sector">Industry Sector *</label>
                        <select id="industry_sector" name="industry_sector" required>
                            <option value="">Select Industry</option>
                            <option value="Construction" ${profile.industry_sector === 'Construction' ? 'selected' : ''}>Construction</option>
                            <option value="IT Services" ${profile.industry_sector === 'IT Services' ? 'selected' : ''}>IT Services</option>
                            <option value="Security" ${profile.industry_sector === 'Security' ? 'selected' : ''}>Security</option>
                            <option value="Cleaning" ${profile.industry_sector === 'Cleaning' ? 'selected' : ''}>Cleaning</option>
                            <option value="Transport" ${profile.industry_sector === 'Transport' ? 'selected' : ''}>Transport</option>
                            <option value="Healthcare" ${profile.industry_sector === 'Healthcare' ? 'selected' : ''}>Healthcare</option>
                            <option value="Education" ${profile.industry_sector === 'Education' ? 'selected' : ''}>Education</option>
                            <option value="Agriculture" ${profile.industry_sector === 'Agriculture' ? 'selected' : ''}>Agriculture</option>
                            <option value="Mining" ${profile.industry_sector === 'Mining' ? 'selected' : ''}>Mining</option>
                            <option value="Manufacturing" ${profile.industry_sector === 'Manufacturing' ? 'selected' : ''}>Manufacturing</option>
                        </select>
                    </div>
                    
                    <div class="form-group full-width">
                        <label for="services_provided">Services Provided *</label>
                        <textarea id="services_provided" name="services_provided" rows="3" 
                                  placeholder="Describe the services your company offers. Be specific for better tender matches."
                                  required>${this.escapeHtml(profile.services_provided || '')}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="years_experience">Years of Experience *</label>
                        <input type="number" id="years_experience" name="years_experience" 
                               value="${profile.years_experience || ''}" min="0" max="100"
                               placeholder="Number of years in business" required>
                    </div>
                    
                    <div class="form-group full-width">
                        <label>Certifications & Compliance</label>
                        <div class="certifications-grid">
                            <div class="certification-item">
                                <label for="cidb">CIDB Grade</label>
                                <input type="text" id="cidb" name="cidb" 
                                       value="${this.escapeHtml(getCertification('CIDB'))}" 
                                       placeholder="e.g., Grade 7">
                                <small>Construction Industry Development Board</small>
                            </div>
                            <div class="certification-item">
                                <label for="bbbee">BBBEE Level</label>
                                <input type="text" id="bbbee" name="bbbee" 
                                       value="${this.escapeHtml(getCertification('BBBEE'))}" 
                                       placeholder="e.g., Level 2">
                                <small>Broad-Based Black Economic Empowerment</small>
                            </div>
                            <div class="certification-item">
                                <label for="sars">SARS Tax Compliant</label>
                                <select id="sars" name="sars">
                                    <option value="false">No</option>
                                    <option value="true" ${getCertification('SARS') === 'true' ? 'selected' : ''}>Yes</option>
                                </select>
                                <small>South African Revenue Service</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group full-width">
                        <label for="geographic_coverage">Geographic Coverage *</label>
                        <select id="geographic_coverage" name="geographic_coverage" multiple 
                                class="province-select" required>
                            <option value="Gauteng" ${hasCoverage('Gauteng') ? 'selected' : ''}>Gauteng</option>
                            <option value="Western Cape" ${hasCoverage('Western Cape') ? 'selected' : ''}>Western Cape</option>
                            <option value="KwaZulu-Natal" ${hasCoverage('KwaZulu-Natal') ? 'selected' : ''}>KwaZulu-Natal</option>
                            <option value="Eastern Cape" ${hasCoverage('Eastern Cape') ? 'selected' : ''}>Eastern Cape</option>
                            <option value="Limpopo" ${hasCoverage('Limpopo') ? 'selected' : ''}>Limpopo</option>
                            <option value="Mpumalanga" ${hasCoverage('Mpumalanga') ? 'selected' : ''}>Mpumalanga</option>
                            <option value="North West" ${hasCoverage('North West') ? 'selected' : ''}>North West</option>
                            <option value="Free State" ${hasCoverage('Free State') ? 'selected' : ''}>Free State</option>
                            <option value="Northern Cape" ${hasCoverage('Northern Cape') ? 'selected' : ''}>Northern Cape</option>
                        </select>
                        <small>Hold Ctrl/Cmd to select multiple provinces where your company operates</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="contact_email">Contact Email *</label>
                        <input type="email" id="contact_email" name="contact_email" 
                               value="${this.escapeHtml(profile.contact_email || '')}" 
                               placeholder="primary@company.co.za" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="contact_phone">Contact Phone *</label>
                        <input type="tel" id="contact_phone" name="contact_phone" 
                               value="${this.escapeHtml(profile.contact_phone || '')}" 
                               placeholder="+27 11 123 4567" required>
                    </div>
                    
                    <div class="form-actions full-width">
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-save"></i> ${profile.id ? 'Update' : 'Save'} Profile
                        </button>
                        ${profile.id ? `
                            <button type="button" class="btn btn-outline" id="view-readiness-impact">
                                <i class="fas fa-chart-line"></i> View Readiness Impact
                            </button>
                        ` : ''}
                    </div>
                </form>
            </div>
        `;
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

    // Method to get form data
    static getFormData() {
        const form = document.getElementById('profileForm');
        if (!form) return null;

        const formData = new FormData(form);
        const geographicCoverage = Array.from(document.getElementById('geographic_coverage').selectedOptions)
            .map(option => option.value);

        return {
            company_name: formData.get('company_name'),
            industry_sector: formData.get('industry_sector'),
            services_provided: formData.get('services_provided'),
            years_experience: parseInt(formData.get('years_experience')),
            certifications: {
                CIDB: formData.get('cidb'),
                BBBEE: formData.get('bbbee'),
                SARS: formData.get('sars')
            },
            geographic_coverage: geographicCoverage,
            contact_email: formData.get('contact_email'),
            contact_phone: formData.get('contact_phone')
        };
    }

    // Method to validate form
    static validateForm() {
        const form = document.getElementById('profileForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return false;
        }

        // Custom validation for geographic coverage
        const geographicCoverage = Array.from(document.getElementById('geographic_coverage').selectedOptions)
            .map(option => option.value);
        
        if (geographicCoverage.length === 0) {
            alert('Please select at least one province for geographic coverage');
            return false;
        }

        return true;
    }
}