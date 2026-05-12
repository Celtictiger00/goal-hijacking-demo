import yaml
from agent.tools import (
    book_flight,
    cancel_all_flights,
    transfer_funds,
    send_email
)

# Load governance policy
with open("agent/governance_policy.yaml", "r") as f:
    policy = yaml.safe_load(f)

TOOLS = {
    "book_flight": book_flight,
    "cancel_all_flights": cancel_all_flights,
    "transfer_funds": transfer_funds,
    "send_email": send_email
}


# --- Intent Classification ---
def classify_intent(user_input: str):
    text = user_input.lower()

    if "book" in text and "flight" in text:
        return "book_flight"
    if "cancel" in text:
        return "cancel_all_flights"
    if "transfer" in text or "send money" in text:
        return "transfer_funds"
    if "email" in text:
        return "send_email"

    return "unknown"


# --- Risk Level Check ---
def get_risk_level(action: str):
    return policy["risk_levels"].get(action, "unknown")


# --- Governance Enforcement ---
def enforce_policy(action: str):
    risk_level = get_risk_level(action)

    if action in policy["blocked_actions"]:
        return False, f"❌ BLOCKED: {action} is not permitted", risk_level

    if action not in policy["allowed_actions"]:
        return False, f"⚠️ UNKNOWN or unapproved action: {action}", risk_level

    return True, "✅ Action allowed", risk_level


# --- Graduated Risk Response ---
def apply_risk_response(action: str, risk_level: str):
    if risk_level == "low":
        return "permitted", "✅ Low risk — action permitted and logged"

    if risk_level == "medium":
        return "warning", "⚠️ Medium risk — action permitted with warning. Review recommended"

    if risk_level == "high":
        return "escalate", "🔶 High risk — human confirmation required before execution"

    if risk_level == "critical":
        return "block", "🚨 Critical risk — action blocked and escalated to risk owner"

    return "block", "❌ Unknown risk level — action blocked by default"


# --- EU AI Act Control Mapping ---
def get_control_mapping(action: str):
    triggered_rules = []
    for rule in policy["rules"]:
        triggered_rules.append({
            "rule": rule["name"],
            "eu_ai_act_ref": rule["eu_ai_act_ref"],
            "control_owner": rule["control_owner"]
        })
    return triggered_rules


# --- Logging ---
def log_event(event: dict):
    print("\n[🛡️ GOVERNANCE LOG]")
    for k, v in event.items():
        if isinstance(v, list):
            print(f"  {k}:")
            for item in v:
                print(f"    → {item}")
        else:
            print(f"  {k}: {v}")


# --- Agent Execution ---
def run_agent(user_input: str, original_goal: str = None):
    intent = classify_intent(user_input)
    drift_detected = original_goal and intent != original_goal
    allowed, decision, risk_level = enforce_policy(intent)
    risk_status, risk_message = apply_risk_response(intent, risk_level)
    control_mapping = get_control_mapping(intent)

    log_event({
        "user_input": user_input,
        "detected_intent": intent,
        "original_goal": original_goal,
        "goal_drift": drift_detected,
        "risk_level": risk_level,
        "risk_response": risk_message,
        "eu_ai_act_controls": control_mapping,
        "policy_decision": decision
    })

    if drift_detected:
        return "⚠️ Goal hijacking detected — intent deviates from original request."

    if risk_status == "block":
        return "🚨 Execution blocked — critical or unknown risk. Escalated to risk owner."

    if risk_status == "escalate":
        return "🔶 Execution paused — high risk action requires human confirmation."

    if risk_status == "warning":
        print("⚠️ Warning issued — medium risk action proceeding with log.")

    if not allowed:
        return "🚫 Execution blocked by governance policy."

    if intent == "book_flight":
        return TOOLS[intent]("London")

    if intent == "send_email":
        return TOOLS[intent]("admin@example.com", "Test message")

    return "No valid action executed."