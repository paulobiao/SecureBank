import random
from collections import defaultdict

# Parâmetros globais padrão (podem ser sobrescritos pelo config.json)
NUM_USERS = 500
NUM_DEVICES = 800
NUM_STEPS = 5000       # quantidade de eventos simulados
ATTACK_PROB = 0.05     # probabilidade de um evento ser ataque

SERVICES = [
    "payments",
    "settlement",
    "risk_analytics",
    "aml",
    "customer_identity",
]


def generate_users():
    users = []
    for i in range(NUM_USERS):
        user_type = random.choice(["customer", "employee"])
        base_risk = (
            random.uniform(0.1, 0.5)
            if user_type == "customer"
            else random.uniform(0.05, 0.3)
        )
        users.append(
            {
                "id": i,
                "type": user_type,
                "base_risk": base_risk,
            }
        )
    return users


def generate_devices(users):
    """
    Garante pelo menos 1 device por usuário,
    depois adiciona devices extras aleatórios.
    """
    devices = []
    # 1 device por usuário
    for u in users:
        devices.append(
            {
                "id": len(devices),
                "owner_id": u["id"],
                "compromised": False,
            }
        )

    # devices extras, donos aleatórios
    extras = max(0, NUM_DEVICES - len(devices))
    for _ in range(extras):
        owner = random.choice(users)
        devices.append(
            {
                "id": len(devices),
                "owner_id": owner["id"],
                "compromised": False,
            }
        )
    return devices


def generate_normal_transaction(user):
    service = random.choice(SERVICES)
    amount = random.lognormvariate(mu=3.0, sigma=0.7)  # tende a valores menores
    ctx = {
        "geo": random.choice(["US-FL", "US-NY", "US-CA", "BR-SP"]),
        "hour": random.randint(0, 23),
        "channel": random.choice(["web", "mobile", "api"]),
    }
    tx = {
        "user_id": user["id"],
        "service": service,
        "amount": amount,
        "is_attack": False,
        "scenario": None,
    }
    return tx, ctx


def inject_attack(tx, ctx, scenario_id):
    tx = tx.copy()
    ctx = ctx.copy()
    tx["is_attack"] = True
    tx["scenario"] = scenario_id

    if scenario_id == 1:  # credential compromise
        ctx["geo"] = random.choice(["RU", "CN", "NG"])
        ctx["hour"] = random.randint(0, 23)
        tx["amount"] *= random.uniform(5, 50)

    elif scenario_id == 2:  # insider lateral movement
        tx["service"] = random.choice(["risk_analytics", "aml", "settlement"])

    elif scenario_id == 3:  # API abuse
        ctx["channel"] = "api"
        # na simulação isso aparece como muitos eventos em sequência

    elif scenario_id == 4:  # money laundering
        tx["amount"] = random.uniform(9000, 10000)  # abaixo de thresholds típicos

    elif scenario_id == 5:  # session hijacking
        ctx["geo"] = random.choice(["US-FL", "US-NY", "BR-SP", "DE", "IN"])
        ctx["hour"] = random.randint(0, 23)

    return tx, ctx


def baseline_pdp(event):
    """
    PDP tradicional: regrinhas simples.
    Retorna: {"allowed": bool, "action": "allow"/"step_up"/"block"}
    """
    tx = event["tx"]
    ctx = event["ctx"]

    # Regra simplificada de valor
    if tx["amount"] > 20000:
        return {"allowed": False, "action": "step_up"}

    # Localização "estranha" com valor médio/alto
    if ctx["geo"] in ["RU", "CN", "NG"] and tx["amount"] > 2000:
        return {"allowed": False, "action": "block"}

    return {"allowed": True, "action": "allow"}


def securebank_pdp(event, state):
    """
    SecureBank™ Policy Decision Point (PDP) – versão calibrada para:
    - Aumentar SAE (mais incidentes tratados automaticamente);
    - Manter TII próximo do baseline;
    - Garantir ITAL > 0 (confiança cai sob ataque).
    """
    user = event["user"]
    device = event["device"]
    tx = event["tx"]
    ctx = event["ctx"]

    # Confiança inicial de identidade e dispositivo (default 0.9)
    I_u = state["I"].get(user["id"], 0.9)
    D_d = state["D"].get(device["id"], 0.9)

    amount = tx["amount"]
    risk = 0.0

    # 1) Risco baseado em valor da transação
    if amount > 5_000:
        risk += 0.2
    if amount > 20_000:
        risk += 0.3
    if amount > 50_000:
        risk += 0.3

    # 2) Risco contextual (geo / horário)
    if ctx["geo"] not in ["US-FL", "US-NY", "US-CA", "BR-SP"]:
        risk += 0.4
    if ctx["hour"] < 5 or ctx["hour"] > 23:
        risk += 0.2

    # 3) Risco por canal e serviço
    if ctx["channel"] == "api":
        risk += 0.25

    if tx["service"] in ["settlement", "aml"] and amount > 10_000:
        risk += 0.25

    # Clamp do risco em [0, 1]
    risk = min(1.0, risk)

    # Confiança base = média de identidade e dispositivo
    base_trust = 0.5 * I_u + 0.5 * D_d

    # Combinação: quanto maior o risco, mais reduzimos o theta
    theta = base_trust - 0.5 * risk
    theta = max(0.0, min(1.0, theta))

    # Decisão de política
    if theta < 0.3:
        action = "block"
        allowed = False
    elif theta < 0.6:
        action = "step_up"  # ex: MFA extra, revisão manual
        allowed = False
    else:
        action = "allow"
        allowed = True

    # --- Adaptação da confiança (ITAL) ---
    # Alta suspeita -> queda forte de confiança
    if risk > 0.6:
        decay_I, decay_D = 0.2, 0.15
        new_I = max(0.0, I_u * (1 - decay_I))
        new_D = max(0.0, D_d * (1 - decay_D))
    else:
        # Baixo/médio risco -> recuperação lenta em direção a 0.95
        rec_I, rec_D = 0.05, 0.05
        new_I = min(0.95, I_u + rec_I * (0.95 - I_u))
        new_D = min(0.95, D_d + rec_D * (0.95 - D_d))

    state["I"][user["id"]] = new_I
    state["D"][device["id"]] = new_D

    # IMPORTANTÍSSIMO: esses campos são o que o compute_ital() usa
    return {
        "allowed": allowed,
        "action": action,
        "theta": theta,
        "risk": risk,
        "I_u": I_u,
        "D_d": D_d,
        "new_I": new_I,
        "new_D": new_D,
    }


def run_simulation(config):
    """
    Função principal da simulação.
    Lê parâmetros de config (num_events, attack_probability) e
    retorna dois vetores de logs: baseline e securebank.
    """
    random.seed(42)

    # Parâmetros vindos do JSON (com defaults)
    num_events = config.get("num_events", NUM_STEPS)
    attack_prob = config.get("attack_probability", ATTACK_PROB)

    users = generate_users()
    devices = generate_devices(users)

    # índice rápido: user_id -> lista de devices
    devices_by_owner = defaultdict(list)
    for d in devices:
        devices_by_owner[d["owner_id"]].append(d)

    baseline_logs = []
    securebank_logs = []

    # Estado interno do SecureBank™ (confiança por usuário/dispositivo)
    sb_state = {"I": {}, "D": {}}

    for _ in range(num_events):
        user = random.choice(users)
        user_devices = devices_by_owner[user["id"]]
        device = random.choice(user_devices)

        tx, ctx = generate_normal_transaction(user)

        # Decide se injeta ataque
        is_attack = random.random() < attack_prob
        scenario = None
        if is_attack:
            scenario = random.randint(1, 5)
            tx, ctx = inject_attack(tx, ctx, scenario)

        event = {
            "user": user,
            "device": device,
            "tx": tx,
            "ctx": ctx,
            "scenario": scenario,
            "is_attack": is_attack,
        }

        # --------- Baseline ---------
        base_decision = baseline_pdp(event)
        baseline_logs.append(
            {
                "user_id": user["id"],
                "device_id": device["id"],
                "is_attack": is_attack,
                "scenario": scenario,
                "allowed": base_decision["allowed"],
                "action": base_decision["action"],
                # se no futuro quisermos ITAL básico, dá pra adicionar I/D fixos aqui
            }
        )

        # --------- SecureBank ---------
        sb_decision = securebank_pdp(event, sb_state)
        securebank_logs.append(
            {
                "user_id": user["id"],
                "device_id": device["id"],
                "is_attack": is_attack,
                "scenario": scenario,
                "amount": tx["amount"],
                "geo": ctx["geo"],
                "hour": ctx["hour"],
                "channel": ctx["channel"],
                "service": tx["service"],
                # campos usados por TII/SAE/ITAL:
                **sb_decision,
            }
        )

    return baseline_logs, securebank_logs
