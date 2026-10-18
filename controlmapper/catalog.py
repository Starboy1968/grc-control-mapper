"""Control catalog: a curated subset of NIST SP 800-53 Rev. 5 controls.

Titles and families follow NIST SP 800-53 Rev. 5 (public domain).
Descriptions are short plain-language summaries written for matching,
not the official control text. CSF is the NIST CSF 2.0 category the
control most closely supports.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Control:
    id: str
    title: str
    family: str
    csf: str
    description: str
    keywords: tuple = field(default_factory=tuple)

    @property
    def match_text(self) -> str:
        # Keywords are repeated so they carry more weight than prose.
        return " ".join([self.title, self.description] + list(self.keywords) * 2)


FAMILIES = {
    "AC": "Access Control",
    "AT": "Awareness and Training",
    "AU": "Audit and Accountability",
    "CA": "Assessment, Authorization, and Monitoring",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MP": "Media Protection",
    "PE": "Physical and Environmental Protection",
    "PM": "Program Management",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "SA": "System and Services Acquisition",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
    "SR": "Supply Chain Risk Management",
}


def _c(id, title, csf, description, keywords):
    return Control(id, title, id.split("-")[0], csf, description, tuple(keywords))


CATALOG = [
    _c("AC-1", "Policy and Procedures", "GV.PO",
       "Develop, document, approve, and review an access control policy and procedures.",
       ["access control policy", "policy review", "procedures"]),
    _c("AC-2", "Account Management", "PR.AA",
       "Manage user accounts: approve, create, modify, disable, and remove accounts; review them periodically.",
       ["user accounts", "account review", "account provisioning", "deprovision", "disable accounts", "access review"]),
    _c("AC-3", "Access Enforcement", "PR.AA",
       "Enforce approved authorizations for access to systems and data.",
       ["authorization", "enforce access", "permissions", "role-based access"]),
    _c("AC-5", "Separation of Duties", "PR.AA",
       "Separate duties so no single person controls a whole critical process.",
       ["separation of duties", "segregation of duties", "dual control"]),
    _c("AC-6", "Least Privilege", "PR.AA",
       "Give users only the access needed for their job.",
       ["least privilege", "minimum necessary", "need to know", "only the access", "access required", "privileged access", "administrator"]),
    _c("AC-7", "Unsuccessful Logon Attempts", "PR.AA",
       "Limit failed logon attempts and lock accounts after the limit.",
       ["failed login", "account lockout", "lock account", "logon attempts"]),
    _c("AC-17", "Remote Access", "PR.AA",
       "Authorize, monitor, and protect remote access to systems.",
       ["remote access", "vpn", "telework", "remote work"]),
    _c("AT-2", "Literacy Training and Awareness", "PR.AT",
       "Give all users security awareness training at onboarding and on a recurring basis.",
       ["security awareness", "annual training", "phishing training", "employee training"]),
    _c("AT-3", "Role-Based Training", "PR.AT",
       "Give role-specific security training to people with security duties.",
       ["role-based training", "specialized training", "security responsibilities"]),
    _c("AU-2", "Event Logging", "DE.CM",
       "Identify the events the system must log to support monitoring and investigations.",
       ["logging", "audit logs", "log events", "security events"]),
    _c("AU-6", "Audit Record Review, Analysis, and Reporting", "DE.AE",
       "Review and analyze logs for suspicious activity and report findings.",
       ["log review", "log analysis", "siem", "suspicious activity", "audit review"]),
    _c("AU-11", "Audit Record Retention", "PR.PS",
       "Keep audit records for a defined period to support investigations and requirements.",
       ["log retention", "retain logs", "record retention", "audit records"]),
    _c("CA-2", "Control Assessments", "ID.IM",
       "Assess controls on a defined schedule and report results.",
       ["control assessment", "internal audit", "security assessment", "audit"]),
    _c("CA-7", "Continuous Monitoring", "DE.CM",
       "Run an ongoing program to monitor control effectiveness and risk.",
       ["continuous monitoring", "ongoing monitoring", "metrics", "security posture"]),
    _c("CM-2", "Baseline Configuration", "PR.PS",
       "Create and maintain secure baseline configurations for systems.",
       ["baseline configuration", "secure configuration", "hardening", "standard build"]),
    _c("CM-3", "Configuration Change Control", "PR.PS",
       "Review, approve, test, and document changes to systems before release.",
       ["change management", "change control", "change approval", "change request"]),
    _c("CM-8", "System Component Inventory", "ID.AM",
       "Keep an accurate inventory of hardware, software, and system components.",
       ["asset inventory", "hardware inventory", "software inventory", "asset management"]),
    _c("CP-2", "Contingency Plan", "RC.RP",
       "Create a plan to keep critical functions running and recover from disruption.",
       ["business continuity", "contingency plan", "disaster recovery", "continuity plan"]),
    _c("CP-9", "System Backup", "PR.DS",
       "Back up system and user data on a defined schedule and protect the backups.",
       ["backup", "backups", "data backup", "offsite backup"]),
    _c("CP-10", "System Recovery and Reconstitution", "RC.RP",
       "Recover and restore systems to a known state after a disruption.",
       ["restore", "recovery time", "rto", "rpo", "system recovery"]),
    _c("IA-2", "Identification and Authentication (Organizational Users)", "PR.AA",
       "Uniquely identify and authenticate users; use multi-factor authentication where required.",
       ["multi-factor authentication", "mfa", "unique user id", "authentication", "two-factor"]),
    _c("IA-5", "Authenticator Management", "PR.AA",
       "Manage passwords and other authenticators: strength, change, protection, and reset.",
       ["password", "password complexity", "password rotation", "credentials", "authenticator"]),
    _c("IR-4", "Incident Handling", "RS.MA",
       "Detect, analyze, contain, eradicate, and recover from security incidents.",
       ["incident handling", "incident response", "containment", "eradication", "security incident"]),
    _c("IR-5", "Incident Monitoring", "RS.AN",
       "Track and document security incidents.",
       ["incident tracking", "incident log", "incident documentation"]),
    _c("IR-6", "Incident Reporting", "RS.CO",
       "Require personnel to report suspected incidents quickly and report to authorities.",
       ["report incidents", "breach notification", "incident reporting", "notify", "regulators"]),
    _c("IR-8", "Incident Response Plan", "RS.MA",
       "Maintain an incident response plan with roles, procedures, and regular updates.",
       ["incident response plan", "response roles", "incident playbook", "tabletop"]),
    _c("MP-6", "Media Sanitization", "PR.DS",
       "Sanitize or destroy media before disposal or reuse.",
       ["media sanitization", "data destruction", "secure disposal", "physically destroyed", "wipe", "shred"]),
    _c("PE-2", "Physical Access Authorizations", "PR.AA",
       "Control who is authorized to enter facilities and review the list regularly.",
       ["physical access", "badge", "facility access", "visitor", "data center access"]),
    _c("PM-9", "Risk Management Strategy", "GV.RM",
       "Define and maintain a strategy for managing organizational risk.",
       ["risk management strategy", "risk appetite", "risk tolerance", "risk governance"]),
    _c("PS-3", "Personnel Screening", "GV.RR",
       "Screen individuals before granting access and rescreen as needed.",
       ["background check", "screening", "pre-employment", "personnel screening"]),
    _c("PS-4", "Personnel Termination", "GV.RR",
       "On termination, disable access, retrieve assets, and conduct exit steps.",
       ["termination", "offboarding", "last day", "revoke access", "access revoked", "return of assets"]),
    _c("RA-3", "Risk Assessment", "ID.RA",
       "Assess the likelihood and impact of risks and update the assessment regularly.",
       ["risk assessment", "risk register", "likelihood", "impact", "threat"]),
    _c("RA-5", "Vulnerability Monitoring and Scanning", "ID.RA",
       "Scan for vulnerabilities on a schedule, analyze results, and remediate.",
       ["vulnerability scan", "vulnerability management", "penetration test", "scanning"]),
    _c("SA-9", "External System Services", "GV.SC",
       "Require security from external service providers and monitor their compliance.",
       ["third party", "vendor", "service provider", "outsourced", "cloud provider"]),
    _c("SC-7", "Boundary Protection", "PR.IR",
       "Monitor and control communications at network boundaries; use firewalls and segmentation.",
       ["firewall", "network segmentation", "boundary", "dmz", "perimeter"]),
    _c("SC-8", "Transmission Confidentiality and Integrity", "PR.DS",
       "Protect data in transit.",
       ["encryption in transit", "tls", "secure transmission", "data in transit"]),
    _c("SC-13", "Cryptographic Protection", "PR.DS",
       "Use approved cryptography for protecting data.",
       ["encryption", "cryptography", "key management", "approved algorithms"]),
    _c("SC-28", "Protection of Information at Rest", "PR.DS",
       "Protect stored data from unauthorized disclosure or change.",
       ["encryption at rest", "data at rest", "disk encryption", "stored data"]),
    _c("SI-2", "Flaw Remediation", "ID.RA",
       "Find, report, and fix system flaws; install security patches on a defined timeline.",
       ["patching", "patch management", "patches", "security patches", "security updates", "remediation timeline", "flaw remediation"]),
    _c("SI-3", "Malicious Code Protection", "DE.CM",
       "Detect and stop malicious code with protection tools and keep them updated.",
       ["antivirus", "anti-malware", "endpoint protection", "malware", "edr"]),
    _c("SI-4", "System Monitoring", "DE.CM",
       "Monitor systems to detect attacks, unauthorized use, and anomalies.",
       ["intrusion detection", "system monitoring", "alerts", "anomalies", "ids"]),
    _c("SR-2", "Supply Chain Risk Management Plan", "GV.SC",
       "Develop a plan to manage supply chain risks for systems and services.",
       ["supply chain", "supplier risk", "vendor risk", "third-party risk management"]),
]

BY_ID = {c.id: c for c in CATALOG}
