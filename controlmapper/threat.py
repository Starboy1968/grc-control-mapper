"""Threat-informed ranking with MITRE ATT&CK ("know the enemy").

Each technique lists the controls that help stop it. If those controls
are missing from the policy, the technique is exposed. Exposed
techniques that attackers favor rise to the top, and the controls that
would close them rise with them.

IMPORTANT: the technique list, the technique-to-control links, and the
weights are a curated starting set written for this project. They are
judgment calls informed by public ATT&CK mitigations and common breach
reporting. They are NOT the official MITRE Center for Threat-Informed
Defense mapping. Swap in the official mapping for production use.
Technique IDs and names follow MITRE ATT&CK Enterprise.
"""

from dataclasses import dataclass, field

from .catalog import BY_ID


@dataclass(frozen=True)
class Technique:
    id: str
    name: str
    tactic: str
    weight: int          # 1 = occasional, 2 = common, 3 = very common
    controls: tuple      # 800-53 controls that help stop it


TECHNIQUES = (
    Technique("T1078", "Valid Accounts", "Initial Access", 3,
              ("IA-2", "IA-5", "AC-2", "AC-6", "AU-6")),
    Technique("T1566", "Phishing", "Initial Access", 3,
              ("AT-2", "SI-3", "SC-7")),
    Technique("T1190", "Exploit Public-Facing Application", "Initial Access", 3,
              ("SI-2", "RA-5", "SC-7")),
    Technique("T1133", "External Remote Services", "Initial Access", 2,
              ("AC-17", "IA-2", "SC-7")),
    Technique("T1195", "Supply Chain Compromise", "Initial Access", 2,
              ("SR-2", "SA-9", "SI-2")),
    Technique("T1199", "Trusted Relationship", "Initial Access", 1,
              ("SA-9", "AC-6", "SR-2")),
    Technique("T1200", "Hardware Additions", "Initial Access", 1,
              ("CM-8", "PE-2")),
    Technique("T1204", "User Execution", "Execution", 2,
              ("AT-2", "SI-3", "CM-2")),
    Technique("T1059", "Command and Scripting Interpreter", "Execution", 2,
              ("CM-2", "SI-3", "AC-6")),
    Technique("T1098", "Account Manipulation", "Persistence", 1,
              ("AC-2", "AC-6", "AU-6", "IA-5")),
    Technique("T1136", "Create Account", "Persistence", 1,
              ("AC-2", "AC-6", "AU-6")),
    Technique("T1068", "Exploitation for Privilege Escalation", "Privilege Escalation", 2,
              ("SI-2", "RA-5", "AC-6")),
    Technique("T1110", "Brute Force", "Credential Access", 2,
              ("AC-7", "IA-5", "IA-2")),
    Technique("T1003", "OS Credential Dumping", "Credential Access", 2,
              ("AC-6", "IA-5", "SI-3", "SI-4")),
    Technique("T1552", "Unsecured Credentials", "Credential Access", 2,
              ("IA-5", "AC-6", "CM-2")),
    Technique("T1557", "Adversary-in-the-Middle", "Credential Access", 1,
              ("SC-8", "SC-13")),
    Technique("T1021", "Remote Services", "Lateral Movement", 2,
              ("AC-17", "IA-2", "SC-7", "AC-6")),
    Technique("T1562", "Impair Defenses", "Defense Evasion", 2,
              ("AC-6", "SI-3", "AU-2", "CM-2")),
    Technique("T1070", "Indicator Removal", "Defense Evasion", 2,
              ("AU-2", "AU-6", "AU-11", "AC-6")),
    Technique("T1530", "Data from Cloud Storage", "Collection", 2,
              ("AC-3", "AC-6", "SC-28", "CM-2")),
    Technique("T1041", "Exfiltration Over C2 Channel", "Exfiltration", 2,
              ("SC-7", "SI-4")),
    Technique("T1048", "Exfiltration Over Alternative Protocol", "Exfiltration", 1,
              ("SC-7", "SI-4", "AU-6")),
    Technique("T1567", "Exfiltration Over Web Service", "Exfiltration", 2,
              ("SC-7", "SI-4", "AC-6")),
    Technique("T1486", "Data Encrypted for Impact", "Impact", 3,
              ("CP-9", "CP-10", "SI-3", "IR-4")),
    Technique("T1490", "Inhibit System Recovery", "Impact", 2,
              ("CP-9", "CP-10", "AC-6")),
    Technique("T1485", "Data Destruction", "Impact", 1,
              ("CP-9", "CP-10", "AC-6")),
    Technique("T1498", "Network Denial of Service", "Impact", 1,
              ("SC-7", "CP-2")),
)


@dataclass
class TechniqueView:
    technique: Technique
    in_scope: list
    covered: list
    missing: list
    exposure: float      # share of mitigating controls that are missing (0 to 1)
    risk: float          # weight x exposure

    @property
    def status(self) -> str:
        if not self.covered:
            return "Undefended"
        if self.missing:
            return "Weakly defended"
        return "Defended"


@dataclass
class ThreatView:
    techniques: list = field(default_factory=list)       # ranked, riskiest first
    control_scores: dict = field(default_factory=dict)   # control id -> threat score
    blocks: dict = field(default_factory=dict)           # control id -> [technique ids it helps close]


def assess(covered_ids, scope_ids) -> ThreatView:
    """Rank techniques by risk and controls by how much attacker risk they close.

    covered_ids: controls with high-confidence or analyst-accepted support.
    scope_ids:   controls the assessment covers (the baseline).
    """
    covered_ids, scope_ids = set(covered_ids), set(scope_ids)
    views, scores, blocks = [], {}, {}
    for t in TECHNIQUES:
        ids = [c for c in t.controls if c in scope_ids]
        if not ids:
            continue
        done = [c for c in ids if c in covered_ids]
        missing = [c for c in ids if c not in covered_ids]
        exposure = len(missing) / len(ids)
        risk = round(t.weight * exposure, 3)
        views.append(TechniqueView(t, ids, done, missing, round(exposure, 3), risk))
        # A missing control earns credit for each exposed technique it would help close.
        # Splitting by the number of missing controls stops one technique from
        # being counted many times over.
        for c in missing:
            scores[c] = round(scores.get(c, 0.0) + risk / len(missing), 3)
            blocks.setdefault(c, []).append(t.id)

    views.sort(key=lambda v: (-v.risk, -v.technique.weight, v.technique.id))
    return ThreatView(views, scores, blocks)


def to_dict(view: ThreatView, top: int = 10) -> dict:
    return {
        "note": "Curated starting set, not the official MITRE CTID mapping.",
        "top_techniques": [
            {
                "id": v.technique.id,
                "name": v.technique.name,
                "tactic": v.technique.tactic,
                "status": v.status,
                "risk": v.risk,
                "missing_controls": v.missing,
            }
            for v in view.techniques[:top]
            if v.risk > 0
        ],
        "control_threat_scores": dict(
            sorted(view.control_scores.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
    }


def to_markdown(view: ThreatView, top: int = 5) -> list:
    exposed = [v for v in view.techniques if v.risk > 0][:top]
    lines = [
        "### Know the enemy: likely attack paths",
        "",
        "Real attacker techniques (MITRE ATT&CK) that your policy leaves open, "
        "ranked by how often attackers use them and how much is missing. "
        "Source of the mapping is noted at the end of the report.",
        "",
    ]
    if not exposed:
        return lines + ["No exposed techniques in scope.", ""]
    lines += ["| Rank | Technique | Tactic | Status | Close with |", "|---:|---|---|---|---|"]
    for i, v in enumerate(exposed, 1):
        t = v.technique
        close = ", ".join(v.missing)
        lines.append(f"| {i} | {t.id} {t.name} | {t.tactic} | {v.status} | {close} |")
    lines.append("")
    return lines


def blocked_by(view: ThreatView, control_id: str, limit: int = 3) -> str:
    return ", ".join(view.blocks.get(control_id, [])[:limit]) or "none"
