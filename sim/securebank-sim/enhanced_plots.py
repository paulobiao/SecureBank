"""
enhanced_plots.py

Módulo de visualização avançada com significância estatística para SecureBank™.
Gera gráficos de barras, boxplots e violin plots com anotações de significância,
intervalos de confiança e p-values para publicação científica.

Autor: SecureBank Research Team
Data: 2025-12-12
"""

from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
import seaborn as sns
from statistical_analysis import StatisticalTestResult, significance_stars, format_p_value


# Configuração de estilo para publicação científica
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")

# Cores para publicação
COLOR_BASELINE = "#E74C3C"  # Vermelho
COLOR_SECUREBANK = "#3498DB"  # Azul
COLOR_CI = "#95a5a6"  # Cinza


def plot_comparison_bars_with_significance(
    baseline_data: Dict[str, List[float]],
    securebank_data: Dict[str, List[float]],
    statistical_results: Dict[str, StatisticalTestResult],
    output_path: Path,
    figsize: Tuple[int, int] = (12, 6),
    dpi: int = 300
):
    """
    Gera gráfico de barras comparativo com barras de erro (IC 95%) e significância.
    
    Args:
        baseline_data: Dict com dados baseline {"TII": [...], "SAE": [...], "ITAL": [...]}
        securebank_data: Dict com dados SecureBank™
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_path: Caminho para salvar a figura
        figsize: Tamanho da figura (largura, altura)
        dpi: Resolução da figura
    """
    metrics = list(baseline_data.keys())
    n_metrics = len(metrics)
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    x = np.arange(n_metrics)
    width = 0.35
    
    # Calcula médias e intervalos de confiança
    baseline_means = []
    baseline_errors = []
    securebank_means = []
    securebank_errors = []
    
    for metric in metrics:
        result = statistical_results[metric]
        
        baseline_means.append(result.baseline_mean)
        securebank_means.append(result.securebank_mean)
        
        # Erro = metade da largura do IC
        ci_lower, ci_upper = result.confidence_interval
        ci_width = ci_upper - ci_lower
        baseline_errors.append(ci_width / 2)
        securebank_errors.append(ci_width / 2)
    
    # Plota barras
    bars1 = ax.bar(
        x - width/2, baseline_means, width, 
        label='Baseline', 
        color=COLOR_BASELINE, 
        alpha=0.8,
        yerr=baseline_errors,
        capsize=5,
        error_kw={'linewidth': 2, 'ecolor': COLOR_CI}
    )
    
    bars2 = ax.bar(
        x + width/2, securebank_means, width, 
        label='SecureBank™', 
        color=COLOR_SECUREBANK, 
        alpha=0.8,
        yerr=securebank_errors,
        capsize=5,
        error_kw={'linewidth': 2, 'ecolor': COLOR_CI}
    )
    
    # Adiciona anotações de significância
    y_max = max(max(baseline_means), max(securebank_means)) * 1.15
    
    for i, metric in enumerate(metrics):
        result = statistical_results[metric]
        sig = significance_stars(result.p_value)
        p_str = format_p_value(result.p_value)
        
        # Altura da anotação
        y_pos = max(baseline_means[i] + baseline_errors[i], 
                    securebank_means[i] + securebank_errors[i]) * 1.05
        
        # Linha horizontal indicando comparação
        ax.plot([i - width/2, i + width/2], [y_pos, y_pos], 'k-', linewidth=1.5)
        
        # Texto com significância
        if sig != "ns":
            ax.text(i, y_pos * 1.03, f'{sig}\n{p_str}', 
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            ax.text(i, y_pos * 1.03, f'ns\n{p_str}', 
                   ha='center', va='bottom', fontsize=9, color='gray')
    
    # Configurações dos eixos
    ax.set_ylabel('Metric Value', fontsize=14, fontweight='bold')
    ax.set_xlabel('Metrics', fontsize=14, fontweight='bold')
    ax.set_title('SecureBank™ vs. Baseline: Statistical Comparison', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=12)
    ax.legend(fontsize=12, loc='upper left')
    ax.set_ylim(0, y_max)
    
    # Grid suave
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico de barras com significância salvo: {output_path}")


def plot_boxplots_comparison(
    baseline_data: Dict[str, List[float]],
    securebank_data: Dict[str, List[float]],
    statistical_results: Dict[str, StatisticalTestResult],
    output_path: Path,
    figsize: Tuple[int, int] = (14, 5),
    dpi: int = 300
):
    """
    Gera boxplots comparativos para cada métrica com anotações de significância.
    
    Args:
        baseline_data: Dict com dados baseline
        securebank_data: Dict com dados SecureBank™
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_path: Caminho para salvar a figura
        figsize: Tamanho da figura
        dpi: Resolução da figura
    """
    metrics = list(baseline_data.keys())
    n_metrics = len(metrics)
    
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize, dpi=dpi)
    
    if n_metrics == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        result = statistical_results[metric]
        
        # Prepara dados para boxplot
        data_to_plot = [baseline_data[metric], securebank_data[metric]]
        
        # Cria boxplot
        bp = ax.boxplot(
            data_to_plot,
            labels=['Baseline', 'SecureBank™'],
            patch_artist=True,
            widths=0.6,
            showmeans=True,
            meanprops=dict(marker='D', markerfacecolor='yellow', markeredgecolor='black', markersize=8)
        )
        
        # Colorir boxes
        bp['boxes'][0].set_facecolor(COLOR_BASELINE)
        bp['boxes'][0].set_alpha(0.7)
        bp['boxes'][1].set_facecolor(COLOR_SECUREBANK)
        bp['boxes'][1].set_alpha(0.7)
        
        # Adiciona pontos individuais (strip plot)
        for i, data in enumerate(data_to_plot):
            y = data
            x = np.random.normal(i + 1, 0.04, size=len(y))
            ax.scatter(x, y, alpha=0.3, s=20, color='black')
        
        # Anotação de significância
        sig = significance_stars(result.p_value)
        p_str = format_p_value(result.p_value)
        
        y_max = max(max(baseline_data[metric]), max(securebank_data[metric]))
        y_min = min(min(baseline_data[metric]), min(securebank_data[metric]))
        y_range = y_max - y_min
        y_pos = y_max + y_range * 0.1
        
        # Linha horizontal de comparação
        ax.plot([1, 2], [y_pos, y_pos], 'k-', linewidth=1.5)
        
        # Texto de significância
        if sig != "ns":
            ax.text(1.5, y_pos * 1.02, f'{sig}\n{p_str}', 
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            ax.text(1.5, y_pos * 1.02, f'ns\n{p_str}', 
                   ha='center', va='bottom', fontsize=9, color='gray')
        
        # Título e labels
        ax.set_title(f'{metric}', fontsize=13, fontweight='bold')
        ax.set_ylabel('Value', fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona info de Cohen's d
        if result.effect_size:
            ax.text(0.5, 0.02, f"Cohen's d = {result.effect_size:.3f}\n({result.effect_size_interpretation})",
                   transform=ax.transAxes, fontsize=9, va='bottom', ha='left',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Distribution Comparison: Baseline vs. SecureBank™', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Boxplots comparativos salvos: {output_path}")


def plot_violin_comparison(
    baseline_data: Dict[str, List[float]],
    securebank_data: Dict[str, List[float]],
    statistical_results: Dict[str, StatisticalTestResult],
    output_path: Path,
    figsize: Tuple[int, int] = (14, 5),
    dpi: int = 300
):
    """
    Gera violin plots comparativos mostrando distribuições completas.
    
    Args:
        baseline_data: Dict com dados baseline
        securebank_data: Dict com dados SecureBank™
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_path: Caminho para salvar a figura
        figsize: Tamanho da figura
        dpi: Resolução da figura
    """
    metrics = list(baseline_data.keys())
    n_metrics = len(metrics)
    
    fig, axes = plt.subplots(1, n_metrics, figsize=figsize, dpi=dpi)
    
    if n_metrics == 1:
        axes = [axes]
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        result = statistical_results[metric]
        
        # Prepara dados para violin plot
        positions = [1, 2]
        data_to_plot = [baseline_data[metric], securebank_data[metric]]
        
        # Cria violin plot
        parts = ax.violinplot(
            data_to_plot,
            positions=positions,
            showmeans=True,
            showmedians=True,
            widths=0.7
        )
        
        # Colorir violins
        colors = [COLOR_BASELINE, COLOR_SECUREBANK]
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.7)
        
        # Adiciona boxplot interno (quartis)
        bp = ax.boxplot(
            data_to_plot,
            positions=positions,
            widths=0.15,
            showfliers=False,
            showcaps=False,
            patch_artist=True,
            boxprops=dict(facecolor='white', edgecolor='black', linewidth=1.5),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(color='black', linewidth=1.5)
        )
        
        # Anotação de significância
        sig = significance_stars(result.p_value)
        p_str = format_p_value(result.p_value)
        
        y_max = max(max(baseline_data[metric]), max(securebank_data[metric]))
        y_min = min(min(baseline_data[metric]), min(securebank_data[metric]))
        y_range = y_max - y_min
        y_pos = y_max + y_range * 0.15
        
        # Linha horizontal de comparação
        ax.plot([1, 2], [y_pos, y_pos], 'k-', linewidth=1.5)
        
        # Texto de significância
        if sig != "ns":
            ax.text(1.5, y_pos * 1.02, f'{sig}\n{p_str}', 
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            ax.text(1.5, y_pos * 1.02, f'ns\n{p_str}', 
                   ha='center', va='bottom', fontsize=9, color='gray')
        
        # Configurações do eixo
        ax.set_title(f'{metric}', fontsize=13, fontweight='bold')
        ax.set_ylabel('Value', fontsize=11)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Baseline', 'SecureBank™'], fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona estatísticas no canto
        stats_text = (
            f"Baseline: {result.baseline_mean:.3f}±{result.baseline_std:.3f}\n"
            f"SecureBank™: {result.securebank_mean:.3f}±{result.securebank_std:.3f}"
        )
        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes, fontsize=8, va='top', ha='left',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
    
    plt.suptitle('Distribution Analysis: Baseline vs. SecureBank™', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Violin plots salvos: {output_path}")


def plot_effect_sizes(
    statistical_results: Dict[str, StatisticalTestResult],
    output_path: Path,
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 300
):
    """
    Gera gráfico de tamanhos de efeito (Cohen's d) com interpretação.
    
    Args:
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_path: Caminho para salvar a figura
        figsize: Tamanho da figura
        dpi: Resolução da figura
    """
    metrics = list(statistical_results.keys())
    effect_sizes = [statistical_results[m].effect_size for m in metrics]
    interpretations = [statistical_results[m].effect_size_interpretation for m in metrics]
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Define cores baseadas na interpretação
    colors = []
    for interp in interpretations:
        if interp in ["negligible"]:
            colors.append("#95a5a6")  # Cinza
        elif interp == "small":
            colors.append("#f39c12")  # Laranja
        elif interp == "medium":
            colors.append("#3498db")  # Azul
        elif interp == "large":
            colors.append("#2ecc71")  # Verde
        else:  # very large, huge
            colors.append("#e74c3c")  # Vermelho
    
    # Gráfico de barras horizontal
    y_pos = np.arange(len(metrics))
    bars = ax.barh(y_pos, [abs(e) for e in effect_sizes], color=colors, alpha=0.8)
    
    # Adiciona valores e interpretação
    for i, (es, interp) in enumerate(zip(effect_sizes, interpretations)):
        ax.text(abs(es) + 0.05, i, f'{abs(es):.3f}\n({interp})', 
               va='center', ha='left', fontsize=10, fontweight='bold')
    
    # Linhas de referência para interpretação
    ax.axvline(x=0.2, color='gray', linestyle='--', alpha=0.5, label='Small (0.2)')
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5, label='Medium (0.5)')
    ax.axvline(x=0.8, color='gray', linestyle='--', alpha=0.5, label='Large (0.8)')
    
    # Configurações do eixo
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=12)
    ax.set_xlabel("Effect Size (|Cohen's d|)", fontsize=13, fontweight='bold')
    ax.set_title("Effect Size Analysis: SecureBank™ vs. Baseline", 
                fontsize=15, fontweight='bold', pad=20)
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico de tamanhos de efeito salvo: {output_path}")


def plot_confidence_intervals(
    statistical_results: Dict[str, StatisticalTestResult],
    output_path: Path,
    figsize: Tuple[int, int] = (10, 6),
    dpi: int = 300
):
    """
    Gera gráfico de intervalos de confiança 95% para as diferenças.
    
    Args:
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_path: Caminho para salvar a figura
        figsize: Tamanho da figura
        dpi: Resolução da figura
    """
    metrics = list(statistical_results.keys())
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    y_pos = np.arange(len(metrics))
    
    for i, metric in enumerate(metrics):
        result = statistical_results[metric]
        ci_lower, ci_upper = result.confidence_interval
        mean_diff = (ci_lower + ci_upper) / 2
        
        # Determina cor baseado na significância
        color = COLOR_SECUREBANK if result.is_significant else COLOR_CI
        
        # Plota intervalo de confiança
        ax.errorbar(
            mean_diff, i, 
            xerr=[[mean_diff - ci_lower], [ci_upper - mean_diff]],
            fmt='o', 
            markersize=8, 
            color=color, 
            ecolor=color,
            capsize=5,
            capthick=2,
            linewidth=2,
            alpha=0.8
        )
        
        # Adiciona texto com valores
        sig = significance_stars(result.p_value)
        ax.text(ci_upper + 0.01, i, f'{sig}', 
               va='center', ha='left', fontsize=12, fontweight='bold')
    
    # Linha vertical em zero (sem diferença)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='No difference')
    
    # Configurações do eixo
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metrics, fontsize=12)
    ax.set_xlabel('Mean Difference (SecureBank™ - Baseline)\n95% Confidence Interval', 
                 fontsize=13, fontweight='bold')
    ax.set_title('Confidence Intervals for Mean Differences', 
                fontsize=15, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico de intervalos de confiança salvo: {output_path}")


def generate_all_enhanced_plots(
    baseline_data: Dict[str, List[float]],
    securebank_data: Dict[str, List[float]],
    statistical_results: Dict[str, StatisticalTestResult],
    output_dir: Path
):
    """
    Gera todos os gráficos estatísticos aprimorados.
    
    Args:
        baseline_data: Dict com dados baseline
        securebank_data: Dict com dados SecureBank™
        statistical_results: Dict com StatisticalTestResult para cada métrica
        output_dir: Diretório para salvar as figuras
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "="*60)
    print("Gerando gráficos estatísticos aprimorados...")
    print("="*60)
    
    # 1. Gráfico de barras com significância
    plot_comparison_bars_with_significance(
        baseline_data, securebank_data, statistical_results,
        output_dir / "statistical_bars_comparison.png"
    )
    
    # 2. Boxplots comparativos
    plot_boxplots_comparison(
        baseline_data, securebank_data, statistical_results,
        output_dir / "statistical_boxplots.png"
    )
    
    # 3. Violin plots
    plot_violin_comparison(
        baseline_data, securebank_data, statistical_results,
        output_dir / "statistical_violin_plots.png"
    )
    
    # 4. Tamanhos de efeito
    plot_effect_sizes(
        statistical_results,
        output_dir / "effect_sizes.png"
    )
    
    # 5. Intervalos de confiança
    plot_confidence_intervals(
        statistical_results,
        output_dir / "confidence_intervals.png"
    )
    
    print("="*60)
    print("✓ Todos os gráficos estatísticos foram gerados com sucesso!")
    print("="*60)


if __name__ == "__main__":
    print("Enhanced Plots Module for SecureBank™")
    print("Módulo de visualização avançada com significância estatística")
