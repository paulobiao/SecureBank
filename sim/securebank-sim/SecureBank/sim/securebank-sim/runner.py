# runner.py
import json
import os
from datetime import datetime

from simulator import run_simulation
from metrics import compute_tii, compute_sae, compute_ital
from plots import generate_plots

# ----------------------------------------------------------------
# Create experiment directory
# ----------------------------------------------------------------
os.makedirs("experiments", exist_ok=True)


def run_experiment():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = f"experiments/exp_{timestamp}"
    os.makedirs(exp_dir, exist_ok=True)

    # Load config
    with open("config.json", "r") as f:
        CONFIG = json.load(f)

    # Run simulation
    baseline_logs, sb_logs = run_simulation(CONFIG)

    # Meta: totais
    total_events = len(baseline_logs)
    total_attacks = sum(1 for log in baseline_logs if log.get("is_attack"))

    # Parâmetros de ITAL vindos do JSON
    ital_params = CONFIG.get("ital_params", {})

    # Compute metrics
    results = {
        "meta": {
            "total_events": total_events,
            "total_attacks": total_attacks,
        },
        "TII": {
            "baseline": compute_tii(baseline_logs),
            "securebank": compute_tii(sb_logs),
        },
        "SAE": {
            "baseline": compute_sae(baseline_logs),
            "securebank": compute_sae(sb_logs),
        },
        "ITAL": {
            "baseline": compute_ital(baseline_logs, ital_params),
            "securebank": compute_ital(sb_logs, ital_params),
        },
    }

    # Save logs
    with open(os.path.join(exp_dir, "baseline_logs.json"), "w") as f:
        json.dump(baseline_logs, f, indent=2)

    with open(os.path.join(exp_dir, "securebank_logs.json"), "w") as f:
        json.dump(sb_logs, f, indent=2)

    # Save results
    with open(os.path.join(exp_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Generate plots dynamically para ESTE experimento
    generate_plots(results, output_dir=exp_dir)

    print("\n=== Experiment Finished ===")
    print(f"Results saved to: {exp_dir}")


if __name__ == "__main__":
    run_experiment()
