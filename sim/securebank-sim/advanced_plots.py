"""
advanced_plots.py

Módulo de visualizações para análises avançadas do SecureBank™:
1. ROI e Payback Period
2. Matriz de Confusão e métricas de classificação
3. Escalabilidade (latência, throughput, recursos)
4. Sensibilidade de parâmetros
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Any, List


# Configuração global do estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# =========================================================================
# 1. VISUALIZAÇÕES DE ROI
# =========================================================================

def plot_roi_analysis(roi_data: Dict[str, Any], output_dir: Path):
    """
    Cria visualizações para análise de ROI.
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 1.1 Gráfico de ROI ao longo dos anos
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = [1, 3, 5]
    roi_values = [
        roi_data["roi"]["year_1"],
        roi_data["roi"]["year_3"],
        roi_data["roi"]["year_5"]
    ]
    
    bars = ax.bar(years, roi_values, color=['#e74c3c', '#3498db', '#2ecc71'], 
                  alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Years', fontsize=12, fontweight='bold')
    ax.set_ylabel('ROI (%)', fontsize=12, fontweight='bold')
    ax.set_title('SecureBank™ Return on Investment (ROI) Over Time', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(years)
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax.grid(True, alpha=0.3)
    
    # Adiciona valores no topo das barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'roi_over_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 1.2 Gráfico de Payback Period
    fig, ax = plt.subplots(figsize=(8, 6))
    
    payback_months = roi_data["roi"]["payback_months"]
    payback_years = roi_data["roi"]["payback_years"]
    
    ax.barh(['Payback Period'], [payback_months], color='#9b59b6', 
            alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Months', fontsize=12, fontweight='bold')
    ax.set_title('SecureBank™ Payback Period', fontsize=14, fontweight='bold')
    ax.text(payback_months/2, 0, f'{payback_months:.1f} months\n({payback_years:.2f} years)',
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'payback_period.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 1.3 Gráfico de Custos vs Benefícios
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Implementation\nCost', 'Annual\nOperational', 'Annual\nBenefits', 'Net Annual\nBenefit']
    values = [
        roi_data["costs"]["implementation"],
        roi_data["costs"]["annual_operational"],
        roi_data["benefits"]["total_annual"],
        roi_data["benefits"]["net_annual"]
    ]
    colors = ['#e74c3c', '#f39c12', '#2ecc71', '#27ae60']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7, 
                  edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('USD ($)', fontsize=12, fontweight='bold')
    ax.set_title('SecureBank™ Cost-Benefit Breakdown', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Formata valores em k
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1000:.1f}K',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cost_benefit_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ ROI plots saved to {output_dir}")


# =========================================================================
# 2. VISUALIZAÇÕES DE FALSOS POSITIVOS/NEGATIVOS
# =========================================================================

def plot_confusion_matrices(fp_fn_data: Dict[str, Any], output_dir: Path):
    """
    Cria visualizações de matrizes de confusão e métricas.
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 2.1 Matrizes de confusão lado a lado
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    for idx, (system, ax) in enumerate(zip(['baseline', 'securebank'], axes)):
        cm = fp_fn_data[system]["confusion_matrix"]
        
        # Matriz 2x2
        matrix = np.array([
            [cm["TP"], cm["FN"]],
            [cm["FP"], cm["TN"]]
        ])
        
        # Heatmap
        sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', cbar=True,
                   xticklabels=['Predicted\nPositive', 'Predicted\nNegative'],
                   yticklabels=['Actual\nPositive', 'Actual\nNegative'],
                   ax=ax, linewidths=2, linecolor='black')
        
        title = 'Baseline System' if system == 'baseline' else 'SecureBank™'
        ax.set_title(f'Confusion Matrix: {title}', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'confusion_matrices.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2.2 Comparação de métricas de classificação
    fig, ax = plt.subplots(figsize=(12, 6))
    
    metrics_names = ['Precision', 'Recall', 'F1-Score', 'Accuracy', 'Specificity']
    baseline_values = [
        fp_fn_data["baseline"]["metrics"]["precision"],
        fp_fn_data["baseline"]["metrics"]["recall"],
        fp_fn_data["baseline"]["metrics"]["f1_score"],
        fp_fn_data["baseline"]["metrics"]["accuracy"],
        fp_fn_data["baseline"]["metrics"]["specificity"]
    ]
    securebank_values = [
        fp_fn_data["securebank"]["metrics"]["precision"],
        fp_fn_data["securebank"]["metrics"]["recall"],
        fp_fn_data["securebank"]["metrics"]["f1_score"],
        fp_fn_data["securebank"]["metrics"]["accuracy"],
        fp_fn_data["securebank"]["metrics"]["specificity"]
    ]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline_values, width, label='Baseline',
                   color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, securebank_values, width, label='SecureBank™',
                   color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Classification Metrics Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adiciona valores
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'classification_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2.3 Impacto financeiro de FP e FN
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['FP Cost', 'FN Cost', 'Total Cost']
    baseline_costs = [
        fp_fn_data["baseline"]["financial_impact"]["fp_cost"],
        fp_fn_data["baseline"]["financial_impact"]["fn_cost"],
        fp_fn_data["baseline"]["financial_impact"]["total_cost"]
    ]
    securebank_costs = [
        fp_fn_data["securebank"]["financial_impact"]["fp_cost"],
        fp_fn_data["securebank"]["financial_impact"]["fn_cost"],
        fp_fn_data["securebank"]["financial_impact"]["total_cost"]
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline_costs, width, label='Baseline',
                   color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, securebank_costs, width, label='SecureBank™',
                   color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Cost (USD)', fontsize=12, fontweight='bold')
    ax.set_title('Financial Impact of False Positives and Negatives', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Formata valores
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height >= 1000:
                label = f'${height/1000:.1f}K'
            else:
                label = f'${height:.0f}'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    label, ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'financial_impact_fp_fn.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ FP/FN plots saved to {output_dir}")


# =========================================================================
# 3. VISUALIZAÇÕES DE ESCALABILIDADE
# =========================================================================

def plot_scalability_analysis(scalability_data: Dict[str, Any], output_dir: Path):
    """
    Cria visualizações de escalabilidade.
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    
    load_levels = scalability_data["load_levels"]
    results = scalability_data["results"]
    
    # Extrai métricas
    latencies_avg = [results[load]["avg_latency_ms"] for load in load_levels]
    latencies_p95 = [results[load]["p95_latency_ms"] for load in load_levels]
    latencies_p99 = [results[load]["p99_latency_ms"] for load in load_levels]
    throughput = [results[load]["throughput_tps"] for load in load_levels]
    cpu_usage = [results[load]["cpu_usage_pct"] for load in load_levels]
    memory_usage = [results[load]["memory_gb"] for load in load_levels]
    
    # 3.1 Latência vs Carga
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(load_levels, latencies_avg, marker='o', linewidth=2, 
            label='Average Latency', color='#3498db')
    ax.plot(load_levels, latencies_p95, marker='s', linewidth=2, 
            label='P95 Latency', color='#f39c12')
    ax.plot(load_levels, latencies_p99, marker='^', linewidth=2, 
            label='P99 Latency', color='#e74c3c')
    
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, 
               label='100ms Threshold', alpha=0.7)
    
    ax.set_xlabel('Transaction Load (tx/day)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_title('SecureBank™ Latency vs Load', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scalability_latency.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3.2 Throughput vs Carga
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(load_levels, throughput, marker='o', linewidth=2, 
            color='#2ecc71', markersize=8)
    
    ax.set_xlabel('Transaction Load (tx/day)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (tx/second)', fontsize=12, fontweight='bold')
    ax.set_title('SecureBank™ Throughput vs Load', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)
    
    # Adiciona valores
    for x, y in zip(load_levels, throughput):
        ax.annotate(f'{y:.1f}', xy=(x, y), xytext=(0, 10),
                   textcoords='offset points', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scalability_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3.3 Uso de recursos (CPU e Memória)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # CPU Usage
    ax1.plot(load_levels, cpu_usage, marker='o', linewidth=2, 
             color='#e74c3c', markersize=8)
    ax1.axhline(y=80, color='orange', linestyle='--', linewidth=2, 
                label='80% Warning Threshold', alpha=0.7)
    ax1.set_xlabel('Transaction Load (tx/day)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('CPU Usage (%)', fontsize=12, fontweight='bold')
    ax1.set_title('CPU Usage vs Load', fontsize=13, fontweight='bold')
    ax1.set_xscale('log')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Memory Usage
    ax2.plot(load_levels, memory_usage, marker='s', linewidth=2, 
             color='#9b59b6', markersize=8)
    ax2.axhline(y=8, color='orange', linestyle='--', linewidth=2, 
                label='8GB Warning Threshold', alpha=0.7)
    ax2.set_xlabel('Transaction Load (tx/day)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Memory Usage (GB)', fontsize=12, fontweight='bold')
    ax2.set_title('Memory Usage vs Load', fontsize=13, fontweight='bold')
    ax2.set_xscale('log')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scalability_resources.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Scalability plots saved to {output_dir}")


# =========================================================================
# 4. VISUALIZAÇÕES DE SENSIBILIDADE
# =========================================================================

def plot_sensitivity_analysis(sensitivity_data: Dict[str, Any], output_dir: Path):
    """
    Cria visualizações de análise de sensibilidade.
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    
    results = sensitivity_data["results"]
    sensitivity_scores = sensitivity_data["sensitivity_scores"]
    
    # 4.1 Heatmap de sensibilidade
    fig, ax = plt.subplots(figsize=(12, 8))
    
    params = list(sensitivity_scores.keys())
    metrics = ["TII", "SAE", "ITAL"]
    
    # Matriz de sensibilidade
    sensitivity_matrix = np.array([
        [sensitivity_scores[p]["tii_sensitivity"] for p in params],
        [sensitivity_scores[p]["sae_sensitivity"] for p in params],
        [sensitivity_scores[p]["ital_sensitivity"] for p in params]
    ])
    
    sns.heatmap(sensitivity_matrix, annot=True, fmt='.4f', cmap='YlOrRd',
               xticklabels=[p.replace('_', '\n') for p in params],
               yticklabels=metrics, ax=ax, cbar_kws={'label': 'Sensitivity Score'},
               linewidths=1, linecolor='black')
    
    ax.set_title('Parameter Sensitivity Heatmap', fontsize=14, fontweight='bold')
    ax.set_xlabel('Parameters', fontsize=12, fontweight='bold')
    ax.set_ylabel('Metrics', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sensitivity_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4.2 Gráficos de sensibilidade por parâmetro (grid)
    num_params = len(results)
    cols = 3
    rows = (num_params + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 4*rows))
    axes = axes.flatten() if num_params > 1 else [axes]
    
    for idx, (param_name, param_results) in enumerate(results.items()):
        ax = axes[idx]
        
        param_values = [r["param_value"] for r in param_results]
        tii_values = [r["tii"] for r in param_results]
        sae_values = [r["sae"] for r in param_results]
        ital_values = [r["ital"] for r in param_results]
        
        ax.plot(param_values, tii_values, marker='o', label='TII', linewidth=2)
        ax.plot(param_values, sae_values, marker='s', label='SAE', linewidth=2)
        ax.plot(param_values, ital_values, marker='^', label='ITAL', linewidth=2)
        
        ax.set_xlabel(param_name.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        ax.set_ylabel('Metric Value', fontsize=10, fontweight='bold')
        ax.set_title(f'Sensitivity: {param_name.replace("_", " ").title()}', 
                    fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    # Remove eixos extras
    for idx in range(num_params, len(axes)):
        fig.delaxes(axes[idx])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sensitivity_parameters.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4.3 Ranking de sensibilidade agregada
    fig, ax = plt.subplots(figsize=(10, 6))
    
    params_sorted = sorted(sensitivity_scores.items(), 
                          key=lambda x: x[1]["aggregate_sensitivity"], 
                          reverse=True)
    
    param_names = [p[0].replace('_', '\n') for p in params_sorted]
    aggregate_scores = [p[1]["aggregate_sensitivity"] for p in params_sorted]
    
    colors = ['#e74c3c' if i < 3 else '#3498db' for i in range(len(param_names))]
    
    bars = ax.barh(param_names, aggregate_scores, color=colors, 
                   alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Aggregate Sensitivity Score', fontsize=12, fontweight='bold')
    ax.set_title('Parameter Sensitivity Ranking', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Adiciona valores
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f'{width:.4f}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sensitivity_ranking.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sensitivity plots saved to {output_dir}")


# =========================================================================
# RUNNER PARA TODAS AS VISUALIZAÇÕES
# =========================================================================

def generate_all_advanced_plots(
    analyses_results: Dict[str, Any],
    output_dir: Path
):
    """
    Gera todas as visualizações avançadas.
    
    Args:
        analyses_results: Resultados das análises avançadas
        output_dir: Diretório de saída para os gráficos
    """
    print("\n" + "="*70)
    print("GENERATING ADVANCED PLOTS")
    print("="*70)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 1. ROI Plots
    if "roi" in analyses_results and analyses_results["roi"]:
        print("\n[1/4] Generating ROI plots...")
        plot_roi_analysis(analyses_results["roi"], output_dir / "roi")
    
    # 2. FP/FN Plots
    if "fp_fn" in analyses_results and analyses_results["fp_fn"]:
        print("\n[2/4] Generating FP/FN plots...")
        plot_confusion_matrices(analyses_results["fp_fn"], output_dir / "fp_fn")
    
    # 3. Scalability Plots
    if "scalability" in analyses_results and analyses_results["scalability"]:
        print("\n[3/4] Generating Scalability plots...")
        plot_scalability_analysis(analyses_results["scalability"], output_dir / "scalability")
    
    # 4. Sensitivity Plots
    if "sensitivity" in analyses_results and analyses_results["sensitivity"]:
        print("\n[4/4] Generating Sensitivity plots...")
        plot_sensitivity_analysis(analyses_results["sensitivity"], output_dir / "sensitivity")
    
    print("\n" + "="*70)
    print(f"ALL PLOTS SAVED TO: {output_dir}")
    print("="*70 + "\n")
