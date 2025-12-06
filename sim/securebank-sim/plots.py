# plots.py
import numpy as np
import matplotlib.pyplot as plt
import os

# -------------------------------------------------------------------
# Create output directory
# -------------------------------------------------------------------
os.makedirs("plots", exist_ok=True)

# -------------------------------------------------------------------
# Hard-coded results from your simulation output
# -------------------------------------------------------------------
tii_baseline = 0.945
tii_sb = 0.942

sae_baseline = 0.004
sae_sb = 0.118

ital_baseline = 0.000
ital_sb = 0.015

# -------------------------------------------------------------------
# 1) Bar Plot – TII comparison
# -------------------------------------------------------------------
plt.figure(figsize=(6,4))
plt.bar(["Baseline", "SecureBank"], [tii_baseline, tii_sb])
plt.title("Transactional Integrity Index (TII)")
plt.ylabel("Score")
plt.savefig("plots/tii_bar.png", dpi=200)
plt.close()

# -------------------------------------------------------------------
# 2) Bar Plot – Security Automation Efficiency (SAE)
# -------------------------------------------------------------------
plt.figure(figsize=(6,4))
plt.bar(["Baseline", "SecureBank"], [sae_baseline, sae_sb])
plt.title("Security Automation Efficiency (SAE)")
plt.ylabel("Score")
plt.savefig("plots/sae_bar.png", dpi=200)
plt.close()

# -------------------------------------------------------------------
# 3) Bar Plot – Identity Trust Adaptation Level (ITAL)
# -------------------------------------------------------------------
plt.figure(figsize=(6,4))
plt.bar(["Baseline", "SecureBank"], [ital_baseline, ital_sb])
plt.title("Identity Trust Adaptation Level (ITAL)")
plt.ylabel("Score")
plt.savefig("plots/ital_bar.png", dpi=200)
plt.close()

# -------------------------------------------------------------------
# 4) Radar Chart – Overall Security Posture
# -------------------------------------------------------------------
labels = ["TII", "SAE", "ITAL"]

baseline_vals = [tii_baseline, sae_baseline, ital_baseline]
sb_vals = [tii_sb, sae_sb, ital_sb]

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
baseline_vals += baseline_vals[:1]
sb_vals += sb_vals[:1]
angles = np.concatenate([angles, [angles[0]]])

plt.figure(figsize=(6,6))
plt.polar(angles, baseline_vals, label="Baseline")
plt.polar(angles, sb_vals, label="SecureBank")
plt.fill(angles, sb_vals, alpha=0.2)
plt.title("Security Posture Comparison (Radar Chart)")
plt.legend(loc="upper right")
plt.savefig("plots/security_radar.png", dpi=200)
plt.close()

print("Plots generated successfully in /plots folder!")

def generate_plots(results, output_dir="plots"):
    os.makedirs(output_dir, exist_ok=True)

    tii_b = results["TII"]["baseline"]
    tii_s = results["TII"]["securebank"]

    sae_b = results["SAE"]["baseline"]
    sae_s = results["SAE"]["securebank"]

    ital_b = results["ITAL"]["baseline"]
    ital_s = results["ITAL"]["securebank"]

    # Reuse the bar plots but save in output_dir instead
    plt.figure()
    plt.bar(["Baseline", "SecureBank"], [tii_b, tii_s])
    plt.title("Transactional Integrity Index (TII)")
    plt.savefig(f"{output_dir}/tii.png")
    plt.close()

    plt.figure()
    plt.bar(["Baseline", "SecureBank"], [sae_b, sae_s])
    plt.title("Security Automation Efficiency (SAE)")
    plt.savefig(f"{output_dir}/sae.png")
    plt.close()

    plt.figure()
    plt.bar(["Baseline", "SecureBank"], [ital_b, ital_s])
    plt.title("Identity Trust Adaptation Level (ITAL)")
    plt.savefig(f"{output_dir}/ital.png")
    plt.close()

    print("Dynamic plots generated!")
