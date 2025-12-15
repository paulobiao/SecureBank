# simulator.py
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
    """
    Gera população sintética de usuários com base_risk diferente
    para customers e employees.
    """
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
    """
    Gera uma transação "normal" para um usuário,
    com valores log-normais e contexto simples (geo, hour, channel).
    """
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
    """
    Injeta diferentes cenários de ataque sobre uma transação original.
    Compatível com os cenários descritos no artigo:
    - credential compromise
    - insider lateral movement
    - API abuse
    - money laundering
    - session hijacking
    """
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
    PDP tradicional: regras simples e estáticas.
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


def securebank_pdp(event, state, ital_params=None):
    """
    SecureBank PDP (Modo B - equilíbrio entre segurança e usabilidade)

    Objetivos desta calibração:
    - Aumentar SAE de forma consistente em relação ao baseline;
    - Manter TII em faixa aceitável (poucos falsos positivos);
    - Preservar o comportamento adaptativo do ITAL.
    """

    user = event["user"]
    device = event["device"]
    tx = event["tx"]
    ctx = event["ctx"]

    if ital_params is None:
        ital_params = {}

    # Parâmetros de adaptação (podem ser afinados via config.json)
    trust_decay = ital_params.get("trust_decay", 0.12)
    trust_growth = ital_params.get("trust_growth", 0.20)
    identity_drift_factor = ital_params.get("identity_drift_factor", 0.30)

    # Confiança atual de identidade / dispositivo
    I_u = state["I"].get(user["id"], 0.9)
    D_d = state["D"].get(device["id"], 0.9)

    amount = tx["amount"]
    user_base_risk = user.get("base_risk", 0.2)

    risk = 0.0

    # ------------------------------------------------------------------
    # 1) Risco por valor (amount) - mais suave
    # ------------------------------------------------------------------
    if amount > 3_000:
        risk += 0.15
    if amount > 7_500:
        risk += 0.15
    if amount > 15_000:
        risk += 0.20
    if amount > 40_000:
        risk += 0.20

    # ------------------------------------------------------------------
    # 2) Risco geográfico (peso reduzido)
    # ------------------------------------------------------------------
    if ctx["geo"] not in ["US-FL", "US-NY", "US-CA", "BR-SP"]:
        risk += 0.25

    # ------------------------------------------------------------------
    # 3) Horário atípico
    # ------------------------------------------------------------------
    if ctx["hour"] < 6 or ctx["hour"] > 22:
        risk += 0.20

    # ------------------------------------------------------------------
    # 4) Canal / serviço (API com peso reduzido)
    # ------------------------------------------------------------------
    if ctx["channel"] == "api":
        risk += 0.15

    if tx["service"] in ["settlement", "aml"] and amount > 5_000:
        risk += 0.30

    # ------------------------------------------------------------------
    # 5) Identity drift (perfil de gasto do usuário)
    # ------------------------------------------------------------------
    profiles = state.setdefault("profiles", {})
    prof = profiles.get(user["id"])
    drift_risk = 0.0

    if prof is None:
        # inicializa perfil
        profiles[user["id"]] = {"avg_amount": amount, "count": 1}
    else:
        avg_amt = prof["avg_amount"]
        denom = max(avg_amt, 1e-6)
        drift_ratio = abs(amount - avg_amt) / denom

        drift_risk = min(1.0, drift_ratio * identity_drift_factor)
        risk += drift_risk

        new_count = prof["count"] + 1
        new_avg = prof["avg_amount"] + (amount - prof["avg_amount"]) / new_count
        profiles[user["id"]] = {"avg_amount": new_avg, "count": new_count}

    # ------------------------------------------------------------------
    # 6) Componente de risco intrínseco do usuário
    # ------------------------------------------------------------------
    risk += 0.20 * user_base_risk

    # Clamp de segurança
    risk = max(0.0, min(1.0, risk))

    # ------------------------------------------------------------------
    # TRUST + DECISÃO
    # ------------------------------------------------------------------
    base_trust = 0.5 * I_u + 0.5 * D_d

    # Penalização mais suave do que na versão "hard"
    theta = base_trust - 0.30 * risk
    theta = max(0.0, min(1.0, theta))

    # Thresholds de equilíbrio:
    # - abaixo de 0.20: risco muito alto -> bloqueia
    # - entre 0.20 e 0.55: risco intermediário -> step_up
    # - acima de 0.55: permite
    if theta < 0.20:
        action = "block"
        allowed = False
    elif theta < 0.55:
        action = "step_up"
        allowed = False
    else:
        action = "allow"
        allowed = True

    # ------------------------------------------------------------------
    # ITAL: atualização da confiança
    # ------------------------------------------------------------------
    if risk > 0.55:
        # eventos realmente suspeitos -> queda de confiança
        new_I = max(0.0, I_u * (1 - trust_decay))
        new_D = max(0.0, D_d * (1 - trust_decay * 0.8))
    else:
        # eventos normais -> recuperação gradual até ~0.95
        target = 0.95
        new_I = min(target, I_u + trust_growth * (target - I_u))
        new_D = min(target, D_d + trust_growth * (target - D_d))

    state["I"][user["id"]] = new_I
    state["D"][device["id"]] = new_D

    return {
        "allowed": allowed,
        "action": action,
        "theta": theta,
        "risk": risk,
        "I_u": I_u,
        "D_d": D_d,
        "new_I": new_I,
        "new_D": new_D,
        "drift_risk": drift_risk,
        "base_risk_component": 0.20 * user_base_risk,
    }


def run_simulation(config):
    """
    Função principal da simulação.
    Lê parâmetros de config (num_events, attack_probability, seed, scenarios)
    e retorna dois vetores de logs: baseline e securebank.
    """
    # Seed para reprodutibilidade científica
    seed = config.get("seed", 42)
    random.seed(seed)

    # Parâmetros vindos do JSON (com defaults)
    num_events = config.get("num_events", NUM_STEPS)
    attack_prob = config.get("attack_probability", ATTACK_PROB)

    ital_params = config.get("ital_params", {})
    scenarios_cfg = config.get("scenarios", {})

    # mapeia cenários do JSON para IDs internos
    scenario_flags = {
        1: scenarios_cfg.get("enable_credential_compromise", True),
        2: scenarios_cfg.get("enable_insider_movement", True),
        3: scenarios_cfg.get("enable_api_abuse", True),
        4: scenarios_cfg.get("enable_money_laundering", True),
        5: scenarios_cfg.get("enable_session_hijacking", True),
    }
    active_scenarios = [sid for sid, enabled in scenario_flags.items() if enabled]

    users = generate_users()
    devices = generate_devices(users)

    # índice rápido: user_id -> lista de devices
    devices_by_owner = defaultdict(list)
    for d in devices:
        devices_by_owner[d["owner_id"]].append(d)

    baseline_logs = []
    securebank_logs = []

    # Estado interno do SecureBank™ (confiança + perfil de identidade)
    sb_state = {"I": {}, "D": {}, "profiles": {}}

    for _ in range(num_events):
        user = random.choice(users)
        user_devices = devices_by_owner[user["id"]]
        device = random.choice(user_devices)

        tx, ctx = generate_normal_transaction(user)

        # Decide se injeta ataque
        is_attack = False
        scenario = None

        if active_scenarios and random.random() < attack_prob:
            is_attack = True
            scenario = random.choice(active_scenarios)
            tx, ctx = inject_attack(tx, ctx, scenario)

        event = {
            "user": user,
            "device": device,
            "tx": tx,
            "ctx": ctx,
            "scenario": scenario,
            "is_attack": is_attack,
        }

        # Baseline
        base_decision = baseline_pdp(event)
        baseline_logs.append({**event, **base_decision})

        # SecureBank
        sb_decision = securebank_pdp(event, sb_state, ital_params)
        securebank_logs.append({**event, **sb_decision})

    return baseline_logs, securebank_logs


def run_simulation_with_pdp(config, pdp_func, pdp_state=None):
    """
    Executa simulação com um PDP customizado.
    
    Args:
        config: configuração da simulação
        pdp_func: função PDP (event, state, config) -> decision
        pdp_state: estado inicial do PDP (opcional)
    
    Returns:
        logs da simulação
    """
    # Seed para reprodutibilidade científica
    seed = config.get("seed", 42)
    random.seed(seed)

    # Parâmetros vindos do JSON (com defaults)
    num_events = config.get("num_events", NUM_STEPS)
    attack_prob = config.get("attack_probability", ATTACK_PROB)

    ital_params = config.get("ital_params", {})
    scenarios_cfg = config.get("scenarios", {})

    # mapeia cenários do JSON para IDs internos
    scenario_flags = {
        1: scenarios_cfg.get("enable_credential_compromise", True),
        2: scenarios_cfg.get("enable_insider_movement", True),
        3: scenarios_cfg.get("enable_api_abuse", True),
        4: scenarios_cfg.get("enable_money_laundering", True),
        5: scenarios_cfg.get("enable_session_hijacking", True),
    }
    active_scenarios = [sid for sid, enabled in scenario_flags.items() if enabled]

    users = generate_users()
    devices = generate_devices(users)

    # índice rápido: user_id -> lista de devices
    devices_by_owner = defaultdict(list)
    for d in devices:
        devices_by_owner[d["owner_id"]].append(d)

    logs = []

    # Estado interno do PDP
    if pdp_state is None:
        pdp_state = {}

    for _ in range(num_events):
        user = random.choice(users)
        user_devices = devices_by_owner[user["id"]]
        device = random.choice(user_devices)

        tx, ctx = generate_normal_transaction(user)

        # Decide se injeta ataque
        is_attack = False
        scenario = None

        if active_scenarios and random.random() < attack_prob:
            is_attack = True
            scenario = random.choice(active_scenarios)
            tx, ctx = inject_attack(tx, ctx, scenario)

        event = {
            "user": user,
            "device": device,
            "tx": tx,
            "ctx": ctx,
            "scenario": scenario,
            "is_attack": is_attack,
        }

        # PDP customizado
        decision = pdp_func(event, pdp_state, ital_params)
        logs.append({**event, **decision})

    return logs
