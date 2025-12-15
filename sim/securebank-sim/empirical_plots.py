"""
empirical_plots.py

Gera visualizações comparativas entre resultados da simulação e dados reais
para validação empírica do SecureBank™.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any

# Configuração de estilo para artigos científicos
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


def plot_metrics_comparison(
    real_metrics: Dict[str, Any],
    simulation_metrics: Dict[str, Any],
    output_path: str
) -> None:
    """
    Gera gráfico de barras comparando métricas reais vs. simuladas.
    
    Args:
        real_metrics: Métricas dos dados reais
        simulation_metrics: Métricas da simulação
        output_path: Caminho para salvar o gráfico
    """
    metrics = ['TII', 'SAE', 'ITAL']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Simulation vs. Real Data: Metrics Comparison', fontsize=14, fontweight='bold')
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        # Dados
        baseline_sim = simulation_metrics[metric]['baseline']
        baseline_real = real_metrics[metric]['baseline']
        sb_sim = simulation_metrics[metric]['securebank']
        sb_real = real_metrics[metric]['securebank']
        
        # Posições das barras
        x = np.arange(2)
        width = 0.35
        
        # Barras
        bars1 = ax.bar(x - width/2, [baseline_sim, sb_sim], width, 
                       label='Simulation', alpha=0.8, color='#3498db')
        bars2 = ax.bar(x + width/2, [baseline_real, sb_real], width,
                       label='Real Data', alpha=0.8, color='#e74c3c')
        
        # Configuração
        ax.set_ylabel(metric, fontsize=11)
        ax.set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['Baseline', 'SecureBank™'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def plot_correlation_scatter(
    correlation: Dict[str, Any],
    output_path: str
) -> None:
    """
    Gera scatter plots mostrando correlação entre simulação e dados reais.
    
    Args:
        correlation: Dados de correlação
        output_path: Caminho para salvar o gráfico
    """
    metrics = ['TII', 'SAE', 'ITAL']
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Correlation: Simulation vs. Real Data', fontsize=14, fontweight='bold')
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        sim_vals = correlation[metric]['simulation_values']
        real_vals = correlation[metric]['real_values']
        r = correlation[metric]['pearson_r']
        p = correlation[metric]['p_value']
        
        # Scatter plot
        ax.scatter(sim_vals, real_vals, s=150, alpha=0.7, 
                  color=['#3498db', '#e74c3c'], edgecolors='black', linewidth=1.5)
        
        # Linha de identidade (y = x)
        min_val = min(min(sim_vals), min(real_vals))
        max_val = max(max(sim_vals), max(real_vals))
        ax.plot([min_val, max_val], [min_val, max_val], 
               'k--', alpha=0.5, label='Perfect correlation (y=x)')
        
        # Linha de regressão
        z = np.polyfit(sim_vals, real_vals, 1)
        p_fit = np.poly1d(z)
        x_line = np.linspace(min_val, max_val, 100)
        ax.plot(x_line, p_fit(x_line), 'g-', alpha=0.7, linewidth=2, label='Regression line')
        
        # Configuração
        ax.set_xlabel('Simulation', fontsize=11)
        ax.set_ylabel('Real Data', fontsize=11)
        ax.set_title(f'{metric}: r={r:.4f}, p={p:.4f}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        
        # Anotações
        ax.text(0.05, 0.95, f'Pearson r = {r:.4f}\np-value = {p:.4f}',
               transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def plot_improvement_comparison(
    real_metrics: Dict[str, Any],
    simulation_metrics: Dict[str, Any],
    output_path: str
) -> None:
    """
    Compara melhorias percentuais (SecureBank vs. Baseline) em simulação e dados reais.
    
    Args:
        real_metrics: Métricas dos dados reais
        simulation_metrics: Métricas da simulação
        output_path: Caminho para salvar o gráfico
    """
    metrics = ['TII', 'SAE', 'ITAL']
    
    # Calcula melhorias percentuais
    improvements_sim = []
    improvements_real = []
    
    for metric in metrics:
        # Simulação
        baseline_sim = simulation_metrics[metric]['baseline']
        sb_sim = simulation_metrics[metric]['securebank']
        improvement_sim = ((sb_sim - baseline_sim) / baseline_sim * 100) if baseline_sim > 0 else 0
        improvements_sim.append(improvement_sim)
        
        # Real
        improvement_real = real_metrics[metric]['improvement']
        improvements_real.append(improvement_real)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, improvements_sim, width, 
                   label='Simulation', alpha=0.8, color='#3498db')
    bars2 = ax.bar(x + width/2, improvements_real, width,
                   label='Real Data', alpha=0.8, color='#e74c3c')
    
    # Configuração
    ax.set_ylabel('Improvement (%)', fontsize=12)
    ax.set_title('Performance Improvement: SecureBank™ vs. Baseline\n(Simulation vs. Real Data)',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    
    # Adiciona valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom' if height >= 0 else 'top', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def plot_distribution_comparison(
    real_logs: list,
    simulation_logs: list,
    output_path: str
) -> None:
    """
    Compara distribuições de valores de transação entre simulação e dados reais.
    
    Args:
        real_logs: Logs dos dados reais
        simulation_logs: Logs da simulação
        output_path: Caminho para salvar o gráfico
    """
    # Extrai valores
    real_amounts = [log['tx']['amount'] for log in real_logs]
    sim_amounts = [log['tx']['amount'] for log in simulation_logs]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Distribution Comparison: Simulation vs. Real Data', fontsize=14, fontweight='bold')
    
    # 1. Histogramas
    ax = axes[0, 0]
    ax.hist(sim_amounts, bins=50, alpha=0.6, label='Simulation', density=True, color='#3498db')
    ax.hist(real_amounts, bins=50, alpha=0.6, label='Real Data', density=True, color='#e74c3c')
    ax.set_xlabel('Transaction Amount ($)', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.set_title('Transaction Amount Distribution', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Box plots
    ax = axes[0, 1]
    bp = ax.boxplot([sim_amounts, real_amounts],
                    labels=['Simulation', 'Real Data'],
                    patch_artist=True,
                    widths=0.6)
    colors = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_ylabel('Transaction Amount ($)', fontsize=11)
    ax.set_title('Transaction Amount Box Plot', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # 3. CDF (Cumulative Distribution Function)
    ax = axes[1, 0]
    sorted_sim = np.sort(sim_amounts)
    sorted_real = np.sort(real_amounts)
    cdf_sim = np.arange(1, len(sorted_sim)+1) / len(sorted_sim)
    cdf_real = np.arange(1, len(sorted_real)+1) / len(sorted_real)
    ax.plot(sorted_sim, cdf_sim, label='Simulation', color='#3498db', linewidth=2)
    ax.plot(sorted_real, cdf_real, label='Real Data', color='#e74c3c', linewidth=2)
    ax.set_xlabel('Transaction Amount ($)', fontsize=11)
    ax.set_ylabel('Cumulative Probability', fontsize=11)
    ax.set_title('Cumulative Distribution Function (CDF)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 4. Q-Q Plot
    ax = axes[1, 1]
    # Normaliza para quantis
    sim_quantiles = np.percentile(sim_amounts, np.arange(0, 101, 1))
    real_quantiles = np.percentile(real_amounts, np.arange(0, 101, 1))
    ax.scatter(sim_quantiles, real_quantiles, alpha=0.6, s=30, color='#2ecc71')
    # Linha de identidade
    min_val = min(min(sim_quantiles), min(real_quantiles))
    max_val = max(max(sim_quantiles), max(real_quantiles))
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect match')
    ax.set_xlabel('Simulation Quantiles ($)', fontsize=11)
    ax.set_ylabel('Real Data Quantiles ($)', fontsize=11)
    ax.set_title('Q-Q Plot', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def plot_attack_detection_comparison(
    real_scenario_detection: Dict,
    sim_scenario_detection: Dict,
    output_path: str
) -> None:
    """
    Compara taxas de detecção de ataques por cenário entre simulação e dados reais.
    
    Args:
        real_scenario_detection: Detecção por cenário (dados reais)
        sim_scenario_detection: Detecção por cenário (simulação)
        output_path: Caminho para salvar o gráfico
    """
    # Extrai cenários comuns
    scenarios = sorted(set(real_scenario_detection.keys()) & set(sim_scenario_detection.keys()))
    
    if not scenarios:
        print("⚠ No common scenarios found for comparison")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Attack Detection by Scenario: Simulation vs. Real Data', fontsize=14, fontweight='bold')
    
    # Baseline
    ax = axes[0]
    scenario_names = [real_scenario_detection[s]['name'] for s in scenarios]
    
    # Taxa de bloqueio baseline
    baseline_sim_blocked = [
        (sim_scenario_detection[s]['baseline']['blocked'] / sim_scenario_detection[s]['total_attacks'] * 100)
        if sim_scenario_detection[s]['total_attacks'] > 0 else 0
        for s in scenarios
    ]
    baseline_real_blocked = [
        (real_scenario_detection[s]['baseline']['blocked'] / real_scenario_detection[s]['total_attacks'] * 100)
        if real_scenario_detection[s]['total_attacks'] > 0 else 0
        for s in scenarios
    ]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    ax.bar(x - width/2, baseline_sim_blocked, width, label='Simulation', alpha=0.8, color='#3498db')
    ax.bar(x + width/2, baseline_real_blocked, width, label='Real Data', alpha=0.8, color='#e74c3c')
    ax.set_ylabel('Blocked Rate (%)', fontsize=11)
    ax.set_title('Baseline PDP: Attack Detection', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # SecureBank
    ax = axes[1]
    
    # Taxa de bloqueio SecureBank
    sb_sim_blocked = [
        (sim_scenario_detection[s]['securebank']['blocked'] / sim_scenario_detection[s]['total_attacks'] * 100)
        if sim_scenario_detection[s]['total_attacks'] > 0 else 0
        for s in scenarios
    ]
    sb_real_blocked = [
        (real_scenario_detection[s]['securebank']['blocked'] / real_scenario_detection[s]['total_attacks'] * 100)
        if real_scenario_detection[s]['total_attacks'] > 0 else 0
        for s in scenarios
    ]
    
    ax.bar(x - width/2, sb_sim_blocked, width, label='Simulation', alpha=0.8, color='#3498db')
    ax.bar(x + width/2, sb_real_blocked, width, label='Real Data', alpha=0.8, color='#e74c3c')
    ax.set_ylabel('Blocked Rate (%)', fontsize=11)
    ax.set_title('SecureBank™ PDP: Attack Detection', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def plot_validation_summary_table(
    correlation: Dict[str, Any],
    output_path: str
) -> None:
    """
    Gera tabela visual resumindo a validação empírica.
    
    Args:
        correlation: Dados de correlação
        output_path: Caminho para salvar a imagem da tabela
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Dados da tabela
    metrics = ['TII', 'SAE', 'ITAL', 'Overall']
    
    table_data = []
    for metric in metrics:
        if metric == 'Overall':
            row = [
                'OVERALL',
                f"{correlation['overall']['mean_pearson_r']:.4f}",
                correlation['overall']['interpretation'],
                f"{correlation['overall']['mean_absolute_error']:.4f}",
                f"{correlation['overall']['mean_relative_error_pct']:.2f}%",
                '✓' if correlation['overall']['mean_pearson_r'] >= 0.70 else '✗'
            ]
        else:
            row = [
                metric,
                f"{correlation[metric]['pearson_r']:.4f}",
                '✓ Sig.' if correlation[metric]['is_significant'] else '✗ Not sig.',
                f"{correlation[metric]['mean_absolute_error']:.4f}",
                f"{correlation[metric]['mean_relative_error_pct']:.2f}%",
                '✓' if abs(correlation[metric]['pearson_r']) >= 0.70 else '✗'
            ]
        table_data.append(row)
    
    # Cria tabela
    table = ax.table(cellText=table_data,
                    colLabels=['Metric', 'Pearson r', 'Significance', 'MAE', 'MRE', 'Valid (r≥0.70)'],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.12, 0.12, 0.18, 0.12, 0.12, 0.18])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Estilização
    for i in range(len(metrics) + 1):
        for j in range(6):
            cell = table[(i, j)]
            if i == 0:  # Header
                cell.set_facecolor('#3498db')
                cell.set_text_props(weight='bold', color='white')
            elif i == len(metrics):  # Overall row
                cell.set_facecolor('#2ecc71' if j == 5 and '✓' in table_data[i-1][j] else '#e8f4f8')
                cell.set_text_props(weight='bold')
            else:
                cell.set_facecolor('#ffffff' if i % 2 == 0 else '#f7f9fa')
    
    plt.title('Empirical Validation Summary', fontsize=14, fontweight='bold', pad=20)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")


def generate_all_empirical_plots(
    empirical_results_dir: str,
    simulation_results_dir: str,
    output_dir: str
) -> None:
    """
    Gera todos os gráficos de validação empírica.
    
    Args:
        empirical_results_dir: Diretório com resultados empíricos
        simulation_results_dir: Diretório com resultados da simulação
        output_dir: Diretório de saída para os gráficos
    """
    print("\n" + "="*70)
    print("Generating Empirical Validation Plots")
    print("="*70)
    
    emp_path = Path(empirical_results_dir)
    sim_path = Path(simulation_results_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Carrega dados
    with open(emp_path / "empirical_metrics.json", 'r') as f:
        metrics_data = json.load(f)
        real_metrics = metrics_data['real_metrics']
        simulation_metrics = metrics_data['simulation_metrics']
    
    with open(emp_path / "empirical_correlation.json", 'r') as f:
        correlation = json.load(f)
    
    with open(emp_path / "empirical_securebank_logs_sample.json", 'r') as f:
        real_logs = json.load(f)
    
    with open(sim_path / "securebank_logs_run0.json", 'r') as f:
        sim_logs = json.load(f)
    
    with open(emp_path / "empirical_scenario_detection.json", 'r') as f:
        real_scenario_detection = json.load(f)
    
    with open(sim_path / "scenario_detection_run0.json", 'r') as f:
        sim_scenario_detection = json.load(f)
    
    # Gera gráficos
    print("\nGenerating plots...")
    
    plot_metrics_comparison(
        real_metrics, simulation_metrics,
        str(out_path / "empirical_metrics_comparison.png")
    )
    
    plot_correlation_scatter(
        correlation,
        str(out_path / "empirical_correlation_scatter.png")
    )
    
    plot_improvement_comparison(
        real_metrics, simulation_metrics,
        str(out_path / "empirical_improvement_comparison.png")
    )
    
    plot_distribution_comparison(
        real_logs, sim_logs,
        str(out_path / "empirical_distribution_comparison.png")
    )
    
    plot_attack_detection_comparison(
        real_scenario_detection, sim_scenario_detection,
        str(out_path / "empirical_attack_detection_comparison.png")
    )
    
    plot_validation_summary_table(
        correlation,
        str(out_path / "empirical_validation_summary.png")
    )
    
    print("\n" + "="*70)
    print(f"All plots saved to: {output_dir}")
    print("="*70)


# CLI
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python empirical_plots.py <empirical_results_dir> <simulation_results_dir> [output_dir]")
        sys.exit(1)
    
    emp_dir = sys.argv[1]
    sim_dir = sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "./empirical_plots"
    
    generate_all_empirical_plots(emp_dir, sim_dir, out_dir)
