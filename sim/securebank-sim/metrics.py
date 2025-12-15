# metrics.py
from collections import defaultdict
from statistics import mean, stdev


def compute_tii(logs):
    """
    Transactional Integrity Index:
    proporção de transações válidas (não ataque, permitidas)
    ponderada pela criticidade do serviço.
    """
    valid = defaultdict(int)
    total = defaultdict(int)

    service_weights = {
        "payments": 1.0,
        "settlement": 1.2,
        "risk_analytics": 0.8,
        "aml": 1.1,
        "customer_identity": 0.9,
    }

    for ev in logs:
        s = ev["tx"]["service"]
        total[s] += 1
        if ev["allowed"] and not ev["is_attack"]:
            valid[s] += 1

    num = 0.0
    den = 0.0
    for s in total:
        w = service_weights.get(s, 1.0)
        num += w * valid[s]
        den += w * total[s]

    return num / den if den > 0 else 0.0


def compute_tii_per_service(logs):
    """
    TII por serviço (não ponderado).

    Retorna um dict:
        { service_name: {"valid": x, "total": y, "tii": x/y} }
    """
    valid = defaultdict(int)
    total = defaultdict(int)

    for ev in logs:
        s = ev["tx"].get("service")
        if not s:
            continue
        total[s] += 1
        if ev.get("allowed") and not ev.get("is_attack", False):
            valid[s] += 1

    result = {}
    for s in total:
        v = valid[s]
        t = total[s]
        result[s] = {
            "valid": v,
            "total": t,
            "tii": (v / t) if t > 0 else 0.0,
        }
    return result


def compute_sae(logs):
    """
    Security Automation Efficiency:
    entre todos os incidentes (ataques),
    quantos foram tratados automaticamente (block/step_up).
    """
    I_tot = 0
    I_auto = 0

    for ev in logs:
        if ev["is_attack"]:
            I_tot += 1
            if ev.get("action") in ["block", "step_up"]:
                I_auto += 1

    return I_auto / I_tot if I_tot > 0 else 0.0


def compute_ital(logs, ital_params=None):
    """
    Identity Trust Adaptation Level (ITAL)

    Mede:
    - quão forte o "drift" de confiança ocorre por usuário ao longo do tempo;
    - quão bem ataques são bloqueados.

    logs de SecureBank devem conter:
    - "I_u" e "new_I" (antes e depois da decisão)
    - "action" indicando allow/step_up/block
    """
    if ital_params is None:
        ital_params = {}

    drift_weight = ital_params.get("identity_drift_factor", 0.6)

    if not logs:
        return 0.0

    # --- 1) Drift de trust por usuário ---
    last_trust = {}
    total_drift = 0.0
    drift_count = 0

    for log in logs:
        uid = log.get("tx", {}).get("user_id")
        trust_before = log.get("I_u")
        trust_after = log.get("new_I")

        if uid is None or trust_before is None or trust_after is None:
            continue

        # drift local neste evento
        diff = abs(trust_after - trust_before)
        total_drift += diff
        drift_count += 1

        last_trust[uid] = trust_after

    avg_drift = (total_drift / drift_count) if drift_count > 0 else 0.0

    # --- 2) Fator de eficácia em ataques (ataques bloqueados) ---
    total_attacks = 0
    blocked_attacks = 0

    for log in logs:
        if log.get("is_attack"):
            total_attacks += 1
            if log.get("action") == "block":
                blocked_attacks += 1

    if total_attacks > 0:
        attack_factor = blocked_attacks / total_attacks
    else:
        attack_factor = 0.0

    # --- 3) Combinação ponderada ---
    ital = drift_weight * avg_drift + (1.0 - drift_weight) * attack_factor
    return ital


def compute_scenario_detection(baseline_logs, securebank_logs):
    """
    Compara baseline x SecureBank por cenário de ataque.

    Retorna um dict:
      {
        scenario_id: {
          "name": "...",
          "total_attacks": N,
          "baseline": {
             "blocked": x,
             "step_up": y,
             "allowed": z
          },
          "securebank": {
             "blocked": x2,
             "step_up": y2,
             "allowed": z2
          }
        },
        ...
      }
    """
    # mapeia IDs para descrições amigáveis
    scenario_names = {
        1: "credential_compromise",
        2: "insider_lateral_movement",
        3: "api_abuse",
        4: "money_laundering",
        5: "session_hijacking",
    }

    # acumuladores
    stats = {}
    for sid in scenario_names:
        stats[sid] = {
            "name": scenario_names[sid],
            "total_attacks": 0,
            "baseline": {"blocked": 0, "step_up": 0, "allowed": 0},
            "securebank": {"blocked": 0, "step_up": 0, "allowed": 0},
        }

    # assumimos que baseline_logs e securebank_logs têm mesmo comprimento
    for base_ev, sb_ev in zip(baseline_logs, securebank_logs):
        if not base_ev.get("is_attack"):
            continue

        sid = base_ev.get("scenario")
        if sid not in stats:
            # cenario inesperado, inicializa dinamicamente
            stats[sid] = {
                "name": f"scenario_{sid}",
                "total_attacks": 0,
                "baseline": {"blocked": 0, "step_up": 0, "allowed": 0},
                "securebank": {"blocked": 0, "step_up": 0, "allowed": 0},
            }

        stats[sid]["total_attacks"] += 1

              # baseline
        act_b = base_ev.get("action")
        if act_b:
            if act_b == "allow":
                key_b = "allowed"
            elif act_b == "block":
                key_b = "blocked"
            else:
                key_b = act_b  # step_up
            stats[sid]["baseline"][key_b] += 1

        # securebank
        act_s = sb_ev.get("action")
        if act_s:
            if act_s == "allow":
                key_s = "allowed"
            elif act_s == "block":
                key_s = "blocked"
            else:
                key_s = act_s  # step_up
            stats[sid]["securebank"][key_s] += 1


    return stats


def compute_stats(logs):
    """
    Estatísticas descritivas básicas para suportar o artigo científico.
    Retorna um dicionário com médias, desvio padrão e contagens.
    """
    if not logs:
        return {}

    amounts = []
    risks = []
    thetas = []
    trust_before = []
    trust_after = []
    actions = defaultdict(int)
    scenarios = defaultdict(int)

    for ev in logs:
        tx = ev.get("tx", {})
        amount = tx.get("amount")
        if amount is not None:
            amounts.append(amount)

        r = ev.get("risk")
        if r is not None:
            risks.append(r)

        th = ev.get("theta")
        if th is not None:
            thetas.append(th)

        I_u = ev.get("I_u")
        new_I = ev.get("new_I")
        if I_u is not None:
            trust_before.append(I_u)
        if new_I is not None:
            trust_after.append(new_I)

        act = ev.get("action")
        if act is not None:
            actions[act] += 1

        sc = ev.get("scenario")
        if sc is not None:
            scenarios[sc] += 1

    def safe_mean(x):
        return mean(x) if x else 0.0

    def safe_stdev(x):
        return stdev(x) if len(x) > 1 else 0.0

    stats = {
        "amount_mean": safe_mean(amounts),
        "amount_std": safe_stdev(amounts),
        "risk_mean": safe_mean(risks),
        "risk_std": safe_stdev(risks),
        "theta_mean": safe_mean(thetas),
        "theta_std": safe_stdev(thetas),
        "trust_before_mean": safe_mean(trust_before),
        "trust_before_std": safe_stdev(trust_before),
        "trust_after_mean": safe_mean(trust_after),
        "trust_after_std": safe_stdev(trust_after),
        "actions": dict(actions),
        "scenarios": dict(scenarios),
        "total_events": len(logs),
    }

    return stats
