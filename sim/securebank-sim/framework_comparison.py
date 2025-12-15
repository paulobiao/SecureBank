# framework_comparison.py
"""
Módulo de Comparação de Frameworks Zero Trust

Compara três abordagens:
1. Baseline: regras estáticas tradicionais
2. NIST ZTA: implementação dos 7 princípios NIST SP 800-207
3. SecureBank™: framework financeiramente aware com ITAL

Dimensões de comparação (baseadas no artigo SecureBank™):
- Financial Context Awareness
- Adaptive Identity Scoring  
- Contextual Micro-Segmentation
- Impact-Driven Automation
- Transactional Risk Integration
- Real-time Trust Adaptation
"""

import json
import statistics
from typing import Dict, List, Tuple
from collections import defaultdict


class FrameworkComparator:
    """
    Compara múltiplos frameworks Zero Trust em dimensões qualitativas e quantitativas.
    """
    
    def __init__(self):
        # Dimensões de avaliação (0-100)
        self.dimensions = [
            "Financial Context Awareness",
            "Adaptive Identity Scoring",
            "Contextual Micro-Segmentation",
            "Impact-Driven Automation",
            "Transactional Risk Integration",
            "Real-time Trust Adaptation",
        ]
        
        # Scores qualitativos baseados em análise arquitetural
        self.qualitative_scores = {
            "baseline": {
                "Financial Context Awareness": 15,  # apenas valor de transação
                "Adaptive Identity Scoring": 10,    # sem adaptação
                "Contextual Micro-Segmentation": 20,  # segmentação rudimentar por geo
                "Impact-Driven Automation": 25,     # regras fixas
                "Transactional Risk Integration": 30,  # considera valor mas não perfil
                "Real-time Trust Adaptation": 5,    # sem adaptação
            },
            "nist_zta": {
                "Financial Context Awareness": 40,  # considera valores mas sem contexto financeiro profundo
                "Adaptive Identity Scoring": 65,    # MFA + device posture + sessões
                "Contextual Micro-Segmentation": 75,  # zonas de rede + least privilege
                "Impact-Driven Automation": 70,     # políticas dinâmicas baseadas em risco
                "Transactional Risk Integration": 55,  # risco genérico, não financeiro específico
                "Real-time Trust Adaptation": 60,   # device trust decay + session monitoring
            },
            "securebank": {
                "Financial Context Awareness": 95,  # serviços financeiros específicos + AML awareness
                "Adaptive Identity Scoring": 95,    # ITAL completo
                "Contextual Micro-Segmentation": 90,  # segmentação por serviço + valor + perfil
                "Impact-Driven Automation": 90,     # adaptação baseada em impacto financeiro
                "Transactional Risk Integration": 95,  # identity drift + perfil transacional
                "Real-time Trust Adaptation": 95,   # ITAL com trust decay/growth dinâmico
            },
        }
    
    def compute_quantitative_metrics(self, baseline_logs, nist_logs, securebank_logs, 
                                    ital_params=None) -> Dict:
        """
        Calcula métricas quantitativas para os 3 frameworks.
        
        Returns:
            dict com métricas TII, SAE, ITAL, latência, overhead
        """
        from metrics import compute_tii, compute_sae, compute_ital
        
        if ital_params is None:
            ital_params = {}
        
        results = {
            "baseline": {
                "TII": compute_tii(baseline_logs),
                "SAE": compute_sae(baseline_logs),
                "ITAL": compute_ital(baseline_logs, ital_params),
                "latency_ms": self._estimate_latency("baseline", baseline_logs),
                "overhead_pct": self._estimate_overhead("baseline"),
            },
            "nist_zta": {
                "TII": compute_tii(nist_logs),
                "SAE": compute_sae(nist_logs),
                "ITAL": compute_ital(nist_logs, ital_params),
                "latency_ms": self._estimate_latency("nist_zta", nist_logs),
                "overhead_pct": self._estimate_overhead("nist_zta"),
            },
            "securebank": {
                "TII": compute_tii(securebank_logs),
                "SAE": compute_sae(securebank_logs),
                "ITAL": compute_ital(securebank_logs, ital_params),
                "latency_ms": self._estimate_latency("securebank", securebank_logs),
                "overhead_pct": self._estimate_overhead("securebank"),
            },
        }
        
        return results
    
    def _estimate_latency(self, pdp_type: str, logs: List[Dict]) -> float:
        """
        Estima latência média de decisão (em ms).
        
        Baseado em complexidade computacional:
        - Baseline: ~5ms (regras simples)
        - NIST ZTA: ~15ms (MFA simulation + device posture + multiple checks)
        - SecureBank: ~20ms (ITAL + identity drift + perfil)
        """
        base_latencies = {
            "baseline": 5.0,
            "nist_zta": 15.0,
            "securebank": 20.0,
        }
        
        base = base_latencies.get(pdp_type, 10.0)
        
        # Adiciona variação baseada em complexidade de decisão
        if logs:
            complex_decisions = sum(1 for log in logs if log.get("action") in ["block", "step_up"])
            complexity_factor = complex_decisions / len(logs)
            base *= (1 + complexity_factor * 0.3)  # até 30% overhead em decisões complexas
        
        return round(base, 2)
    
    def _estimate_overhead(self, pdp_type: str) -> float:
        """
        Estima overhead operacional (% sobre baseline).
        
        Considera:
        - Custo de manutenção de estado
        - Complexidade de configuração
        - Recursos computacionais
        """
        overheads = {
            "baseline": 0.0,      # referência
            "nist_zta": 45.0,     # MFA + device management + session tracking
            "securebank": 55.0,   # ITAL + perfis + identity drift
        }
        
        return overheads.get(pdp_type, 0.0)
    
    def generate_comparison_table(self, quantitative_metrics: Dict) -> Dict:
        """
        Gera tabela comparativa completa (qualitativa + quantitativa).
        
        Returns:
            dict formatado para markdown/LaTeX
        """
        frameworks = ["baseline", "nist_zta", "securebank"]
        framework_names = {
            "baseline": "Baseline (Static Rules)",
            "nist_zta": "NIST ZTA (SP 800-207)",
            "securebank": "SecureBank™ (Proposed)",
        }
        
        comparison = {
            "frameworks": [framework_names[f] for f in frameworks],
            "qualitative": {},
            "quantitative": {},
        }
        
        # Dimensões qualitativas
        for dim in self.dimensions:
            comparison["qualitative"][dim] = [
                self.qualitative_scores[f][dim] for f in frameworks
            ]
        
        # Métricas quantitativas
        for metric in ["TII", "SAE", "ITAL", "latency_ms", "overhead_pct"]:
            comparison["quantitative"][metric] = [
                round(quantitative_metrics[f][metric], 4) for f in frameworks
            ]
        
        # Score agregado (média das dimensões qualitativas)
        comparison["overall_score"] = [
            round(statistics.mean(self.qualitative_scores[f].values()), 1)
            for f in frameworks
        ]
        
        return comparison
    
    def compute_statistical_significance(self, baseline_vals: List[float], 
                                        nist_vals: List[float],
                                        securebank_vals: List[float]) -> Dict:
        """
        Calcula significância estatística das diferenças.
        
        Usa t-test para comparar médias.
        """
        from scipy import stats as scipy_stats
        
        results = {}
        
        # SecureBank vs Baseline
        if len(baseline_vals) > 1 and len(securebank_vals) > 1:
            t_stat, p_value = scipy_stats.ttest_ind(securebank_vals, baseline_vals)
            results["securebank_vs_baseline"] = {
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(p_value), 6),
                "significant": bool(p_value < 0.05),
            }
        
        # SecureBank vs NIST ZTA
        if len(nist_vals) > 1 and len(securebank_vals) > 1:
            t_stat, p_value = scipy_stats.ttest_ind(securebank_vals, nist_vals)
            results["securebank_vs_nist"] = {
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(p_value), 6),
                "significant": bool(p_value < 0.05),
            }
        
        # NIST ZTA vs Baseline
        if len(baseline_vals) > 1 and len(nist_vals) > 1:
            t_stat, p_value = scipy_stats.ttest_ind(nist_vals, baseline_vals)
            results["nist_vs_baseline"] = {
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(p_value), 6),
                "significant": bool(p_value < 0.05),
            }
        
        return results
    
    def analyze_tradeoffs(self, quantitative_metrics: Dict) -> Dict:
        """
        Analisa trade-offs entre frameworks.
        
        Examina:
        - TII vs SAE (usabilidade vs segurança)
        - SAE vs latency (segurança vs performance)
        - Effectiveness vs overhead (efetividade vs custo)
        """
        frameworks = ["baseline", "nist_zta", "securebank"]
        
        tradeoffs = {
            "tii_vs_sae": [],
            "sae_vs_latency": [],
            "effectiveness_vs_overhead": [],
        }
        
        for f in frameworks:
            metrics = quantitative_metrics[f]
            
            tradeoffs["tii_vs_sae"].append({
                "framework": f,
                "tii": metrics["TII"],
                "sae": metrics["SAE"],
            })
            
            tradeoffs["sae_vs_latency"].append({
                "framework": f,
                "sae": metrics["SAE"],
                "latency": metrics["latency_ms"],
            })
            
            # Effectiveness = (SAE + TII) / 2
            effectiveness = (metrics["SAE"] + metrics["TII"]) / 2
            tradeoffs["effectiveness_vs_overhead"].append({
                "framework": f,
                "effectiveness": effectiveness,
                "overhead": metrics["overhead_pct"],
            })
        
        return tradeoffs


def compare_frameworks(baseline_logs, nist_logs, securebank_logs, ital_params=None) -> Dict:
    """
    Função helper para comparação completa de frameworks.
    
    Args:
        baseline_logs: logs do baseline PDP
        nist_logs: logs do NIST ZTA PDP  
        securebank_logs: logs do SecureBank PDP
        ital_params: parâmetros ITAL (opcional)
    
    Returns:
        dict com análise completa
    """
    comparator = FrameworkComparator()
    
    # Métricas quantitativas
    quant_metrics = comparator.compute_quantitative_metrics(
        baseline_logs, nist_logs, securebank_logs, ital_params
    )
    
    # Tabela comparativa
    comparison_table = comparator.generate_comparison_table(quant_metrics)
    
    # Trade-offs
    tradeoffs = comparator.analyze_tradeoffs(quant_metrics)
    
    return {
        "quantitative_metrics": quant_metrics,
        "comparison_table": comparison_table,
        "tradeoffs": tradeoffs,
        "qualitative_scores": comparator.qualitative_scores,
    }
