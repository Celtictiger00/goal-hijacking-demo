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


# --- Governance Enforcement ---
def enforce_policy(action: str):
    if action in policy["blocked_actions"]:
        return False, f"❌ BLOCKED: {action} is not permitted"

    if action not in policy["allowed_actions"]:
        return False, f"⚠️ UNKNOWN or unapproved action: {action}"

    return True, "✅ Action allowed"


# --- Logging ---
def log_event(event: dict):
    print("\n[🛡️ GOVERNANCE LOG]")
    for k, v in event.items():
        print(f"{k}: {v}")


# --- Agent Execution ---
def run_agent(user_input: str, original_goal: str = None):
    intent = classify_intent(user_input)

    # Detect goal drift (simple but powerful concept)
    drift_detected = original_goal and intent != original_goal

    allowed, decision = enforce_policy(intent)

    log_event({
        "user_input": user_input,
        "detected_intent": intent,
        "original_goal": original_goal,
        "goal_drift": drift_detected,
        "policy_decision": decision
    })

    if drift_detected:
        return "⚠️ Goal hijacking detected — intent deviates from original request."

    if not allowed:
        return "🚫 Execution blocked by governance policy."

    # Safe execution
    if intent == "book_flight":
        return TOOLS[intent]("London")

    if intent == "send_email":
        return TOOLS[intent]("admin@example.com", "Test message")

    if intent == "transfer_funds":
        return TOOLS

    return "No valid action executed."