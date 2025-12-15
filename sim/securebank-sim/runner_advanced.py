#!/usr/bin/env python3
"""
runner_advanced.py

Runner para executar análises avançadas do SecureBank™:
- Cost-Benefit / ROI Analysis
- False Positive/Negative Analysis
- Scalability Analysis
- Sensitivity Analysis

Usage:
    python runner_advanced.py [--mode MODE] [--output-dir DIR]
    
Modes:
    all         : Run all analyses (default)
    roi         : Run only ROI analysis
    fp_fn       : Run only FP/FN analysis
    scalability : Run only scalability analysis
    sensitivity : Run only sensitivity analysis
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

from simulator import run_simulation
from advanced_metrics import (
    compute_roi_analysis,
    compute_false_positive_negative_analysis,
    compute_scalability_analysis,
    compute_sensitivity_analysis,
    run_all_advanced_analyses
)
from advanced_plots import generate_all_advanced_plots


def save_results_json(results: dict, output_path: Path):
    """Salva resultados em JSON."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Results saved to {output_path}")


def generate_summary_report(results: dict, output_path: Path):
    """Gera relatório resumido em texto."""
    with open(output_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SECUREBANK™ ADVANCED ANALYSES - SUMMARY REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # ROI Summary
        if "roi" in results and results["roi"]:
            f.write("\n" + "="*70 + "\n")
            f.write("1. COST-BENEFIT / ROI ANALYSIS\n")
            f.write("="*70 + "\n\n")
            
            roi = results["roi"]
            f.write(f"Implementation Cost:     ${roi['costs']['implementation']:,.2f}\n")
            f.write(f"Annual Operational Cost: ${roi['costs']['annual_operational']:,.2f}\n")
            f.write(f"Total Annual Benefits:   ${roi['benefits']['total_annual']:,.2f}\n")
            f.write(f"Net Annual Benefit:      ${roi['benefits']['net_annual']:,.2f}\n\n")
            
            f.write(f"ROI Year 1:  {roi['roi']['year_1']:.2f}%\n")
            f.write(f"ROI Year 3:  {roi['roi']['year_3']:.2f}%\n")
            f.write(f"ROI Year 5:  {roi['roi']['year_5']:.2f}%\n\n")
            
            f.write(f"Payback Period: {roi['roi']['payback_months']:.1f} months ")
            f.write(f"({roi['roi']['payback_years']:.2f} years)\n\n")
            
            f.write("Key Metrics:\n")
            f.write(f"  - Incidents Automated:  {roi['metrics']['incidents_automated']}\n")
            f.write(f"  - Fraud Prevented:      {roi['metrics']['fraud_prevented']}\n")
            f.write(f"  - FP Reduction:         {roi['metrics']['fp_reduction']}\n")
        
        # FP/FN Summary
        if "fp_fn" in results and results["fp_fn"]:
            f.write("\n" + "="*70 + "\n")
            f.write("2. FALSE POSITIVE/NEGATIVE ANALYSIS\n")
            f.write("="*70 + "\n\n")
            
            fp_fn = results["fp_fn"]
            
            f.write("Baseline System:\n")
            cm_base = fp_fn["baseline"]["confusion_matrix"]
            f.write(f"  TP: {cm_base['TP']}, TN: {cm_base['TN']}, ")
            f.write(f"FP: {cm_base['FP']}, FN: {cm_base['FN']}\n")
            
            metrics_base = fp_fn["baseline"]["metrics"]
            f.write(f"  Precision: {metrics_base['precision']:.4f}\n")
            f.write(f"  Recall:    {metrics_base['recall']:.4f}\n")
            f.write(f"  F1-Score:  {metrics_base['f1_score']:.4f}\n\n")
            
            f.write("SecureBank™ System:\n")
            cm_sb = fp_fn["securebank"]["confusion_matrix"]
            f.write(f"  TP: {cm_sb['TP']}, TN: {cm_sb['TN']}, ")
            f.write(f"FP: {cm_sb['FP']}, FN: {cm_sb['FN']}\n")
            
            metrics_sb = fp_fn["securebank"]["metrics"]
            f.write(f"  Precision: {metrics_sb['precision']:.4f}\n")
            f.write(f"  Recall:    {metrics_sb['recall']:.4f}\n")
            f.write(f"  F1-Score:  {metrics_sb['f1_score']:.4f}\n\n")
            
            f.write("Improvements:\n")
            imp = fp_fn["improvement"]
            f.write(f"  Cost Reduction:      {imp['cost_reduction_pct']:.2f}%\n")
            f.write(f"  Cost Savings:        ${imp['cost_savings']:,.2f}\n")
            f.write(f"  Precision Gain:      +{imp['precision_improvement']:.4f}\n")
            f.write(f"  Recall Gain:         +{imp['recall_improvement']:.4f}\n")
            f.write(f"  F1-Score Gain:       +{imp['f1_improvement']:.4f}\n")
        
        # Scalability Summary
        if "scalability" in results and results["scalability"]:
            f.write("\n" + "="*70 + "\n")
            f.write("3. SCALABILITY ANALYSIS\n")
            f.write("="*70 + "\n\n")
            
            scal = results["scalability"]
            
            f.write("Load Testing Results:\n\n")
            f.write(f"{'Load (tx/day)':<15} {'Latency (ms)':<15} {'Throughput (tps)':<20} ")
            f.write(f"{'CPU (%)':<10} {'Memory (GB)':<12}\n")
            f.write("-" * 70 + "\n")
            
            for load in scal["load_levels"]:
                r = scal["results"][load]
                f.write(f"{load:<15,} {r['avg_latency_ms']:<15.2f} ")
                f.write(f"{r['throughput_tps']:<20.2f} ")
                f.write(f"{r['cpu_usage_pct']:<10.1f} {r['memory_gb']:<12.2f}\n")
            
            f.write("\nBottlenecks Identified:\n")
            if scal["bottlenecks"]:
                for b in scal["bottlenecks"]:
                    f.write(f"  - {b}\n")
            else:
                f.write("  - No critical bottlenecks detected\n")
            
            f.write("\nRecommendations:\n")
            for rec in scal["recommendations"]:
                f.write(f"  - {rec}\n")
        
        # Sensitivity Summary
        if "sensitivity" in results and results["sensitivity"]:
            f.write("\n" + "="*70 + "\n")
            f.write("4. SENSITIVITY ANALYSIS\n")
            f.write("="*70 + "\n\n")
            
            sens = results["sensitivity"]
            
            f.write("Parameter Sensitivity Scores:\n\n")
            f.write(f"{'Parameter':<25} {'TII':<10} {'SAE':<10} {'ITAL':<10} {'Aggregate':<12}\n")
            f.write("-" * 70 + "\n")
            
            for param, scores in sens["sensitivity_scores"].items():
                f.write(f"{param:<25} ")
                f.write(f"{scores['tii_sensitivity']:<10.4f} ")
                f.write(f"{scores['sae_sensitivity']:<10.4f} ")
                f.write(f"{scores['ital_sensitivity']:<10.4f} ")
                f.write(f"{scores['aggregate_sensitivity']:<12.4f}\n")
            
            f.write("\nCritical Parameters (most sensitive):\n")
            for param in sens["critical_parameters"]:
                f.write(f"  - {param}\n")
            
            f.write("\nRecommendations:\n")
            for rec in sens["recommendations"]:
                f.write(f"  - {rec}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    print(f"  ✓ Summary report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="SecureBank™ Advanced Analyses Runner"
    )
    parser.add_argument(
        '--mode',
        choices=['all', 'roi', 'fp_fn', 'scalability', 'sensitivity'],
        default='all',
        help='Analysis mode to run (default: all)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for results (default: experiments/advanced_TIMESTAMP)'
    )
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip plot generation'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick mode: skip time-consuming analyses (scalability, sensitivity)'
    )
    
    args = parser.parse_args()
    
    # Setup output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / "experiments" / f"advanced_{timestamp}"
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "="*70)
    print("SECUREBANK™ ADVANCED ANALYSES RUNNER")
    print("="*70)
    print(f"\nMode:       {args.mode}")
    print(f"Output Dir: {output_dir}")
    print(f"Quick Mode: {args.quick}")
    print("="*70 + "\n")
    
    # Load configuration
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Run simulation once to get baseline logs
    print("Running baseline simulation...")
    baseline_logs, securebank_logs = run_simulation(config)
    print(f"  ✓ Generated {len(baseline_logs)} events\n")
    
    # Execute analyses based on mode
    results = {}
    
    if args.mode in ['all', 'roi']:
        print("\n" + "="*70)
        print("ROI ANALYSIS")
        print("="*70)
        results["roi"] = compute_roi_analysis(baseline_logs, securebank_logs)
        print(f"\n  ROI Year 1: {results['roi']['roi']['year_1']:.2f}%")
        print(f"  Payback:    {results['roi']['roi']['payback_months']:.1f} months")
    
    if args.mode in ['all', 'fp_fn']:
        print("\n" + "="*70)
        print("FALSE POSITIVE/NEGATIVE ANALYSIS")
        print("="*70)
        results["fp_fn"] = compute_false_positive_negative_analysis(
            baseline_logs, securebank_logs
        )
        print(f"\n  SecureBank F1-Score: {results['fp_fn']['securebank']['metrics']['f1_score']:.4f}")
        print(f"  Cost Reduction:      {results['fp_fn']['improvement']['cost_reduction_pct']:.2f}%")
    
    if args.mode in ['all', 'scalability'] and not args.quick:
        print("\n" + "="*70)
        print("SCALABILITY ANALYSIS")
        print("="*70)
        results["scalability"] = compute_scalability_analysis(
            run_simulation,
            config,
            load_levels=[1000, 5000, 10000, 50000, 100000]
        )
        max_load = max(results["scalability"]["load_levels"])
        print(f"\n  Max Load Tested: {max_load:,} tx/day")
    
    if args.mode in ['all', 'sensitivity'] and not args.quick:
        print("\n" + "="*70)
        print("SENSITIVITY ANALYSIS")
        print("="*70)
        results["sensitivity"] = compute_sensitivity_analysis(
            run_simulation,
            config,
            num_samples=5
        )
        print(f"\n  Critical Params: {', '.join(results['sensitivity']['critical_parameters'])}")
    
    # Save results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70 + "\n")
    
    save_results_json(results, output_dir / "advanced_results.json")
    generate_summary_report(results, output_dir / "summary_report.txt")
    
    # Generate plots
    if not args.no_plots:
        print("\n" + "="*70)
        print("GENERATING PLOTS")
        print("="*70)
        generate_all_advanced_plots(results, output_dir / "plots")
    
    print("\n" + "="*70)
    print("ADVANCED ANALYSES COMPLETED")
    print("="*70)
    print(f"\nAll results saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Review summary_report.txt")
    print("  2. Check plots/ directory for visualizations")
    print("  3. Use advanced_results.json for further analysis")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
