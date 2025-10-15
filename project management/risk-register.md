# RISK REGISTER
## Tender Insight Hub - Risk Management & Mitigation Plan

**Project:** NSED742-TIH  
**Document Version:** 1.0  
**Date:** August 2025  
**Review Frequency:** Weekly during team lead meetings  

---

## 📊 RISK ASSESSMENT FRAMEWORK

### Risk Probability Scale
| Level | Description | Probability Range |
|-------|-------------|-------------------|
| **1 - Very Low** | Unlikely to occur | 0-10% |
| **2 - Low** | May occur occasionally | 11-30% |
| **3 - Medium** | Likely to occur | 31-60% |
| **4 - High** | Very likely to occur | 61-85% |
| **5 - Very High** | Almost certain to occur | 86-100% |

### Impact Severity Scale
| Level | Description | Impact on Project |
|-------|-------------|-------------------|
| **1 - Very Low** | Minimal impact | <1 day delay, no scope impact |
| **2 - Low** | Minor impact | 1-3 days delay, minor scope adjustment |
| **3 - Medium** | Moderate impact | 1 week delay, feature simplification |
| **4 - High** | Major impact | 2-3 weeks delay, significant scope reduction |
| **5 - Very High** | Critical impact | Project failure or major timeline extension |

### Risk Score Calculation
**Risk Score = Probability × Impact**
- **Low Risk (1-6):** Monitor only
- **Medium Risk (7-12):** Active mitigation required
- **High Risk (13-20):** Immediate action plan required
- **Critical Risk (21-25):** Escalate to instructor immediately

---

## 🚨 HIGH-PRIORITY RISKS (Score 13+)

### R001: Team Member Unavailability
| **Risk ID** | R001 |
|-------------|------|
| **Category** | Resource Risk |
| **Description** | Team member becomes unavailable due to illness, personal issues, or academic conflicts |
| **Probability** | 4 (High) |
| **Impact** | 4 (High) |
| **Risk Score** | 16 (Critical) |
| **Owner** | Current Team Lead |

**Potential Consequences:**
- Critical knowledge loss
- Sprint velocity reduction
- Timeline delays
- Unbalanced workload distribution

**Mitigation Strategies:**
- **Preventive:**
  - Cross-training on all critical components
  - Documentation of all development decisions
  - Pair programming for complex features
  - Regular knowledge sharing sessions
  
- **Contingency:**
  - Backup developer assigned to each major component
  - Scope reduction protocol for extended absences
  - Emergency task redistribution plan
  - External support from other teams (if permitted)

**Monitoring Indicators:**
- Attendance tracking in daily standups
- Reduced commit frequency
- Missed sprint commitments
- Communication gaps

**Escalation Trigger:** Member unavailable >3 consecutive days

---

### R002: OCDS API Reliability Issues
| **Risk ID** | R002 |
|-------------|------|
| **Category** | Technical Risk |
| **Description** | OCDS eTenders API becomes unreliable, rate-limited,
