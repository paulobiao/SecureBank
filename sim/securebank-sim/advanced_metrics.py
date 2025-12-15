"""
advanced_metrics.py

Módulo de análises complementares avançadas para o artigo SecureBank™:
1. Cost-Benefit / ROI Analysis
2. False Positive/Negative Analysis
3. Scalability Analysis
4. Sensitivity Analysis
"""

import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import statistics


# =========================================================================
# 1. ANÁLISE DE CUSTOS / ROI
# =========================================================================

def compute_roi_analysis(
    baseline_logs: List[Dict],
    securebank_logs: List[Dict],
    params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calcula análise de custos/benefícios e ROI para implementação do SecureBank™.
    
    Args:
        baseline_logs: Logs do sistema baseline
        securebank_logs: Logs do SecureBank™
        params: Parâmetros de custo (opcional)
    
    Returns:
        Dict com análise de ROI, payback period, custos e benefícios
    """
    if params is None:
        params = {}
    
    # Custos de implementação (valores padrão em USD)
    costs = {
        # Infraestrutura
        "sdn_infrastructure": params.get("sdn_cost", 50000),
        "soar_platform": params.get("soar_cost", 75000),
        "servers_hardware": params.get("servers_cost", 30000),
        "network_equipment": params.get("network_cost", 20000),
        
        # Desenvolvimento e Integração
        "development_months": params.get("dev_months", 6),
        "developer_rate_monthly": params.get("dev_rate", 10000),
        "integration_effort": params.get("integration_cost", 40000),
        
        # Treinamento
        "training_staff": params.get("training_cost", 15000),
        
        # Manutenção anual
        "annual_maintenance": params.get("maintenance_cost", 25000),
        "annual_licenses": params.get("licenses_cost", 20000),
    }
    
    # Calcula custo total de implementação
    implementation_cost = (
        costs["sdn_infrastructure"] +
        costs["soar_platform"] +
        costs["servers_hardware"] +
        costs["network_equipment"] +
        (costs["development_months"] * costs["developer_rate_monthly"]) +
        costs["integration_effort"] +
        costs["training_staff"]
    )
    
    annual_operational_cost = (
        costs["annual_maintenance"] +
        costs["annual_licenses"]
    )
    
    # Benefícios
    total_events = len(baseline_logs)
    total_attacks = sum(1 for log in baseline_logs if log.get("is_attack"))
    
    # Redução de tempo de resposta a incidentes
    baseline_auto = sum(1 for log in baseline_logs if log.get("is_attack") and log.get("action") in ["block", "step_up"])
    securebank_auto = sum(1 for log in securebank_logs if log.get("is_attack") and log.get("action") in ["block", "step_up"])
    
    incidents_automated = securebank_auto - baseline_auto
    cost_per_manual_incident = params.get("manual_incident_cost", 500)
    annual_incident_response_savings = incidents_automated * cost_per_manual_incident * params.get("annual_multiplier", 73)  # 365/5
    
    # Prevenção de fraudes
    baseline_allowed_attacks = sum(1 for log in baseline_logs if log.get("is_attack") and log.get("action") == "allow")
    securebank_allowed_attacks = sum(1 for log in securebank_logs if log.get("is_attack") and log.get("action") == "allow")
    
    fraud_prevented = baseline_allowed_attacks - securebank_allowed_attacks
    avg_fraud_value = params.get("avg_fraud_value", 25000)
    annual_fraud_prevention_savings = fraud_prevented * avg_fraud_value * params.get("annual_multiplier", 73)
    
    # Eficiência em compliance
    compliance_savings = params.get("annual_compliance_savings", 50000)
    
    # Redução de falsos positivos
    baseline_false_positives = sum(1 for log in baseline_logs if not log.get("is_attack") and log.get("action") in ["block", "step_up"])
    securebank_false_positives = sum(1 for log in securebank_logs if not log.get("is_attack") and log.get("action") in ["block", "step_up"])
    
    fp_reduction = baseline_false_positives - securebank_false_positives
    cost_per_false_positive = params.get("false_positive_cost", 50)
    annual_false_positive_savings = fp_reduction * cost_per_false_positive * params.get("annual_multiplier", 73)
    
    # Total de benefícios anuais
    total_annual_benefits = (
        annual_incident_response_savings +
        annual_fraud_prevention_savings +
        compliance_savings +
        annual_false_positive_savings
    )
    
    net_annual_benefit = total_annual_benefits - annual_operational_cost
    
    # ROI e Payback Period
    roi_year1 = ((net_annual_benefit - implementation_cost) / implementation_cost) * 100
    roi_year3 = ((3 * net_annual_benefit - implementation_cost) / implementation_cost) * 100
    roi_year5 = ((5 * net_annual_benefit - implementation_cost) / implementation_cost) * 100
    
    payback_months = (implementation_cost / net_annual_benefit * 12) if net_annual_benefit > 0 else float('inf')
    
    return {
        "costs": {
            "implementation": implementation_cost,
            "annual_operational": annual_operational_cost,
            "breakdown": costs
        },
        "benefits": {
            "incident_response_savings": annual_incident_response_savings,
            "fraud_prevention_savings": annual_fraud_prevention_savings,
            "compliance_savings": compliance_savings,
            "false_positive_savings": annual_false_positive_savings,
            "total_annual": total_annual_benefits,
            "net_annual": net_annual_benefit
        },
        "metrics": {
            "incidents_automated": incidents_automated,
            "fraud_prevented": fraud_prevented,
            "fp_reduction": fp_reduction
        },
        "roi": {
            "year_1": roi_year1,
            "year_3": roi_year3,
            "year_5": roi_year5,
            "payback_months": payback_months,
            "payback_years": payback_months / 12
        }
    }


# =========================================================================
# 2. ANÁLISE DE FALSOS POSITIVOS / NEGATIVOS
# =========================================================================

def compute_confusion_matrix(logs: List[Dict]) -> Dict[str, int]:
    """
    Calcula matriz de confusão para um conjunto de logs.
    
    Returns:
        Dict com TP, TN, FP, FN
    """
    tp = 0  # True Positive: ataque bloqueado
    tn = 0  # True Negative: transação legítima permitida
    fp = 0  # False Positive: transação legítima bloqueada
    fn = 0  # False Negative: ataque permitido
    
    for log in logs:
        is_attack = log.get("is_attack", False)
        action = log.get("action", "allow")
        blocked = action in ["block", "step_up"]
        
        if is_attack and blocked:
            tp += 1
        elif not is_attack and not blocked:
            tn += 1
        elif not is_attack and blocked:
            fp += 1
        elif is_attack and not blocked:
            fn += 1
    
    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn
    }


def compute_classification_metrics(confusion_matrix: Dict[str, int]) -> Dict[str, float]:
    """
    Calcula métricas de classificação a partir da matriz de confusão.
    
    Returns:
        Dict com precision, recall, f1-score, accuracy, etc.
    """
    tp = confusion_matrix["TP"]
    tn = confusion_matrix["TN"]
    fp = confusion_matrix["FP"]
    fn = confusion_matrix["FN"]
    
    # Precision: TP / (TP + FP)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    # Recall (Sensitivity, True Positive Rate): TP / (TP + FN)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # F1-Score: 2 * (precision * recall) / (precision + recall)
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Accuracy: (TP + TN) / (TP + TN + FP + FN)
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    
    # Specificity (True Negative Rate): TN / (TN + FP)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    # False Positive Rate: FP / (FP + TN)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    # False Negative Rate: FN / (FN + TP)
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "accuracy": accuracy,
        "specificity": specificity,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr
    }


def compute_false_positive_negative_analysis(
    baseline_logs: List[Dict],
    securebank_logs: List[Dict],
    params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Análise completa de falsos positivos e negativos.
    
    Returns:
        Dict com matrizes de confusão, métricas e impacto financeiro
    """
    if params is None:
        params = {}
    
    # Matrizes de confusão
    baseline_cm = compute_confusion_matrix(baseline_logs)
    securebank_cm = compute_confusion_matrix(securebank_logs)
    
    # Métricas de classificação
    baseline_metrics = compute_classification_metrics(baseline_cm)
    securebank_metrics = compute_classification_metrics(securebank_cm)
    
    # Impacto financeiro
    cost_per_fp = params.get("cost_per_false_positive", 50)  # Custo de revisão manual
    cost_per_fn = params.get("cost_per_false_negative", 25000)  # Custo médio de fraude
    
    baseline_fp_cost = baseline_cm["FP"] * cost_per_fp
    baseline_fn_cost = baseline_cm["FN"] * cost_per_fn
    baseline_total_cost = baseline_fp_cost + baseline_fn_cost
    
    securebank_fp_cost = securebank_cm["FP"] * cost_per_fp
    securebank_fn_cost = securebank_cm["FN"] * cost_per_fn
    securebank_total_cost = securebank_fp_cost + securebank_fn_cost
    
    cost_savings = baseline_total_cost - securebank_total_cost
    cost_reduction_pct = (cost_savings / baseline_total_cost * 100) if baseline_total_cost > 0 else 0.0
    
    # Net Benefit: Benefício - Custo de FPs
    baseline_net_benefit = (baseline_cm["TP"] * cost_per_fn) - baseline_fp_cost
    securebank_net_benefit = (securebank_cm["TP"] * cost_per_fn) - securebank_fp_cost
    
    return {
        "baseline": {
            "confusion_matrix": baseline_cm,
            "metrics": baseline_metrics,
            "financial_impact": {
                "fp_cost": baseline_fp_cost,
                "fn_cost": baseline_fn_cost,
                "total_cost": baseline_total_cost,
                "net_benefit": baseline_net_benefit
            }
        },
        "securebank": {
            "confusion_matrix": securebank_cm,
            "metrics": securebank_metrics,
            "financial_impact": {
                "fp_cost": securebank_fp_cost,
                "fn_cost": securebank_fn_cost,
                "total_cost": securebank_total_cost,
                "net_benefit": securebank_net_benefit
            }
        },
        "improvement": {
            "cost_savings": cost_savings,
            "cost_reduction_pct": cost_reduction_pct,
            "net_benefit_improvement": securebank_net_benefit - baseline_net_benefit,
            "precision_improvement": securebank_metrics["precision"] - baseline_metrics["precision"],
            "recall_improvement": securebank_metrics["recall"] - baseline_metrics["recall"],
            "f1_improvement": securebank_metrics["f1_score"] - baseline_metrics["f1_score"]
        }
    }


# =========================================================================
# 3. ANÁLISE DE ESCALABILIDADE
# =========================================================================

def compute_scalability_analysis(
    simulator_func,
    config: Dict[str, Any],
    load_levels: List[int] = None
) -> Dict[str, Any]:
    """
    Simula diferentes cargas de transações e mede performance.
    
    Args:
        simulator_func: Função de simulação (run_simulation)
        config: Configuração base
        load_levels: Lista de cargas a testar (tx/dia)
    
    Returns:
        Dict com métricas de escalabilidade por carga
    """
    if load_levels is None:
        load_levels = [1000, 5000, 10000, 50000, 100000]
    
    import time
    import copy
    
    results = {}
    
    for load in load_levels:
        print(f"Testing load: {load} transactions...")
        
        # Ajusta configuração para esta carga
        test_config = copy.deepcopy(config)
        test_config["num_events"] = load
        
        # Mede tempo de execução
        start_time = time.time()
        baseline_logs, securebank_logs = simulator_func(test_config)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Calcula latências (simuladas baseadas na complexidade)
        num_events = len(securebank_logs)
        
        # Latência média por transação (ms)
        avg_latency_ms = (execution_time / num_events) * 1000 if num_events > 0 else 0
        
        # Simula latências P95 e P99 (aproximação baseada em complexidade)
        # Para SecureBank, assume overhead de ~4-5x vs baseline
        p95_latency_ms = avg_latency_ms * 1.8
        p99_latency_ms = avg_latency_ms * 2.5
        
        # Throughput (transações/segundo)
        throughput = num_events / execution_time if execution_time > 0 else 0
        
        # Simula uso de recursos (baseado na carga)
        # CPU: assume crescimento linear com algumas otimizações
        cpu_usage_pct = min(95, (load / 100000) * 85)
        
        # Memória: assume crescimento sub-linear (cache effects)
        memory_gb = 0.5 + (load / 100000) * 7.5
        
        results[load] = {
            "execution_time_s": execution_time,
            "num_events": num_events,
            "avg_latency_ms": avg_latency_ms,
            "p95_latency_ms": p95_latency_ms,
            "p99_latency_ms": p99_latency_ms,
            "throughput_tps": throughput,
            "cpu_usage_pct": cpu_usage_pct,
            "memory_gb": memory_gb
        }
    
    # Identifica gargalos
    bottlenecks = []
    for load, metrics in results.items():
        if metrics["avg_latency_ms"] > 100:
            bottlenecks.append(f"Latency exceeds 100ms at {load} tx/day")
        if metrics["cpu_usage_pct"] > 80:
            bottlenecks.append(f"CPU usage exceeds 80% at {load} tx/day")
        if metrics["memory_gb"] > 8:
            bottlenecks.append(f"Memory usage exceeds 8GB at {load} tx/day")
    
    # Recomendações de escala
    recommendations = []
    max_load = max(load_levels)
    max_metrics = results[max_load]
    
    if max_metrics["cpu_usage_pct"] > 70:
        recommendations.append("Consider horizontal scaling with load balancer")
    if max_metrics["memory_gb"] > 6:
        recommendations.append("Implement caching layer (Redis/Memcached)")
    if max_metrics["avg_latency_ms"] > 50:
        recommendations.append("Optimize PDP evaluation pipeline")
    
    recommendations.append("Deploy in Kubernetes for auto-scaling")
    recommendations.append("Use database read replicas for high-load scenarios")
    
    return {
        "load_levels": load_levels,
        "results": results,
        "bottlenecks": bottlenecks,
        "recommendations": recommendations
    }


# =========================================================================
# 4. ANÁLISE DE SENSIBILIDADE
# =========================================================================

def compute_sensitivity_analysis(
    simulator_func,
    config: Dict[str, Any],
    param_ranges: Dict[str, List[float]] = None,
    num_samples: int = 5
) -> Dict[str, Any]:
    """
    Analisa sensibilidade dos parâmetros principais do SecureBank™.
    
    Args:
        simulator_func: Função de simulação
        config: Configuração base
        param_ranges: Dicionário de parâmetros e seus ranges de variação
        num_samples: Número de amostras por parâmetro
    
    Returns:
        Dict com análise de sensibilidade
    """
    import copy
    from metrics import compute_tii, compute_sae, compute_ital
    
    if param_ranges is None:
        # Parâmetros padrão para testar (variação de ±20%)
        param_ranges = {
            "identity_drift_factor": [0.64, 0.72, 0.80, 0.88, 0.96],
            "trust_decay": [0.096, 0.108, 0.12, 0.132, 0.144],
            "trust_growth": [0.20, 0.225, 0.25, 0.275, 0.30],
            "ctx_weight": [0.20, 0.225, 0.25, 0.275, 0.30],
            "transaction_weight": [0.20, 0.225, 0.25, 0.275, 0.30],
            "device_weight": [0.20, 0.225, 0.25, 0.275, 0.30],
        }
    
    results = {}
    
    for param_name, param_values in param_ranges.items():
        print(f"Testing sensitivity for parameter: {param_name}")
        
        param_results = []
        
        for param_value in param_values:
            # Clona configuração
            test_config = copy.deepcopy(config)
            
            # Ajusta o parâmetro específico
            if param_name in ["identity_drift_factor", "trust_decay", "trust_growth", 
                            "ctx_weight", "transaction_weight", "device_weight"]:
                test_config["ital_params"][param_name] = param_value
            else:
                test_config[param_name] = param_value
            
            # Roda simulação
            baseline_logs, securebank_logs = simulator_func(test_config)
            
            # Calcula métricas
            tii = compute_tii(securebank_logs)
            sae = compute_sae(securebank_logs)
            ital = compute_ital(securebank_logs, test_config.get("ital_params", {}))
            
            param_results.append({
                "param_value": param_value,
                "tii": tii,
                "sae": sae,
                "ital": ital
            })
        
        results[param_name] = param_results
    
    # Calcula sensibilidade (variação das métricas)
    sensitivity_scores = {}
    
    for param_name, param_results in results.items():
        tii_values = [r["tii"] for r in param_results]
        sae_values = [r["sae"] for r in param_results]
        ital_values = [r["ital"] for r in param_results]
        
        # Calcula coeficiente de variação (CV = std/mean)
        tii_sensitivity = (statistics.stdev(tii_values) / statistics.mean(tii_values)) if statistics.mean(tii_values) > 0 else 0
        sae_sensitivity = (statistics.stdev(sae_values) / statistics.mean(sae_values)) if statistics.mean(sae_values) > 0 else 0
        ital_sensitivity = (statistics.stdev(ital_values) / statistics.mean(ital_values)) if statistics.mean(ital_values) > 0 else 0
        
        # Score agregado
        aggregate_sensitivity = (tii_sensitivity + sae_sensitivity + ital_sensitivity) / 3
        
        sensitivity_scores[param_name] = {
            "tii_sensitivity": tii_sensitivity,
            "sae_sensitivity": sae_sensitivity,
            "ital_sensitivity": ital_sensitivity,
            "aggregate_sensitivity": aggregate_sensitivity
        }
    
    # Identifica parâmetros mais sensíveis
    sorted_params = sorted(
        sensitivity_scores.items(),
        key=lambda x: x[1]["aggregate_sensitivity"],
        reverse=True
    )
    
    critical_params = [p[0] for p in sorted_params[:3]]
    
    # Recomendações de tuning
    recommendations = []
    for param_name in critical_params:
        recommendations.append(
            f"Parameter '{param_name}' is highly sensitive - requires careful tuning"
        )
    
    recommendations.append("Use grid search or Bayesian optimization for fine-tuning")
    recommendations.append("Monitor these parameters closely in production")
    
    return {
        "param_ranges": param_ranges,
        "results": results,
        "sensitivity_scores": sensitivity_scores,
        "critical_parameters": critical_params,
        "recommendations": recommendations
    }


# =========================================================================
# RUNNER PARA TODAS AS ANÁLISES
# =========================================================================

def run_all_advanced_analyses(
    simulator_func,
    config: Dict[str, Any],
    baseline_logs: List[Dict] = None,
    securebank_logs: List[Dict] = None,
    run_scalability: bool = True,
    run_sensitivity: bool = True
) -> Dict[str, Any]:
    """
    Executa todas as 4 análises avançadas.
    
    Args:
        simulator_func: Função de simulação
        config: Configuração base
        baseline_logs: Logs baseline (se já disponíveis)
        securebank_logs: Logs SecureBank (se já disponíveis)
        run_scalability: Se deve executar análise de escalabilidade (demorada)
        run_sensitivity: Se deve executar análise de sensibilidade (demorada)
    
    Returns:
        Dict com todas as análises
    """
    print("\n" + "="*70)
    print("ADVANCED ANALYSES FOR SECUREBANK™")
    print("="*70)
    
    # Se logs não foram fornecidos, roda simulação
    if baseline_logs is None or securebank_logs is None:
        print("\nRunning baseline simulation...")
        baseline_logs, securebank_logs = simulator_func(config)
    
    results = {}
    
    # 1. ROI Analysis
    print("\n[1/4] Computing Cost-Benefit / ROI Analysis...")
    results["roi"] = compute_roi_analysis(baseline_logs, securebank_logs)
    print(f"  ✓ ROI Year 1: {results['roi']['roi']['year_1']:.1f}%")
    print(f"  ✓ Payback Period: {results['roi']['roi']['payback_months']:.1f} months")
    
    # 2. False Positive/Negative Analysis
    print("\n[2/4] Computing False Positive/Negative Analysis...")
    results["fp_fn"] = compute_false_positive_negative_analysis(baseline_logs, securebank_logs)
    print(f"  ✓ SecureBank F1-Score: {results['fp_fn']['securebank']['metrics']['f1_score']:.3f}")
    print(f"  ✓ Cost Reduction: {results['fp_fn']['improvement']['cost_reduction_pct']:.1f}%")
    
    # 3. Scalability Analysis
    if run_scalability:
        print("\n[3/4] Computing Scalability Analysis...")
        results["scalability"] = compute_scalability_analysis(
            simulator_func,
            config,
            load_levels=[1000, 5000, 10000, 50000, 100000]
        )
        max_load = max(results["scalability"]["load_levels"])
        max_latency = results["scalability"]["results"][max_load]["avg_latency_ms"]
        print(f"  ✓ Max Load Tested: {max_load:,} tx/day")
        print(f"  ✓ Latency at Max Load: {max_latency:.2f} ms")
    else:
        print("\n[3/4] Skipping Scalability Analysis (run_scalability=False)")
        results["scalability"] = None
    
    # 4. Sensitivity Analysis
    if run_sensitivity:
        print("\n[4/4] Computing Sensitivity Analysis...")
        results["sensitivity"] = compute_sensitivity_analysis(
            simulator_func,
            config,
            num_samples=5
        )
        print(f"  ✓ Critical Parameters: {', '.join(results['sensitivity']['critical_parameters'])}")
    else:
        print("\n[4/4] Skipping Sensitivity Analysis (run_sensitivity=False)")
        results["sensitivity"] = None
    
    print("\n" + "="*70)
    print("ADVANCED ANALYSES COMPLETED")
    print("="*70 + "\n")
    
    return results
