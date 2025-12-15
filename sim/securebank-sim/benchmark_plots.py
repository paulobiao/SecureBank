# benchmark_plots.py
"""
Visualizações para benchmark de frameworks Zero Trust.

Gera:
- Gráfico radar (spider chart) com 6 dimensões qualitativas
- Tabela comparativa estilo acadêmico
- Gráficos de barras agrupadas para métricas
- Matriz de cobertura MITRE ATT&CK (heatmap)
- Gráfico de trade-offs (TII vs SAE)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import pandas as pd
from typing import Dict, List

# Configuração visual
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


class BenchmarkPlotter:
    """
    Gera visualizações comparativas para benchmark de frameworks.
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Cores consistentes para frameworks
        self.colors = {
            "baseline": "#e74c3c",      # vermelho
            "nist_zta": "#3498db",      # azul
            "securebank": "#2ecc71",    # verde
        }
        
        self.framework_labels = {
            "baseline": "Baseline",
            "nist_zta": "NIST ZTA",
            "securebank": "SecureBank™",
        }
    
    def plot_radar_chart(self, qualitative_scores: Dict, filename="radar_comparison.png"):
        """
        Gráfico radar (spider chart) com 6 dimensões qualitativas.
        """
        dimensions = [
            "Financial Context\nAwareness",
            "Adaptive Identity\nScoring",
            "Contextual\nMicro-Segmentation",
            "Impact-Driven\nAutomation",
            "Transactional Risk\nIntegration",
            "Real-time Trust\nAdaptation",
        ]
        
        frameworks = ["baseline", "nist_zta", "securebank"]
        
        # Prepara dados
        original_dims = [
            "Financial Context Awareness",
            "Adaptive Identity Scoring",
            "Contextual Micro-Segmentation",
            "Impact-Driven Automation",
            "Transactional Risk Integration",
            "Real-time Trust Adaptation",
        ]
        
        values = {
            f: [qualitative_scores[f][d] for d in original_dims]
            for f in frameworks
        }
        
        # Setup radar chart
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        angles += angles[:1]  # fecha o círculo
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plota cada framework
        for framework in frameworks:
            vals = values[framework] + values[framework][:1]  # fecha o círculo
            ax.plot(angles, vals, 'o-', linewidth=2.5, 
                   label=self.framework_labels[framework],
                   color=self.colors[framework])
            ax.fill(angles, vals, alpha=0.15, color=self.colors[framework])
        
        # Customização
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, size=9)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], size=8)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
        plt.title("Framework Comparison: Qualitative Dimensions", 
                 size=14, weight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, bbox_inches='tight')
        plt.close()
        
        print(f"Saved radar chart: {filename}")
    
    def plot_metrics_comparison(self, quantitative_metrics: Dict, 
                               filename="metrics_comparison.png"):
        """
        Gráficos de barras agrupadas para métricas quantitativas.
        """
        frameworks = ["baseline", "nist_zta", "securebank"]
        metrics = ["TII", "SAE", "ITAL"]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            values = [quantitative_metrics[f][metric] for f in frameworks]
            colors = [self.colors[f] for f in frameworks]
            labels = [self.framework_labels[f] for f in frameworks]
            
            bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Adiciona valores no topo das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=10, weight='bold')
            
            ax.set_ylabel(metric, fontsize=12, weight='bold')
            ax.set_ylim(0, 1.1)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_title(f"{metric} Comparison", fontsize=12, weight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, bbox_inches='tight')
        plt.close()
        
        print(f"Saved metrics comparison: {filename}")
    
    def plot_mitre_coverage_heatmap(self, mitre_coverage: Dict, 
                                   filename="mitre_coverage_heatmap.png"):
        """
        Matriz de cobertura MITRE ATT&CK (heatmap).
        """
        matrix = mitre_coverage["matrix"]
        
        # Prepara dados para heatmap
        techniques = sorted(matrix.keys())
        frameworks = ["baseline", "nist_zta", "securebank"]
        
        data = []
        labels = []
        
        for tech_id in techniques:
            tech_data = matrix[tech_id]
            tech_name = tech_data["technique_name"]
            labels.append(f"{tech_id}\n{tech_name}")
            
            row = [tech_data[f] for f in frameworks]
            data.append(row)
        
        data = np.array(data)
        
        # Cria heatmap
        fig, ax = plt.subplots(figsize=(10, 12))
        
        im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        
        # Configura eixos
        ax.set_xticks(np.arange(len(frameworks)))
        ax.set_yticks(np.arange(len(techniques)))
        ax.set_xticklabels([self.framework_labels[f] for f in frameworks], fontsize=11)
        ax.set_yticklabels(labels, fontsize=8)
        
        # Adiciona valores nas células
        for i in range(len(techniques)):
            for j in range(len(frameworks)):
                text = ax.text(j, i, f'{data[i, j]:.0f}%',
                             ha="center", va="center", color="black", 
                             fontsize=9, weight='bold')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Detection Rate (%)', rotation=270, labelpad=20, fontsize=11)
        
        ax.set_title("MITRE ATT&CK Coverage Matrix", fontsize=14, weight='bold', pad=15)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, bbox_inches='tight')
        plt.close()
        
        print(f"Saved MITRE coverage heatmap: {filename}")
    
    def plot_tradeoffs(self, tradeoffs: Dict, filename="tradeoffs_analysis.png"):
        """
        Gráfico de trade-offs (TII vs SAE, effectiveness vs overhead).
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # TII vs SAE
        ax1 = axes[0]
        for point in tradeoffs["tii_vs_sae"]:
            framework = point["framework"]
            ax1.scatter(point["tii"], point["sae"], 
                       s=300, color=self.colors[framework], 
                       alpha=0.7, edgecolors='black', linewidth=2,
                       label=self.framework_labels[framework])
            ax1.annotate(self.framework_labels[framework], 
                        (point["tii"], point["sae"]),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=10, weight='bold')
        
        ax1.set_xlabel('TII (Transactional Integrity Index)', fontsize=11, weight='bold')
        ax1.set_ylabel('SAE (Security Automation Efficiency)', fontsize=11, weight='bold')
        ax1.set_title('Usability vs Security Trade-off', fontsize=12, weight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xlim(0, 1.05)
        ax1.set_ylim(0, 1.05)
        
        # Effectiveness vs Overhead
        ax2 = axes[1]
        for point in tradeoffs["effectiveness_vs_overhead"]:
            framework = point["framework"]
            ax2.scatter(point["overhead"], point["effectiveness"],
                       s=300, color=self.colors[framework],
                       alpha=0.7, edgecolors='black', linewidth=2,
                       label=self.framework_labels[framework])
            ax2.annotate(self.framework_labels[framework],
                        (point["overhead"], point["effectiveness"]),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=10, weight='bold')
        
        ax2.set_xlabel('Operational Overhead (%)', fontsize=11, weight='bold')
        ax2.set_ylabel('Overall Effectiveness', fontsize=11, weight='bold')
        ax2.set_title('Cost vs Effectiveness Trade-off', fontsize=12, weight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_ylim(0, 1.05)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, bbox_inches='tight')
        plt.close()
        
        print(f"Saved trade-offs analysis: {filename}")
    
    def generate_comparison_table_latex(self, comparison_table: Dict, 
                                       filename="comparison_table.tex"):
        """
        Gera tabela comparativa em formato LaTeX.
        """
        frameworks = comparison_table["frameworks"]
        
        latex = []
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Framework Comparison: Quantitative and Qualitative Analysis}")
        latex.append("\\label{tab:framework_comparison}")
        latex.append("\\begin{tabular}{l|" + "c" * len(frameworks) + "}")
        latex.append("\\hline")
        latex.append("\\textbf{Dimension/Metric} & " + " & ".join([f"\\textbf{{{f}}}" for f in frameworks]) + " \\\\")
        latex.append("\\hline")
        latex.append("\\multicolumn{" + str(len(frameworks) + 1) + "}{c}{\\textit{Qualitative Dimensions (0-100)}} \\\\")
        latex.append("\\hline")
        
        # Dimensões qualitativas
        for dim, values in comparison_table["qualitative"].items():
            row = dim + " & " + " & ".join([str(v) for v in values]) + " \\\\"
            latex.append(row)
        
        latex.append("\\hline")
        latex.append("\\multicolumn{" + str(len(frameworks) + 1) + "}{c}{\\textit{Quantitative Metrics}} \\\\")
        latex.append("\\hline")
        
        # Métricas quantitativas
        metric_labels = {
            "TII": "TII",
            "SAE": "SAE",
            "ITAL": "ITAL",
            "latency_ms": "Latency (ms)",
            "overhead_pct": "Overhead (\\%)",
        }
        
        for metric, label in metric_labels.items():
            values = comparison_table["quantitative"][metric]
            row = label + " & " + " & ".join([f"{v:.3f}" if v < 10 else f"{v:.1f}" for v in values]) + " \\\\"
            latex.append(row)
        
        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")
        
        # Salva arquivo
        with open(self.output_dir / filename, 'w') as f:
            f.write("\n".join(latex))
        
        print(f"Saved LaTeX table: {filename}")
    
    def generate_all_plots(self, comparison_data: Dict, mitre_coverage: Dict):
        """
        Gera todas as visualizações de uma vez.
        
        Args:
            comparison_data: resultado de compare_frameworks()
            mitre_coverage: resultado de analyze_mitre_coverage()
        """
        print("\nGenerating benchmark visualizations...")
        
        # 1. Radar chart
        self.plot_radar_chart(comparison_data["qualitative_scores"])
        
        # 2. Metrics comparison
        self.plot_metrics_comparison(comparison_data["quantitative_metrics"])
        
        # 3. MITRE coverage heatmap
        self.plot_mitre_coverage_heatmap(mitre_coverage)
        
        # 4. Trade-offs
        self.plot_tradeoffs(comparison_data["tradeoffs"])
        
        # 5. LaTeX table
        self.generate_comparison_table_latex(comparison_data["comparison_table"])
        
        print(f"\nAll visualizations saved to: {self.output_dir}")
