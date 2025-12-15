"""
empirical_validation.py

Módulo de validação empírica para SecureBank™.

Executa os PDPs (baseline e SecureBank) sobre dados reais de fraude bancária
e compara os resultados com os obtidos na simulação, calculando correlações
e validando a generalização dos modelos.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from scipy import stats

from real_data_adapter import RealDataAdapter, load_and_adapt_real_data
from simulator import baseline_pdp, securebank_pdp
from metrics import compute_tii, compute_sae, compute_ital, compute_scenario_detection


class EmpiricalValidator:
    """
    Classe para executar validação empírica dos PDPs sobre dados reais.
    
    Compara resultados da simulação com resultados sobre dados reais,
    calculando correlações e métricas de generalização.
    """
    
    def __init__(self, real_dataset_path: str, config: Dict = None):
        """
        Inicializa o validador empírico.
        
        Args:
            real_dataset_path: Caminho para o dataset real
            config: Configuração da simulação (ITAL params, etc.)
        """
        self.real_dataset_path = real_dataset_path
        self.config = config or {}
        
        # Resultados
        self.real_events = None
        self.real_stats = None
        self.baseline_logs = None
        self.securebank_logs = None
        
        # Métricas
        self.real_metrics = {}
        self.simulation_metrics = {}
        self.correlation = {}
        
    def load_real_data(self) -> Tuple[List[Dict], Dict]:
        """
        Carrega e adapta dados reais para o formato da simulação.
        
        Returns:
            Tupla (eventos, estatísticas)
        """
        print("\n" + "="*70)
        print("Loading Real Data")
        print("="*70)
        
        self.real_events, self.real_stats = load_and_adapt_real_data(
            self.real_dataset_path
        )
        
        print(f"\n✓ Loaded {len(self.real_events)} real transactions")
        print(f"  - Fraud rate: {self.real_stats['fraud_rate']*100:.2f}%")
        print(f"  - Users: {self.real_stats['total_users']}")
        print(f"  - Devices: {self.real_stats['total_devices']}")
        
        return self.real_events, self.real_stats
    
    def run_pdps_on_real_data(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Executa os PDPs (baseline e SecureBank) sobre dados reais.
        
        Returns:
            Tupla (baseline_logs, securebank_logs)
        """
        if self.real_events is None:
            raise ValueError("Real data not loaded. Call load_real_data() first.")
        
        print("\n" + "="*70)
        print("Running PDPs on Real Data")
        print("="*70)
        
        # Parâmetros ITAL do config
        ital_params = self.config.get("ital_params", {})
        
        baseline_logs = []
        securebank_logs = []
        
        # Estado interno do SecureBank (confiança)
        sb_state = {"I": {}, "D": {}, "profiles": {}}
        
        total = len(self.real_events)
        
        for i, event in enumerate(self.real_events):
            # Progress indicator
            if (i + 1) % 1000 == 0 or i == total - 1:
                print(f"  Processing: {i+1}/{total} transactions ({(i+1)/total*100:.1f}%)", end='\r')
            
            # Baseline PDP
            base_decision = baseline_pdp(event)
            baseline_logs.append({**event, **base_decision})
            
            # SecureBank PDP
            sb_decision = securebank_pdp(event, sb_state, ital_params)
            securebank_logs.append({**event, **sb_decision})
        
        print()  # Nova linha após o progress
        
        self.baseline_logs = baseline_logs
        self.securebank_logs = securebank_logs
        
        print(f"\n✓ Processed {len(baseline_logs)} transactions through both PDPs")
        
        return baseline_logs, securebank_logs
    
    def compute_real_metrics(self) -> Dict[str, float]:
        """
        Calcula métricas TII, SAE e ITAL sobre os dados reais.
        
        Returns:
            Dict com métricas para baseline e SecureBank
        """
        if self.baseline_logs is None or self.securebank_logs is None:
            raise ValueError("PDPs not executed. Call run_pdps_on_real_data() first.")
        
        print("\n" + "="*70)
        print("Computing Metrics on Real Data")
        print("="*70)
        
        ital_params = self.config.get("ital_params", {})
        
        # Métricas baseline
        tii_baseline = compute_tii(self.baseline_logs)
        sae_baseline = compute_sae(self.baseline_logs)
        ital_baseline = compute_ital(self.baseline_logs, ital_params)
        
        # Métricas SecureBank
        tii_sb = compute_tii(self.securebank_logs)
        sae_sb = compute_sae(self.securebank_logs)
        ital_sb = compute_ital(self.securebank_logs, ital_params)
        
        self.real_metrics = {
            "TII": {
                "baseline": tii_baseline,
                "securebank": tii_sb,
                "improvement": ((tii_sb - tii_baseline) / tii_baseline * 100) if tii_baseline > 0 else 0,
            },
            "SAE": {
                "baseline": sae_baseline,
                "securebank": sae_sb,
                "improvement": ((sae_sb - sae_baseline) / sae_baseline * 100) if sae_baseline > 0 else 0,
            },
            "ITAL": {
                "baseline": ital_baseline,
                "securebank": ital_sb,
                "improvement": ((ital_sb - ital_baseline) / ital_baseline * 100) if ital_baseline > 0 else 0,
            }
        }
        
        print(f"\nReal Data Metrics:")
        print(f"  TII:  Baseline={tii_baseline:.4f}, SecureBank={tii_sb:.4f} ({self.real_metrics['TII']['improvement']:+.1f}%)")
        print(f"  SAE:  Baseline={sae_baseline:.4f}, SecureBank={sae_sb:.4f} ({self.real_metrics['SAE']['improvement']:+.1f}%)")
        print(f"  ITAL: Baseline={ital_baseline:.4f}, SecureBank={ital_sb:.4f} ({self.real_metrics['ITAL']['improvement']:+.1f}%)")
        
        return self.real_metrics
    
    def load_simulation_metrics(self, simulation_results_path: str) -> Dict[str, float]:
        """
        Carrega métricas da simulação para comparação.
        
        Args:
            simulation_results_path: Caminho para o summary_results.json da simulação
            
        Returns:
            Dict com métricas da simulação
        """
        print("\n" + "="*70)
        print("Loading Simulation Metrics")
        print("="*70)
        
        with open(simulation_results_path, 'r') as f:
            sim_results = json.load(f)
        
        self.simulation_metrics = {
            "TII": {
                "baseline": sim_results["TII"]["baseline_mean"],
                "baseline_std": sim_results["TII"]["baseline_std"],
                "securebank": sim_results["TII"]["securebank_mean"],
                "securebank_std": sim_results["TII"]["securebank_std"],
            },
            "SAE": {
                "baseline": sim_results["SAE"]["baseline_mean"],
                "baseline_std": sim_results["SAE"]["baseline_std"],
                "securebank": sim_results["SAE"]["securebank_mean"],
                "securebank_std": sim_results["SAE"]["securebank_std"],
            },
            "ITAL": {
                "baseline": sim_results["ITAL"]["baseline_mean"],
                "baseline_std": sim_results["ITAL"]["baseline_std"],
                "securebank": sim_results["ITAL"]["securebank_mean"],
                "securebank_std": sim_results["ITAL"]["securebank_std"],
            }
        }
        
        print(f"\nSimulation Metrics (mean ± std):")
        print(f"  TII:  Baseline={self.simulation_metrics['TII']['baseline']:.4f}±{self.simulation_metrics['TII']['baseline_std']:.4f}, "
              f"SecureBank={self.simulation_metrics['TII']['securebank']:.4f}±{self.simulation_metrics['TII']['securebank_std']:.4f}")
        print(f"  SAE:  Baseline={self.simulation_metrics['SAE']['baseline']:.4f}±{self.simulation_metrics['SAE']['baseline_std']:.4f}, "
              f"SecureBank={self.simulation_metrics['SAE']['securebank']:.4f}±{self.simulation_metrics['SAE']['securebank_std']:.4f}")
        print(f"  ITAL: Baseline={self.simulation_metrics['ITAL']['baseline']:.4f}±{self.simulation_metrics['ITAL']['baseline_std']:.4f}, "
              f"SecureBank={self.simulation_metrics['ITAL']['securebank']:.4f}±{self.simulation_metrics['ITAL']['securebank_std']:.4f}")
        
        return self.simulation_metrics
    
    def compute_correlation(self) -> Dict[str, Any]:
        """
        Calcula correlação entre métricas da simulação e dados reais.
        
        Returns:
            Dict com correlações e estatísticas de validação
        """
        if not self.real_metrics or not self.simulation_metrics:
            raise ValueError("Metrics not computed. Call compute_real_metrics() and load_simulation_metrics() first.")
        
        print("\n" + "="*70)
        print("Computing Correlation: Simulation vs. Real Data")
        print("="*70)
        
        correlations = {}
        
        for metric in ["TII", "SAE", "ITAL"]:
            # Valores da simulação (baseline e securebank)
            sim_vals = [
                self.simulation_metrics[metric]["baseline"],
                self.simulation_metrics[metric]["securebank"]
            ]
            
            # Valores dos dados reais (baseline e securebank)
            real_vals = [
                self.real_metrics[metric]["baseline"],
                self.real_metrics[metric]["securebank"]
            ]
            
            # Correlação de Pearson
            r, p_value = stats.pearsonr(sim_vals, real_vals)
            
            # Diferença absoluta (erro médio)
            abs_diff_baseline = abs(sim_vals[0] - real_vals[0])
            abs_diff_sb = abs(sim_vals[1] - real_vals[1])
            mean_abs_error = (abs_diff_baseline + abs_diff_sb) / 2
            
            # Diferença relativa (%)
            rel_diff_baseline = abs_diff_baseline / sim_vals[0] * 100 if sim_vals[0] > 0 else 0
            rel_diff_sb = abs_diff_sb / sim_vals[1] * 100 if sim_vals[1] > 0 else 0
            mean_rel_error = (rel_diff_baseline + rel_diff_sb) / 2
            
            correlations[metric] = {
                "pearson_r": r,
                "p_value": p_value,
                "is_significant": p_value < 0.05,
                "mean_absolute_error": mean_abs_error,
                "mean_relative_error_pct": mean_rel_error,
                "simulation_values": sim_vals,
                "real_values": real_vals,
                "baseline_diff": abs_diff_baseline,
                "securebank_diff": abs_diff_sb,
            }
            
            print(f"\n{metric}:")
            print(f"  Pearson r: {r:.4f} (p={p_value:.4f}) {'✓ Significant' if p_value < 0.05 else '✗ Not significant'}")
            print(f"  Mean Absolute Error: {mean_abs_error:.4f}")
            print(f"  Mean Relative Error: {mean_rel_error:.2f}%")
            print(f"  Simulation: Baseline={sim_vals[0]:.4f}, SecureBank={sim_vals[1]:.4f}")
            print(f"  Real:       Baseline={real_vals[0]:.4f}, SecureBank={real_vals[1]:.4f}")
        
        # Correlação geral (média ponderada)
        overall_r = np.mean([correlations[m]["pearson_r"] for m in ["TII", "SAE", "ITAL"]])
        overall_mae = np.mean([correlations[m]["mean_absolute_error"] for m in ["TII", "SAE", "ITAL"]])
        overall_mre = np.mean([correlations[m]["mean_relative_error_pct"] for m in ["TII", "SAE", "ITAL"]])
        
        correlations["overall"] = {
            "mean_pearson_r": overall_r,
            "mean_absolute_error": overall_mae,
            "mean_relative_error_pct": overall_mre,
            "interpretation": self._interpret_correlation(overall_r),
        }
        
        print(f"\n{'='*70}")
        print(f"Overall Correlation:")
        print(f"  Mean Pearson r: {overall_r:.4f} - {correlations['overall']['interpretation']}")
        print(f"  Mean Absolute Error: {overall_mae:.4f}")
        print(f"  Mean Relative Error: {overall_mre:.2f}%")
        print(f"{'='*70}")
        
        self.correlation = correlations
        
        return correlations
    
    def _interpret_correlation(self, r: float) -> str:
        """
        Interpreta valor de correlação de Pearson.
        
        Args:
            r: Coeficiente de correlação de Pearson
            
        Returns:
            String com interpretação
        """
        abs_r = abs(r)
        if abs_r >= 0.90:
            return "Excellent correlation (r ≥ 0.90)"
        elif abs_r >= 0.80:
            return "Very strong correlation (0.80 ≤ r < 0.90)"
        elif abs_r >= 0.70:
            return "Strong correlation (0.70 ≤ r < 0.80)"
        elif abs_r >= 0.50:
            return "Moderate correlation (0.50 ≤ r < 0.70)"
        else:
            return "Weak correlation (r < 0.50)"
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """
        Converte objetos numpy para tipos Python nativos para serialização JSON.
        
        Args:
            obj: Objeto a ser convertido
            
        Returns:
            Objeto com tipos Python nativos
        """
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        else:
            return obj
    
    def analyze_distribution_similarity(self) -> Dict[str, Any]:
        """
        Analisa similaridade entre distribuições de transações reais e simuladas.
        
        Returns:
            Dict com estatísticas de distribuição
        """
        print("\n" + "="*70)
        print("Analyzing Distribution Similarity")
        print("="*70)
        
        # Extrai valores de transações reais
        real_amounts = [log['tx']['amount'] for log in self.baseline_logs]
        real_services = [log['tx']['service'] for log in self.baseline_logs]
        real_channels = [log['ctx']['channel'] for log in self.baseline_logs]
        real_geos = [log['ctx']['geo'] for log in self.baseline_logs]
        real_is_attack = [log['is_attack'] for log in self.baseline_logs]
        
        # Estatísticas de distribuição
        distribution_stats = {
            "amount": {
                "real_mean": np.mean(real_amounts),
                "real_median": np.median(real_amounts),
                "real_std": np.std(real_amounts),
                "real_min": np.min(real_amounts),
                "real_max": np.max(real_amounts),
            },
            "attack_rate": {
                "real": np.mean(real_is_attack),
            },
            "service_distribution": {
                service: real_services.count(service) / len(real_services)
                for service in set(real_services)
            },
            "channel_distribution": {
                channel: real_channels.count(channel) / len(real_channels)
                for channel in set(real_channels)
            },
            "geo_distribution_top10": {},
        }
        
        # Top 10 localizações
        geo_counts = defaultdict(int)
        for geo in real_geos:
            geo_counts[geo] += 1
        top_geos = sorted(geo_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for geo, count in top_geos:
            distribution_stats["geo_distribution_top10"][geo] = count / len(real_geos)
        
        print(f"\nReal Data Distribution:")
        print(f"  Amount: mean=${distribution_stats['amount']['real_mean']:.2f}, "
              f"median=${distribution_stats['amount']['real_median']:.2f}, "
              f"std=${distribution_stats['amount']['real_std']:.2f}")
        print(f"  Attack rate: {distribution_stats['attack_rate']['real']*100:.2f}%")
        print(f"  Services: {len(distribution_stats['service_distribution'])} types")
        print(f"  Channels: {len(distribution_stats['channel_distribution'])} types")
        print(f"  Geolocations: {len(geo_counts)} unique locations")
        
        return distribution_stats
    
    def save_results(self, output_dir: str) -> None:
        """
        Salva todos os resultados da validação empírica.
        
        Args:
            output_dir: Diretório de saída
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*70)
        print("Saving Empirical Validation Results")
        print("="*70)
        
        # 1. Métricas reais
        metrics_path = output_path / "empirical_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump({
                "real_metrics": self.real_metrics,
                "simulation_metrics": self.simulation_metrics,
            }, f, indent=2)
        print(f"✓ Saved metrics: {metrics_path}")
        
        # 2. Correlação (converte numpy types para Python types)
        correlation_serializable = self._make_json_serializable(self.correlation)
        correlation_path = output_path / "empirical_correlation.json"
        with open(correlation_path, 'w') as f:
            json.dump(correlation_serializable, f, indent=2)
        print(f"✓ Saved correlation: {correlation_path}")
        
        # 3. Estatísticas do dataset real
        stats_path = output_path / "empirical_dataset_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(self.real_stats, f, indent=2)
        print(f"✓ Saved dataset stats: {stats_path}")
        
        # 4. Logs completos (baseline e securebank) - apenas uma amostra
        sample_size = min(1000, len(self.baseline_logs))
        baseline_sample = self._make_json_serializable(self.baseline_logs[:sample_size])
        securebank_sample = self._make_json_serializable(self.securebank_logs[:sample_size])
        
        baseline_path = output_path / "empirical_baseline_logs_sample.json"
        with open(baseline_path, 'w') as f:
            json.dump(baseline_sample, f, indent=2)
        print(f"✓ Saved baseline logs sample: {baseline_path}")
        
        securebank_path = output_path / "empirical_securebank_logs_sample.json"
        with open(securebank_path, 'w') as f:
            json.dump(securebank_sample, f, indent=2)
        print(f"✓ Saved securebank logs sample: {securebank_path}")
        
        # 5. Detecção por cenário
        scenario_detection = compute_scenario_detection(self.baseline_logs, self.securebank_logs)
        scenario_path = output_path / "empirical_scenario_detection.json"
        with open(scenario_path, 'w') as f:
            json.dump(scenario_detection, f, indent=2)
        print(f"✓ Saved scenario detection: {scenario_path}")
        
        print(f"\n{'='*70}")
        print(f"All results saved to: {output_dir}")
        print(f"{'='*70}")
    
    def run_full_validation(self, simulation_results_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Executa validação empírica completa.
        
        Args:
            simulation_results_path: Caminho para resultados da simulação
            output_dir: Diretório de saída
            
        Returns:
            Dict com todos os resultados
        """
        print("\n" + "="*70)
        print("EMPIRICAL VALIDATION - FULL PIPELINE")
        print("="*70)
        
        # 1. Carrega dados reais
        self.load_real_data()
        
        # 2. Executa PDPs sobre dados reais
        self.run_pdps_on_real_data()
        
        # 3. Calcula métricas sobre dados reais
        self.compute_real_metrics()
        
        # 4. Carrega métricas da simulação
        self.load_simulation_metrics(simulation_results_path)
        
        # 5. Calcula correlação
        self.compute_correlation()
        
        # 6. Analisa distribuições
        distribution_stats = self.analyze_distribution_similarity()
        
        # 7. Salva resultados
        self.save_results(output_dir)
        
        # Resultado final
        results = {
            "real_metrics": self.real_metrics,
            "simulation_metrics": self.simulation_metrics,
            "correlation": self.correlation,
            "distribution_stats": distribution_stats,
            "summary": {
                "overall_correlation": self.correlation["overall"]["mean_pearson_r"],
                "correlation_interpretation": self.correlation["overall"]["interpretation"],
                "mean_relative_error_pct": self.correlation["overall"]["mean_relative_error_pct"],
                "validation_success": self.correlation["overall"]["mean_pearson_r"] >= 0.70,
            }
        }
        
        # Imprime resumo final
        print("\n" + "="*70)
        print("EMPIRICAL VALIDATION SUMMARY")
        print("="*70)
        print(f"\n✓ Overall Correlation: r = {results['summary']['overall_correlation']:.4f}")
        print(f"  {results['summary']['correlation_interpretation']}")
        print(f"\n✓ Mean Relative Error: {results['summary']['mean_relative_error_pct']:.2f}%")
        print(f"\n✓ Validation {'PASSED' if results['summary']['validation_success'] else 'FAILED'}")
        print(f"  Criterion: r ≥ 0.70 {'✓' if results['summary']['validation_success'] else '✗'}")
        print("="*70)
        
        return results


# CLI para executar validação empírica
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python empirical_validation.py <real_dataset_path> <simulation_results_path> [output_dir]")
        sys.exit(1)
    
    real_dataset = sys.argv[1]
    sim_results = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "./empirical_validation_results"
    
    # Carrega config
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Executa validação
    validator = EmpiricalValidator(real_dataset, config)
    results = validator.run_full_validation(sim_results, output_dir)
