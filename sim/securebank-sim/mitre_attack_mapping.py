# mitre_attack_mapping.py
"""
Mapeamento MITRE ATT&CK para cenários de ataque SecureBank™

Mapeia os 5 cenários de simulação para técnicas específicas do MITRE ATT&CK Framework,
permitindo análise quantitativa de cobertura de segurança.

Referência: https://attack.mitre.org/
"""

from typing import Dict, List, Set
from collections import defaultdict


# Mapeamento completo: cenário -> técnicas MITRE ATT&CK
SCENARIO_TO_MITRE = {
    1: {  # Credential Compromise
        "name": "Credential Compromise",
        "description": "Uso de credenciais roubadas ou comprometidas",
        "techniques": [
            {
                "id": "T1078",
                "name": "Valid Accounts",
                "tactic": "Initial Access, Defense Evasion, Persistence, Privilege Escalation",
                "description": "Adversários usam credenciais válidas para acesso inicial",
            },
            {
                "id": "T1110",
                "name": "Brute Force",
                "tactic": "Credential Access",
                "description": "Tentativas de adivinhar credenciais através de força bruta",
            },
            {
                "id": "T1212",
                "name": "Exploitation for Credential Access",
                "tactic": "Credential Access",
                "description": "Exploração para obter credenciais",
            },
        ],
    },
    2: {  # Insider Lateral Movement
        "name": "Insider Lateral Movement",
        "description": "Movimento lateral de insider malicioso entre serviços",
        "techniques": [
            {
                "id": "T1021",
                "name": "Remote Services",
                "tactic": "Lateral Movement",
                "description": "Uso de serviços remotos legítimos para movimento lateral",
            },
            {
                "id": "T1570",
                "name": "Lateral Tool Transfer",
                "tactic": "Lateral Movement",
                "description": "Transferência de ferramentas entre sistemas comprometidos",
            },
            {
                "id": "T1550",
                "name": "Use Alternate Authentication Material",
                "tactic": "Defense Evasion, Lateral Movement",
                "description": "Uso de tokens/tickets de autenticação alternativos",
            },
        ],
    },
    3: {  # API Abuse
        "name": "API Abuse",
        "description": "Abuso de APIs públicas para exfiltração ou ataque",
        "techniques": [
            {
                "id": "T1190",
                "name": "Exploit Public-Facing Application",
                "tactic": "Initial Access",
                "description": "Exploração de aplicações web/APIs públicas",
            },
            {
                "id": "T1595",
                "name": "Active Scanning",
                "tactic": "Reconnaissance",
                "description": "Scanning ativo de APIs para identificar vulnerabilidades",
            },
            {
                "id": "T1499",
                "name": "Endpoint Denial of Service",
                "tactic": "Impact",
                "description": "DoS através de abuso de endpoints de API",
            },
        ],
    },
    4: {  # Money Laundering
        "name": "Money Laundering",
        "description": "Lavagem de dinheiro através de transações estruturadas",
        "techniques": [
            {
                "id": "T1573",
                "name": "Encrypted Channel",
                "tactic": "Command and Control",
                "description": "Uso de canais criptografados para ocultar comunicação",
            },
            {
                "id": "T1048",
                "name": "Exfiltration Over Alternative Protocol",
                "tactic": "Exfiltration",
                "description": "Exfiltração de fundos através de protocolos alternativos",
            },
            {
                "id": "T1027",
                "name": "Obfuscated Files or Information",
                "tactic": "Defense Evasion",
                "description": "Ofuscação de padrões transacionais",
            },
        ],
    },
    5: {  # Session Hijacking
        "name": "Session Hijacking",
        "description": "Sequestro de sessão autenticada",
        "techniques": [
            {
                "id": "T1539",
                "name": "Steal Web Session Cookie",
                "tactic": "Credential Access",
                "description": "Roubo de cookies de sessão web",
            },
            {
                "id": "T1185",
                "name": "Browser Session Hijacking",
                "tactic": "Collection",
                "description": "Sequestro de sessão ativa do browser",
            },
            {
                "id": "T1563",
                "name": "Remote Service Session Hijacking",
                "tactic": "Lateral Movement",
                "description": "Sequestro de sessão de serviço remoto",
            },
        ],
    },
}


class MITREAttackMapper:
    """
    Analisa cobertura de técnicas MITRE ATT&CK por diferentes PDPs.
    """
    
    def __init__(self):
        self.scenario_mapping = SCENARIO_TO_MITRE
        
    def get_all_techniques(self) -> Set[str]:
        """
        Retorna conjunto de todos os IDs de técnicas MITRE mapeadas.
        """
        techniques = set()
        for scenario_data in self.scenario_mapping.values():
            for tech in scenario_data["techniques"]:
                techniques.add(tech["id"])
        return techniques
    
    def get_techniques_for_scenario(self, scenario_id: int) -> List[Dict]:
        """
        Retorna lista de técnicas MITRE para um cenário específico.
        """
        if scenario_id in self.scenario_mapping:
            return self.scenario_mapping[scenario_id]["techniques"]
        return []
    
    def compute_coverage(self, logs: List[Dict], pdp_name: str) -> Dict:
        """
        Calcula cobertura MITRE ATT&CK para um PDP.
        
        Args:
            logs: logs de simulação do PDP
            pdp_name: nome do PDP ("baseline", "nist_zta", "securebank")
        
        Returns:
            dict com métricas de cobertura
        """
        # Contadores por técnica
        technique_stats = defaultdict(lambda: {
            "total_attacks": 0,
            "detected": 0,
            "blocked": 0,
            "scenarios": set(),
        })
        
        # Contadores por cenário
        scenario_stats = defaultdict(lambda: {
            "total": 0,
            "detected": 0,
            "blocked": 0,
        })
        
        for log in logs:
            if not log.get("is_attack"):
                continue
            
            scenario_id = log.get("scenario")
            if scenario_id not in self.scenario_mapping:
                continue
            
            action = log.get("action")
            detected = action in ["block", "step_up"]
            blocked = action == "block"
            
            # Atualiza estatísticas do cenário
            scenario_stats[scenario_id]["total"] += 1
            if detected:
                scenario_stats[scenario_id]["detected"] += 1
            if blocked:
                scenario_stats[scenario_id]["blocked"] += 1
            
            # Atualiza estatísticas de cada técnica associada
            techniques = self.get_techniques_for_scenario(scenario_id)
            for tech in techniques:
                tech_id = tech["id"]
                technique_stats[tech_id]["total_attacks"] += 1
                technique_stats[tech_id]["scenarios"].add(scenario_id)
                if detected:
                    technique_stats[tech_id]["detected"] += 1
                if blocked:
                    technique_stats[tech_id]["blocked"] += 1
        
        # Converte sets para listas (para JSON serialization)
        for tech_id in technique_stats:
            technique_stats[tech_id]["scenarios"] = list(technique_stats[tech_id]["scenarios"])
        
        # Calcula métricas agregadas
        total_techniques = len(self.get_all_techniques())
        covered_techniques = len([t for t in technique_stats if technique_stats[t]["detected"] > 0])
        
        total_attacks = sum(s["total"] for s in scenario_stats.values())
        total_detected = sum(s["detected"] for s in scenario_stats.values())
        total_blocked = sum(s["blocked"] for s in scenario_stats.values())
        
        coverage_rate = (covered_techniques / total_techniques * 100) if total_techniques > 0 else 0
        detection_rate = (total_detected / total_attacks * 100) if total_attacks > 0 else 0
        block_rate = (total_blocked / total_attacks * 100) if total_attacks > 0 else 0
        
        return {
            "pdp_name": pdp_name,
            "total_techniques": total_techniques,
            "covered_techniques": covered_techniques,
            "coverage_rate": coverage_rate,
            "total_attacks": total_attacks,
            "total_detected": total_detected,
            "total_blocked": total_blocked,
            "detection_rate": detection_rate,
            "block_rate": block_rate,
            "technique_stats": dict(technique_stats),
            "scenario_stats": dict(scenario_stats),
        }
    
    def generate_coverage_matrix(self, baseline_logs, nist_logs, securebank_logs) -> Dict:
        """
        Gera matriz de cobertura comparativa entre os 3 PDPs.
        
        Returns:
            dict com matriz [technique x pdp] e estatísticas
        """
        baseline_coverage = self.compute_coverage(baseline_logs, "baseline")
        nist_coverage = self.compute_coverage(nist_logs, "nist_zta")
        securebank_coverage = self.compute_coverage(securebank_logs, "securebank")
        
        # Matriz de cobertura: técnica -> {baseline, nist, securebank}
        matrix = {}
        for tech_id in self.get_all_techniques():
            matrix[tech_id] = {
                "technique_name": self._get_technique_name(tech_id),
                "baseline": self._get_technique_detection_rate(baseline_coverage, tech_id),
                "nist_zta": self._get_technique_detection_rate(nist_coverage, tech_id),
                "securebank": self._get_technique_detection_rate(securebank_coverage, tech_id),
            }
        
        return {
            "matrix": matrix,
            "summary": {
                "baseline": baseline_coverage,
                "nist_zta": nist_coverage,
                "securebank": securebank_coverage,
            },
        }
    
    def _get_technique_name(self, tech_id: str) -> str:
        """Obtém nome da técnica pelo ID."""
        for scenario_data in self.scenario_mapping.values():
            for tech in scenario_data["techniques"]:
                if tech["id"] == tech_id:
                    return tech["name"]
        return "Unknown"
    
    def _get_technique_detection_rate(self, coverage_data: Dict, tech_id: str) -> float:
        """Calcula taxa de detecção para uma técnica específica."""
        tech_stats = coverage_data["technique_stats"].get(tech_id, {})
        total = tech_stats.get("total_attacks", 0)
        detected = tech_stats.get("detected", 0)
        
        if total == 0:
            return 0.0
        return (detected / total) * 100


def analyze_mitre_coverage(baseline_logs, nist_logs, securebank_logs) -> Dict:
    """
    Função helper para análise completa de cobertura MITRE ATT&CK.
    
    Args:
        baseline_logs: logs do baseline PDP
        nist_logs: logs do NIST ZTA PDP
        securebank_logs: logs do SecureBank PDP
    
    Returns:
        dict com análise completa de cobertura
    """
    mapper = MITREAttackMapper()
    return mapper.generate_coverage_matrix(baseline_logs, nist_logs, securebank_logs)
