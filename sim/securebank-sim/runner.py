# runner.py
import argparse
import copy
import csv
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from simulator import run_simulation
from metrics import (
    compute_ital,
    compute_sae,
    compute_scenario_detection,
    compute_stats,
    compute_tii,
    compute_tii_per_service,
)
from plots import generate_plots


# ----------------------------------------------------------------
# Paths baseados no local deste arquivo (securebank-sim)
# ----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXP_ROOT = BASE_DIR / "experiments"
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_EXP_ROOT.mkdir(exist_ok=True)


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_mean_std(values: List[float]) -> Tuple[Optional[float], Optional[float]]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def _t_critical_95(df: int) -> float:
    """
    t crítico para IC 95% (bicaudal).
    Tenta scipy; se não existir, usa aproximação (ok para df>=30).
    """
    try:
        from scipy.stats import t  # type: ignore
        return float(t.ppf(0.975, df))
    except Exception:
        # Aproximação grosseira: para df>=30, t~1.96
        return 1.96 if df >= 30 else 2.13


def _ci95(values: List[float]) -> Dict[str, Optional[float]]:
    """
    IC 95% da média: mean ± t * (sd/sqrt(n))
    """
    n = len(values)
    mean, sd = _safe_mean_std(values)
    if mean is None or sd is None or n == 0:
        return {"mean": None, "sd": None, "n": n, "ci95_low": None, "ci95_high": None}
    if n == 1:
        return {"mean": mean, "sd": sd, "n": n, "ci95_low": mean, "ci95_high": mean}

    tcrit = _t_critical_95(n - 1)
    half = tcrit * (sd / (n ** 0.5))
    return {
        "mean": mean,
        "sd": sd,
        "n": n,
        "ci95_low": mean - half,
        "ci95_high": mean + half,
    }


def _cohens_d(a: List[float], b: List[float]) -> Optional[float]:
    """
    Cohen's d (efeito): (mean_b - mean_a) / pooled_sd
    """
    if len(a) < 2 or len(b) < 2:
        return None
    ma, sa = statistics.mean(a), statistics.stdev(a)
    mb, sb = statistics.mean(b), statistics.stdev(b)
    na, nb = len(a), len(b)
    pooled = (((na - 1) * (sa ** 2) + (nb - 1) * (sb ** 2)) / (na + nb - 2)) ** 0.5
    if pooled == 0:
        return None
    return (mb - ma) / pooled


def _get_git_info(base_dir: Path) -> Dict[str, Any]:
    """
    Captura commit e status do repositório, se existir.
    """
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(base_dir),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(base_dir),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return {"git_commit": commit, "git_dirty": bool(status), "git_status": status}
    except Exception:
        return {"git_commit": None, "git_dirty": None, "git_status": None}


def _pip_freeze() -> Optional[str]:
    """
    Tenta registrar ambiente (pip freeze). Se falhar, retorna None.
    """
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return None


def run_experiment(
    num_runs: Optional[int] = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
    exp_root: Path = DEFAULT_EXP_ROOT,
    save_run_logs: int = 1,
) -> Path:
    """
    Roda experimento Monte Carlo e salva outputs.
    Retorna o diretório do experimento.
    """
    exp_root.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = exp_root / f"exp_{timestamp}"
    exp_dir.mkdir(exist_ok=True)

    if not config_path.exists():
        raise FileNotFoundError(f"config.json não encontrado em: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        base_config = json.load(f)

    logging_cfg = base_config.get("logging", {})
    ital_params = base_config.get("ital_params", {})
    base_seed = int(base_config.get("seed", 42))

    if num_runs is None:
        num_runs = int(base_config.get("num_runs", 30))
        num_runs_source = "config"
    else:
        num_runs_source = "cli"

    # ----------------- Metadata forense -----------------
    run_metadata = {
        "timestamp": timestamp,
        "command": " ".join(sys.argv),
        "base_dir": str(BASE_DIR),
        "python": sys.version,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "config_path": str(config_path),
        "config_sha256": _file_sha256(config_path),
        "base_seed": base_seed,
        "num_runs": num_runs,
        "num_runs_source": num_runs_source,
        "pip_freeze": _pip_freeze(),
        **_get_git_info(BASE_DIR),
    }
    with (exp_dir / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(run_metadata, f, indent=2)

    # ----------------- Acumuladores -----------------
    runs_metrics: List[Dict[str, Any]] = []
    tii_baseline_vals: List[float] = []
    tii_sb_vals: List[float] = []
    sae_baseline_vals: List[float] = []
    sae_sb_vals: List[float] = []
    ital_baseline_vals: List[float] = []
    ital_sb_vals: List[float] = []
    total_events_list: List[int] = []
    total_attacks_list: List[int] = []

    saved_baseline_logs: List[List[Dict[str, Any]]] = []
    saved_sb_logs: List[List[Dict[str, Any]]] = []

    # ----------------- Runs -----------------
    for run_id in range(num_runs):
        cfg = copy.deepcopy(base_config)
        run_seed = base_seed + run_id
        cfg["seed"] = run_seed

        baseline_logs, sb_logs = run_simulation(cfg)

        # Sanidade: cenários comparáveis (mesma quantidade de eventos)
        if len(baseline_logs) != len(sb_logs):
            print(
                f"[WARN] run {run_id}: baseline_logs({len(baseline_logs)}) != securebank_logs({len(sb_logs)})"
            )

        total_events = len(baseline_logs)
        total_attacks = sum(1 for log in baseline_logs if log.get("is_attack"))

        total_events_list.append(total_events)
        total_attacks_list.append(total_attacks)

        tii_baseline = float(compute_tii(baseline_logs))
        tii_sb = float(compute_tii(sb_logs))
        sae_baseline = float(compute_sae(baseline_logs))
        sae_sb = float(compute_sae(sb_logs))
        ital_baseline = float(compute_ital(baseline_logs, ital_params))
        ital_sb = float(compute_ital(sb_logs, ital_params))

        # Sanidade: métricas fora do esperado
        for name, val in [
            ("TII_baseline", tii_baseline),
            ("TII_securebank", tii_sb),
            ("SAE_baseline", sae_baseline),
            ("SAE_securebank", sae_sb),
            ("ITAL_baseline", ital_baseline),
            ("ITAL_securebank", ital_sb),
        ]:
            if not (val == val):  # NaN check
                print(f"[WARN] {name} é NaN no run {run_id}")
            if abs(val) > 10_000:
                print(f"[WARN] {name} muito alto ({val}) no run {run_id} — verifique escala/normalização.")

        tii_baseline_vals.append(tii_baseline)
        tii_sb_vals.append(tii_sb)
        sae_baseline_vals.append(sae_baseline)
        sae_sb_vals.append(sae_sb)
        ital_baseline_vals.append(ital_baseline)
        ital_sb_vals.append(ital_sb)

        runs_metrics.append(
            {
                "run_id": run_id,
                "seed": run_seed,
                "total_events": total_events,
                "total_attacks": total_attacks,
                "TII_baseline": tii_baseline,
                "TII_securebank": tii_sb,
                "SAE_baseline": sae_baseline,
                "SAE_securebank": sae_sb,
                "ITAL_baseline": ital_baseline,
                "ITAL_securebank": ital_sb,
            }
        )

        # Salvar logs detalhados (N primeiros runs)
        if save_run_logs > 0 and run_id < save_run_logs:
            saved_baseline_logs.append(baseline_logs)
            saved_sb_logs.append(sb_logs)

    # ----------------- Estatística agregada -----------------
    total_events_mean, total_events_std = _safe_mean_std([float(x) for x in total_events_list])
    total_attacks_mean, total_attacks_std = _safe_mean_std([float(x) for x in total_attacks_list])

    summary_results = {
        "meta": {
            "experiment_name": base_config.get("experiment_name"),
            "description": base_config.get("description"),
            "version": base_config.get("version"),
            "base_seed": base_seed,
            "num_runs": num_runs,
            "num_runs_source": num_runs_source,
            "total_events_mean": total_events_mean,
            "total_events_std": total_events_std,
            "total_attacks_mean": total_attacks_mean,
            "total_attacks_std": total_attacks_std,
        },
        "TII": {
            **_ci95(tii_baseline_vals),
            "securebank": _ci95(tii_sb_vals),
            "cohens_d_securebank_vs_baseline": _cohens_d(tii_baseline_vals, tii_sb_vals),
        },
        "SAE": {
            "baseline": _ci95(sae_baseline_vals),
            "securebank": _ci95(sae_sb_vals),
            "cohens_d_securebank_vs_baseline": _cohens_d(sae_baseline_vals, sae_sb_vals),
        },
        "ITAL": {
            "baseline": _ci95(ital_baseline_vals),
            "securebank": _ci95(ital_sb_vals),
            "cohens_d_securebank_vs_baseline": _cohens_d(ital_baseline_vals, ital_sb_vals),
        },
    }

    # Compatível com plots antigos (média)
    results_for_plots = {
        "meta": summary_results["meta"],
        "TII": {"baseline": statistics.mean(tii_baseline_vals), "securebank": statistics.mean(tii_sb_vals)},
        "SAE": {"baseline": statistics.mean(sae_baseline_vals), "securebank": statistics.mean(sae_sb_vals)},
        "ITAL": {"baseline": statistics.mean(ital_baseline_vals), "securebank": statistics.mean(ital_sb_vals)},
    }

    with (exp_dir / "summary_results.json").open("w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)

    with (exp_dir / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results_for_plots, f, indent=2)

    # CSV por run
    with (exp_dir / "metrics_runs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "run_id",
                "seed",
                "total_events",
                "total_attacks",
                "TII_baseline",
                "TII_securebank",
                "SAE_baseline",
                "SAE_securebank",
                "ITAL_baseline",
                "ITAL_securebank",
            ]
        )
        for rm in runs_metrics:
            w.writerow(
                [
                    rm["run_id"],
                    rm["seed"],
                    rm["total_events"],
                    rm["total_attacks"],
                    rm["TII_baseline"],
                    rm["TII_securebank"],
                    rm["SAE_baseline"],
                    rm["SAE_securebank"],
                    rm["ITAL_baseline"],
                    rm["ITAL_securebank"],
                ]
            )

    # CSV agregado (mean/std)
    def _write_summary_row(w, metric: str, policy: str, values: List[float]):
        m, s = _safe_mean_std(values)
        w.writerow([metric, policy, m, s])

    with (exp_dir / "metrics_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "policy", "mean", "std"])
        _write_summary_row(w, "TII", "baseline", tii_baseline_vals)
        _write_summary_row(w, "TII", "securebank", tii_sb_vals)
        _write_summary_row(w, "SAE", "baseline", sae_baseline_vals)
        _write_summary_row(w, "SAE", "securebank", sae_sb_vals)
        _write_summary_row(w, "ITAL", "baseline", ital_baseline_vals)
        _write_summary_row(w, "ITAL", "securebank", ital_sb_vals)

    # Detalhes e artefatos para runs salvos
    for i, (b_logs, s_logs) in enumerate(zip(saved_baseline_logs, saved_sb_logs)):
        with (exp_dir / f"baseline_logs_run{i}.json").open("w", encoding="utf-8") as f:
            json.dump(b_logs, f, indent=2)
        with (exp_dir / f"securebank_logs_run{i}.json").open("w", encoding="utf-8") as f:
            json.dump(s_logs, f, indent=2)

        if logging_cfg.get("save_stats", True):
            stats = {"baseline": compute_stats(b_logs), "securebank": compute_stats(s_logs)}
            with (exp_dir / f"stats_run{i}.json").open("w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)

        if logging_cfg.get("save_timeline", True):
            n = len(s_logs)
            timeline = {
                "step": list(range(n)),
                "sb_theta": [ev.get("theta") for ev in s_logs],
                "sb_risk": [ev.get("risk") for ev in s_logs],
                "sb_I_before": [ev.get("I_u") for ev in s_logs],
                "sb_I_after": [ev.get("new_I") for ev in s_logs],
                "sb_action": [ev.get("action") for ev in s_logs],
                "is_attack": [bool(ev.get("is_attack")) for ev in s_logs],
                "baseline_action": [ev.get("action") for ev in b_logs],
            }
            with (exp_dir / f"timeline_run{i}.json").open("w", encoding="utf-8") as f:
                json.dump(timeline, f, indent=2)

        tii_per_service = {"baseline": compute_tii_per_service(b_logs), "securebank": compute_tii_per_service(s_logs)}
        with (exp_dir / f"tii_per_service_run{i}.json").open("w", encoding="utf-8") as f:
            json.dump(tii_per_service, f, indent=2)

        scenario_detection = compute_scenario_detection(b_logs, s_logs)
        with (exp_dir / f"scenario_detection_run{i}.json").open("w", encoding="utf-8") as f:
            json.dump(scenario_detection, f, indent=2)

    # Plots
    if logging_cfg.get("save_plots", True):
        generate_plots(results_for_plots, output_dir=exp_dir)

    print("\n=== Experiment Finished ===")
    print(f"Results saved to: {exp_dir}")
    print(f"Number of runs: {num_runs} (source={num_runs_source})")
    print(f"Config SHA256: {_file_sha256(config_path)}")
    return exp_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SecureBank-SIM Runner (simulation)")
    parser.add_argument(
        "--mode",
        choices=["simulation", "empirical", "both"],
        default="simulation",
        help="Modo de execução. Este runner executa apenas 'simulation'.",
    )
    parser.add_argument(
        "--num-runs",
        type=int,
        default=None,
        help="Número de execuções Monte Carlo. Se omitido, usa config.json ou 30.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Caminho para o config.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_EXP_ROOT),
        help="Diretório raiz para salvar experiments/exp_*.",
    )
    parser.add_argument(
        "--save-run-logs",
        type=int,
        default=1,
        help="Quantos runs completos salvar (logs/timeline/stats). 0 = não salva logs detalhados.",
    )

    args = parser.parse_args()

    if args.mode != "simulation":
        print(f"[WARN] mode='{args.mode}' não está implementado neste runner.py. Executando 'simulation'.")

    run_experiment(
        num_runs=args.num_runs,
        config_path=Path(args.config).expanduser().resolve(),
        exp_root=Path(args.output_dir).expanduser().resolve(),
        save_run_logs=max(0, int(args.save_run_logs)),
    )
