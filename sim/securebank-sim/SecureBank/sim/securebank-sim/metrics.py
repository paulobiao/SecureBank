from collections import defaultdict


def compute_tii(logs):
    """
    Transactional Integrity Index (TII)

    Ideia:
    - mede a proporção de transações válidas (não ataque E permitidas),
      ponderada pela criticidade do serviço.
    - Usa campos FLAT do log: "service", "allowed", "is_attack".
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
        service = ev.get("service")
        if service is None:
            continue

        total[service] += 1

        # conta como transação íntegra se:
        # - não é ataque
        # - foi permitida
        if ev.get("allowed") and not ev.get("is_attack", False):
            valid[service] += 1

    num = 0.0
    den = 0.0
    for s in total:
        w = service_weights.get(s, 1.0)
        num += w * valid[s]
        den += w * total[s]

    return num / den if den > 0 else 0.0


def compute_sae(logs):
    """
    Security Automation Efficiency (SAE)

    Ideia:
    - entre todos os incidentes (ataques),
      quantos foram tratados automaticamente pelo PDP
      (decisão "block" ou "step_up").
    - Usa campos: "is_attack", "action".
    """
    total_incidents = 0
    auto_handled = 0

    for ev in logs:
        if ev.get("is_attack"):
            total_incidents += 1
            if ev.get("action") in ["block", "step_up"]:
                auto_handled += 1

    return auto_handled / total_incidents if total_incidents > 0 else 0.0


def compute_ital(logs, ital_params=None):
    """
    Identity Trust Adaptation Level (ITAL)

    Ideia:
    - mede o quanto a confiança de identidade se adapta ao longo dos eventos
      (diferença entre I_u e new_I por usuário)
    - combina isso com a eficácia contra ataques (ataques bloqueados/step_up)
    - baseline tende a ~0 (sem campos de confiança), SecureBank > 0 e
      refletindo adaptação e eficácia.

    Espera campos nos logs do SecureBank:
      - "user_id"
      - "I_u"   (trust antes da decisão)
      - "new_I" (trust depois da decisão)
      - "is_attack"
      - "action"  ("allow"/"step_up"/"block")
    """
    if ital_params is None:
        ital_params = {}

    drift_weight = ital_params.get("identity_drift_factor", 0.6)

    if not logs:
        return 0.0

    # --- 1) Drift de confiança por usuário ---
    # Em vez de reconstruir uma série temporal longa, usamos
    # a variação local |new_I - I_u| em cada evento.
    per_user_drift_sum = defaultdict(float)
    per_user_drift_count = defaultdict(int)

    has_trust_info = False

    for ev in logs:
        uid = ev.get("user_id")
        I_u = ev.get("I_u")
        new_I = ev.get("new_I")

        # Logs de baseline não têm esses campos -> ignoramos
        if uid is None or I_u is None or new_I is None:
            continue

        has_trust_info = True
        diff = abs(float(new_I) - float(I_u))
        per_user_drift_sum[uid] += diff
        per_user_drift_count[uid] += 1

    if not has_trust_info:
        # Ex.: baseline: ITAL = 0 por definição
        return 0.0

    # média de drift por usuário, depois média entre usuários
    user_drifts = []
    for uid, total_diff in per_user_drift_sum.items():
        cnt = per_user_drift_count[uid]
        if cnt > 0:
            user_drifts.append(total_diff / cnt)

    avg_drift = sum(user_drifts) / len(user_drifts) if user_drifts else 0.0

    # --- 2) Fator de eficácia contra ataques ---
    total_attacks = 0
    blocked_or_stepped = 0

    for ev in logs:
        if ev.get("is_attack"):
            total_attacks += 1
            if ev.get("action") in ["block", "step_up"]:
                blocked_or_stepped += 1

    attack_factor = (
        blocked_or_stepped / total_attacks if total_attacks > 0 else 0.0
    )

    # --- 3) Combinação ponderada ---
    ital = drift_weight * avg_drift + (1.0 - drift_weight) * attack_factor
    return ital
