# Policy-to-Control Mapping Report

- **Source:** acme_infosec_policy.md
- **Generated:** 2026-10-17
- **Framework:** NIST SP 800-53 Rev. 5 (curated subset), CSF 2.0 crosswalk

## Executive summary

- **42.9%** of in-scope controls have a high-confidence policy statement.
- **20 of 20** policy statements mapped to at least one control.
- **17** controls have no supporting statement (gaps).
- **13** mappings are low confidence and need analyst review.

## Coverage by control family

| Family | Covered | Total | % |
|---|---:|---:|---:|
| AC Access Control | 3 | 7 | 42.9% |
| AT Awareness and Training | 1 | 2 | 50.0% |
| AU Audit and Accountability | 0 | 3 | 0.0% |
| CA Assessment, Authorization, and Monitoring | 0 | 2 | 0.0% |
| CM Configuration Management | 1 | 3 | 33.3% |
| CP Contingency Planning | 1 | 3 | 33.3% |
| IA Identification and Authentication | 2 | 2 | 100.0% |
| IR Incident Response | 3 | 4 | 75.0% |
| MP Media Protection | 1 | 1 | 100.0% |
| PE Physical and Environmental Protection | 0 | 1 | 0.0% |
| PM Program Management | 0 | 1 | 0.0% |
| PS Personnel Security | 2 | 2 | 100.0% |
| RA Risk Assessment | 1 | 2 | 50.0% |
| SA System and Services Acquisition | 0 | 1 | 0.0% |
| SC System and Communications Protection | 2 | 4 | 50.0% |
| SI System and Information Integrity | 1 | 3 | 33.3% |
| SR Supply Chain Risk Management | 0 | 1 | 0.0% |

## Gaps (no supporting statement)

| Priority | Control | Title | CSF |
|---|---|---|---|
| High | AU-2 | Event Logging | DE.CM |
| High | AU-6 | Audit Record Review, Analysis, and Reporting | DE.AE |
| High | RA-3 | Risk Assessment | ID.RA |
| Medium | AC-1 | Policy and Procedures | GV.PO |
| Medium | AC-5 | Separation of Duties | PR.AA |
| Medium | AU-11 | Audit Record Retention | PR.PS |
| Medium | CA-2 | Control Assessments | ID.IM |
| Medium | CA-7 | Continuous Monitoring | DE.CM |
| Medium | CM-2 | Baseline Configuration | PR.PS |
| Medium | CM-8 | System Component Inventory | ID.AM |
| Medium | CP-10 | System Recovery and Reconstitution | RC.RP |
| Medium | CP-2 | Contingency Plan | RC.RP |
| Medium | PE-2 | Physical Access Authorizations | PR.AA |
| Medium | PM-9 | Risk Management Strategy | GV.RM |
| Medium | SI-3 | Malicious Code Protection | DE.CM |
| Medium | SI-4 | System Monitoring | DE.CM |
| Medium | SR-2 | Supply Chain Risk Management Plan | GV.SC |

## Mapped statements

| ID | Section | Statement | Control | Score | Confidence |
|---|---|---|---|---:|---|
| S001 | 1. Access Management | User accounts must be approved by a manager before they are created. | AC-2 | 0.60 | high |
| S001 | 1. Access Management | User accounts must be approved by a manager before they are created. | SC-13 | 0.23 | low |
| S001 | 1. Access Management | User accounts must be approved by a manager before they are created. | AC-7 | 0.20 | low |
| S002 | 1. Access Management | Accounts shall be reviewed every quarter and disabled when no longer needed. | AC-2 | 0.48 | high |
| S002 | 1. Access Management | Accounts shall be reviewed every quarter and disabled when no longer needed. | AC-7 | 0.23 | low |
| S003 | 1. Access Management | All employees must use multi-factor authentication to access company systems. | IA-2 | 0.92 | high |
| S003 | 1. Access Management | All employees must use multi-factor authentication to access company systems. | AC-3 | 0.19 | low |
| S004 | 1. Access Management | Passwords must be at least 14 characters and must not be reused. | IA-5 | 0.58 | high |
| S004 | 1. Access Management | Passwords must be at least 14 characters and must not be reused. | AC-6 | 0.23 | low |
| S005 | 1. Access Management | Staff shall be given only the access required to do their job. | AC-6 | 0.89 | high |
| S006 | 1. Access Management | Remote access to the network must go through the company VPN. | AC-17 | 1.00 | high |
| S006 | 1. Access Management | Remote access to the network must go through the company VPN. | SC-7 | 0.21 | low |
| S007 | 2. Incident Response | The security team shall maintain an incident response plan and test it at least once a year. | IR-8 | 0.72 | high |
| S007 | 2. Incident Response | The security team shall maintain an incident response plan and test it at least once a year. | IR-4 | 0.56 | high |
| S007 | 2. Incident Response | The security team shall maintain an incident response plan and test it at least once a year. | IR-5 | 0.25 | low |
| S008 | 2. Incident Response | All employees must report suspected security incidents to the security team within 24 hours. | IR-4 | 0.55 | high |
| S008 | 2. Incident Response | All employees must report suspected security incidents to the security team within 24 hours. | IR-6 | 0.47 | high |
| S008 | 2. Incident Response | All employees must report suspected security incidents to the security team within 24 hours. | IR-5 | 0.33 | low |
| S009 | 2. Incident Response | The company will notify affected customers and regulators of a breach as required by law. | IR-6 | 0.90 | high |
| S010 | 3. Data Protection | Customer data must be encrypted in transit using TLS 1.2 or higher. | SC-8 | 0.88 | high |
| S011 | 3. Data Protection | Sensitive data stored on laptops and servers shall be encrypted at rest. | SC-28 | 0.71 | high |
| S012 | 3. Data Protection | Backups of critical systems must be taken daily and stored offsite. | CP-9 | 0.98 | high |
| S012 | 3. Data Protection | Backups of critical systems must be taken daily and stored offsite. | SC-28 | 0.20 | low |
| S013 | 3. Data Protection | Retired hard drives must be physically destroyed before disposal. | MP-6 | 0.76 | high |
| S014 | 4. Vulnerability and Change M… | Critical security patches must be applied within 14 days of release. | SI-2 | 0.77 | high |
| S015 | 4. Vulnerability and Change M… | Vulnerability scans shall be run monthly on all production systems. | RA-5 | 0.70 | high |
| S016 | 4. Vulnerability and Change M… | All changes to production systems must be approved through a documented change request. | CM-3 | 0.78 | high |
| S016 | 4. Vulnerability and Change M… | All changes to production systems must be approved through a documented change request. | SC-13 | 0.18 | low |
| S017 | 5. Workforce | New hires must complete security awareness training within 30 days and annually afterward. | AT-2 | 0.85 | high |
| S017 | 5. Workforce | New hires must complete security awareness training within 30 days and annually afterward. | AT-3 | 0.42 | low |
| S018 | 5. Workforce | Background checks are required for all employees before they receive system access. | PS-3 | 0.64 | high |
| S018 | 5. Workforce | Background checks are required for all employees before they receive system access. | AC-6 | 0.20 | low |
| S019 | 5. Workforce | Access must be revoked on the employee's last day. | PS-4 | 0.69 | high |
| S020 | 6. Third Parties | Vendors that handle company data must be assessed for security before a contract is signed. | SA-9 | 0.39 | low |

## Analyst review queue

Low-confidence mappings. Accept or reject each before using this report in an audit.

| Statement | Control | Score | Matched terms |
|---|---|---:|---|
| S001 | SC-13 | 0.23 | approv |
| S001 | AC-7 | 0.20 | account |
| S002 | AC-7 | 0.23 | account |
| S003 | AC-3 | 0.19 | acces, system |
| S004 | AC-6 | 0.23 | least |
| S006 | SC-7 | 0.21 | network |
| S007 | IR-5 | 0.25 | incident, security |
| S008 | IR-5 | 0.33 | incident, security |
| S012 | SC-28 | 0.20 | stor |
| S016 | SC-13 | 0.18 | approv |
| S017 | AT-3 | 0.42 | security, train |
| S018 | AC-6 | 0.20 | acces, requir |
| S020 | SA-9 | 0.39 | vendor, security |

## Unmapped statements

Every statement mapped to at least one control.

---

*Method: TF-IDF similarity plus keyword phrase matching. Scores are decision support, not audit evidence. A human reviews every low-confidence mapping.*
