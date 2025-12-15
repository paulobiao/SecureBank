# nist_zta_pdp.py
"""
NIST Zero Trust Architecture (ZTA) PDP Implementation

Baseado em NIST SP 800-207: Zero Trust Architecture
Implementa os 7 princípios fundamentais:
1. Continuous Verification
2. Least Privilege Access  
3. Assume Breach
4. Inspect and Log All Traffic
5. Use Multiple Sources of Data
6. Dynamic Policy Enforcement
7. Secure All Resources

Este PDP serve como baseline mais sofisticado que as regras estáticas,
mas menos contextualmente aware que o SecureBank™.
"""

import random
from collections import defaultdict


class NISTZeroTrustPDP:
    """
    Policy Decision Point baseado em NIST ZTA.
    
    Implementa verificação contínua com:
    - Multi-factor authentication simulation
    - Device posture checking
    - Network segmentation básica
    - Session monitoring
    - Risk-based access control
    """
    
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Parâmetros de configuração
        self.mfa_threshold = config.get("mfa_threshold", 0.6)
        self.device_trust_decay = config.get("device_trust_decay", 0.05)
        self.session_timeout = config.get("session_timeout", 100)  # eventos
        self.assume_breach_mode = config.get("assume_breach_mode", True)
        
        # Estado interno (princípio 1: continuous verification)
        self.device_posture = {}  # device_id -> posture_score [0,1]
        self.user_sessions = {}   # user_id -> {start_event: int, mfa_verified: bool}
        self.access_history = defaultdict(list)  # user_id -> [service_names]
        self.event_count = 0
        
        # Network segmentation (princípio 4: micro-perimeters)
        self.service_zones = {
            "payments": "dmz",
            "settlement": "restricted",
            "risk_analytics": "internal",
            "aml": "restricted",
            "customer_identity": "dmz",
        }
        
        # Least privilege matrix (princípio 2)
        self.role_permissions = {
            "customer": ["payments", "customer_identity"],
            "employee": ["payments", "settlement", "risk_analytics", "aml", "customer_identity"],
        }
    
    def evaluate(self, event):
        """
        Princípio 6: Dynamic Policy Enforcement
        
        Avalia evento usando múltiplas fontes de dados (princípio 5):
        - Identity (user type, MFA status)
        - Device (posture, trust level)
        - Network context (geo, channel)
        - Behavioral (access patterns)
        - Transactional (amount, service)
        """
        user = event["user"]
        device = event["device"]
        tx = event["tx"]
        ctx = event["ctx"]
        
        self.event_count += 1
        user_id = user["id"]
        device_id = device["id"]
        
        # ================================================================
        # Princípio 1: CONTINUOUS VERIFICATION
        # ================================================================
        
        # 1.1 Session validation
        session = self.user_sessions.get(user_id)
        if session is None:
            # Nova sessão - requer MFA
            mfa_verified = self._simulate_mfa(user, ctx)
            self.user_sessions[user_id] = {
                "start_event": self.event_count,
                "mfa_verified": mfa_verified,
                "last_event": self.event_count,
            }
            if not mfa_verified:
                return {
                    "allowed": False,
                    "action": "step_up",
                    "reason": "MFA_REQUIRED",
                    "nist_principle": "continuous_verification",
                }
        else:
            # Verifica timeout de sessão
            events_since_start = self.event_count - session["start_event"]
            if events_since_start > self.session_timeout:
                # Sessão expirada - nova MFA
                mfa_verified = self._simulate_mfa(user, ctx)
                self.user_sessions[user_id] = {
                    "start_event": self.event_count,
                    "mfa_verified": mfa_verified,
                    "last_event": self.event_count,
                }
                if not mfa_verified:
                    return {
                        "allowed": False,
                        "action": "step_up",
                        "reason": "SESSION_EXPIRED",
                        "nist_principle": "continuous_verification",
                    }
            else:
                session["last_event"] = self.event_count
        
        # 1.2 Device posture checking
        device_score = self._check_device_posture(device_id, ctx)
        if device_score < 0.4:
            return {
                "allowed": False,
                "action": "block",
                "reason": "DEVICE_POSTURE_FAILED",
                "nist_principle": "continuous_verification",
                "device_score": device_score,
            }
        
        # ================================================================
        # Princípio 2: LEAST PRIVILEGE ACCESS
        # ================================================================
        user_type = user.get("type", "customer")
        allowed_services = self.role_permissions.get(user_type, [])
        
        if tx["service"] not in allowed_services:
            return {
                "allowed": False,
                "action": "block",
                "reason": "INSUFFICIENT_PRIVILEGES",
                "nist_principle": "least_privilege",
                "required_role": "employee" if tx["service"] in ["settlement", "aml"] else "customer",
            }
        
        # ================================================================
        # Princípio 3: ASSUME BREACH
        # ================================================================
        # Sempre assume que a rede pode estar comprometida
        # Aumenta scrutiny em atividades suspeitas
        
        risk_score = 0.0
        risk_factors = []
        
        # 3.1 Anomalias geográficas (podem indicar credential theft)
        if ctx["geo"] not in ["US-FL", "US-NY", "US-CA", "BR-SP"]:
            risk_score += 0.35
            risk_factors.append("ANOMALOUS_GEO")
        
        # 3.2 Valores atípicos (podem indicar exfiltração)
        if tx["amount"] > 10000:
            risk_score += 0.25
            risk_factors.append("HIGH_VALUE")
        
        # 3.3 Horário atípico (pode indicar comprometimento)
        if ctx["hour"] < 6 or ctx["hour"] > 22:
            risk_score += 0.20
            risk_factors.append("OFF_HOURS")
        
        # 3.4 API abuse detection
        if ctx["channel"] == "api":
            # APIs são vetores comuns de ataque
            risk_score += 0.15
            risk_factors.append("API_ACCESS")
        
        # ================================================================
        # Princípio 4: INSPECT AND LOG ALL TRAFFIC
        # ================================================================
        # Network segmentation enforcement
        service_zone = self.service_zones.get(tx["service"], "internal")
        
        if service_zone == "restricted":
            # Zonas restritas requerem verificação adicional
            if tx["amount"] > 5000:
                risk_score += 0.20
                risk_factors.append("RESTRICTED_ZONE_HIGH_VALUE")
        
        # ================================================================
        # Princípio 5: USE MULTIPLE SOURCES OF DATA
        # ================================================================
        
        # 5.1 Behavioral analysis - acesso histórico
        self.access_history[user_id].append(tx["service"])
        recent_access = self.access_history[user_id][-20:]  # últimos 20 acessos
        
        # Detecta lateral movement (mudança súbita de padrão)
        if len(recent_access) >= 5:
            recent_services = set(recent_access[-5:])
            if len(recent_services) >= 4:  # muitos serviços diferentes rapidamente
                risk_score += 0.25
                risk_factors.append("LATERAL_MOVEMENT_PATTERN")
        
        # 5.2 Device trust deterioration (assume breach)
        if self.assume_breach_mode:
            # Em assume breach, device trust decai continuamente
            self.device_posture[device_id] = max(0.3, device_score * (1 - self.device_trust_decay))
        
        # ================================================================
        # Princípio 6: DYNAMIC POLICY ENFORCEMENT
        # ================================================================
        
        # Decisão baseada em risk_score agregado
        if risk_score >= 0.7:
            action = "block"
            allowed = False
            reason = "HIGH_RISK_SCORE"
        elif risk_score >= 0.4:
            action = "step_up"
            allowed = False
            reason = "MEDIUM_RISK_SCORE"
        else:
            action = "allow"
            allowed = True
            reason = "LOW_RISK_SCORE"
        
        return {
            "allowed": allowed,
            "action": action,
            "reason": reason,
            "nist_principle": "dynamic_enforcement",
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "device_score": device_score,
            "service_zone": service_zone,
        }
    
    def _simulate_mfa(self, user, ctx):
        """
        Simula verificação MFA.
        
        Fatores considerados:
        - Tipo de usuário (employees têm MFA mais robusto)
        - Contexto geográfico (locais conhecidos têm maior taxa de sucesso)
        - Canal (mobile/web mais confiáveis que API)
        """
        base_success = 0.95
        
        # Employees têm MFA mais robusto
        if user.get("type") == "employee":
            base_success = 0.98
        
        # Geolocalização suspeita reduz confiança em MFA
        if ctx["geo"] not in ["US-FL", "US-NY", "US-CA", "BR-SP"]:
            base_success *= 0.7
        
        # APIs têm menor confiança (podem ser automated)
        if ctx["channel"] == "api":
            base_success *= 0.85
        
        # Simula falha de MFA para ataques
        return random.random() < base_success
    
    def _check_device_posture(self, device_id, ctx):
        """
        Verifica postura do dispositivo.
        
        Considera:
        - Histórico do dispositivo
        - Contexto de acesso (geo, channel)
        - Estado de segurança (simulado)
        """
        if device_id not in self.device_posture:
            # Novo dispositivo - postura inicial baseada em contexto
            initial_score = 0.8
            
            # Geo suspeita reduz score inicial
            if ctx["geo"] not in ["US-FL", "US-NY", "US-CA", "BR-SP"]:
                initial_score *= 0.7
            
            # API access é menos confiável
            if ctx["channel"] == "api":
                initial_score *= 0.85
            
            self.device_posture[device_id] = initial_score
        
        return self.device_posture[device_id]


def nist_zta_pdp(event, state, config=None):
    """
    Wrapper function compatível com a interface do simulator.py
    
    Args:
        event: evento de transação
        state: estado persistente (contém a instância do PDP)
        config: configuração opcional
    
    Returns:
        dict com decisão e metadados NIST ZTA
    """
    if "nist_pdp" not in state:
        state["nist_pdp"] = NISTZeroTrustPDP(config)
    
    pdp = state["nist_pdp"]
    decision = pdp.evaluate(event)
    
    return decision
