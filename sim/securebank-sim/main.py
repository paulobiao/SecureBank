from simulator import run_simulation
from metrics import compute_tii, compute_sae, compute_ital


def main():
    print("Running SecureBank-Sim...")
    baseline_logs, sb_logs = run_simulation()

    # Quantidade de eventos e ataques
    total_events = len(baseline_logs)
    total_attacks = sum(1 for ev in baseline_logs if ev["is_attack"])

    print(f"\nTotal events:   {total_events}")
    print(f"Total attacks:  {total_attacks}")

    # Métricas para baseline
    tii_base = compute_tii(baseline_logs)
    sae_base = compute_sae(baseline_logs)
    ital_base = compute_ital(baseline_logs)  # deve sair 0.0 (sem I_u)

    # Métricas para SecureBank
    tii_sb = compute_tii(sb_logs)
    sae_sb = compute_sae(sb_logs)
    ital_sb = compute_ital(sb_logs)

    print("\n=== Transactional Integrity Index (TII) ===")
    print(f"Baseline   : {tii_base:.3f}")
    print(f"SecureBank : {tii_sb:.3f}")

    print("\n=== Security Automation Efficiency (SAE) ===")
    print(f"Baseline   : {sae_base:.3f}")
    print(f"SecureBank : {sae_sb:.3f}")

    print("\n=== Identity Trust Adaptation Level (ITAL) ===")
    print(f"Baseline (esperado ~0) : {ital_base:.3f}")
    print(f"SecureBank             : {ital_sb:.3f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
