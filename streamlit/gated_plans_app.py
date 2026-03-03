"""
GatedPlans Example - Feature Gating Demo
=========================================
Demonstrates how Native App pricing plans control feature access.
Three tiers: Standard (Bronze), Premium (Silver), Enterprise (Gold).
"""

import streamlit as st
import json
import time

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="GatedPlans Example", page_icon="🏆", layout="centered")

# ---------------------------------------------------------------------------
# CSS for cup icons and flash animation
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@keyframes flash {
    0%   { opacity: 1; transform: scale(1); }
    15%  { opacity: 0.3; transform: scale(1.15); }
    30%  { opacity: 1; transform: scale(1); }
    45%  { opacity: 0.3; transform: scale(1.15); }
    60%  { opacity: 1; transform: scale(1); }
    75%  { opacity: 0.3; transform: scale(1.15); }
    100% { opacity: 1; transform: scale(1); }
}

.cup-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 60px;
    margin: 30px 0 20px 0;
}

.cup-item {
    text-align: center;
}

.cup-icon {
    font-size: 80px;
    display: block;
    transition: all 0.3s ease;
}

.cup-icon.flashing {
    animation: flash 1.5s ease-in-out;
}

.cup-label {
    margin-top: 8px;
    font-weight: 600;
    font-size: 16px;
    color: #555;
}

.upgrade-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.upgrade-box h3 {
    margin: 0 0 8px 0;
    color: white;
}

.upgrade-box p {
    margin: 0;
    opacity: 0.9;
}

.success-box {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
}

.success-box h3 {
    margin: 0 0 8px 0;
    color: white;
}

.success-box p {
    margin: 0;
    opacity: 0.9;
}

.plan-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 16px;
}

.badge-standard  { background: #CD7F32; color: white; }
.badge-premium   { background: #C0C0C0; color: #333; }
.badge-enterprise { background: #FFD700; color: #333; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Plan detection
# ---------------------------------------------------------------------------
def get_active_plan_live():
    """Attempt to read the plan from Marketplace purchase attributes."""
    try:
        session = st.connection("snowflake").session()
        result = session.sql("SELECT SYSTEM$GET_PURCHASE_ATTRIBUTES()").collect()
        if result and result[0][0]:
            attrs = json.loads(result[0][0])
            plan = attrs.get("plan_name", "").upper()
            if plan in ("STANDARD", "PREMIUM", "ENTERPRISE"):
                return plan
    except Exception:
        pass
    return None


def get_active_plan():
    """Return the active plan. Uses live detection first, falls back to demo selector."""
    live = get_active_plan_live()
    if live:
        return live
    return st.session_state.get("demo_plan", "STANDARD")


# ---------------------------------------------------------------------------
# Plan entitlements
# ---------------------------------------------------------------------------
PLAN_ACCESS = {
    "STANDARD":   {"STANDARD"},
    "PREMIUM":    {"STANDARD", "PREMIUM"},
    "ENTERPRISE": {"STANDARD", "PREMIUM", "ENTERPRISE"},
}


def has_access(active_plan: str, required_plan: str) -> bool:
    return required_plan in PLAN_ACCESS.get(active_plan, set())


# ---------------------------------------------------------------------------
# Sidebar - Demo mode plan selector
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Demo Controls")
    st.caption("Simulates plan selection for demo purposes. "
               "In production, the plan is detected automatically via "
               "`SYSTEM$GET_PURCHASE_ATTRIBUTES()`.")

    demo_plan = st.radio(
        "Active Plan",
        ["STANDARD", "PREMIUM", "ENTERPRISE"],
        index=["STANDARD", "PREMIUM", "ENTERPRISE"].index(
            st.session_state.get("demo_plan", "STANDARD")
        ),
        key="demo_plan_radio",
    )
    st.session_state["demo_plan"] = demo_plan

    live_plan = get_active_plan_live()
    if live_plan:
        st.success(f"Live plan detected: **{live_plan}**")
    else:
        st.info("No live Marketplace plan detected. Using demo selector.")

    st.divider()
    st.markdown("#### How It Works")
    st.markdown("""
    1. Each button requires a specific plan tier
    2. The app checks the consumer's active plan
    3. If the plan covers the feature, the cup flashes
    4. If not, an upgrade prompt is shown
    """)

# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
active_plan = get_active_plan()

st.markdown("# 🏆 GatedPlans Example")
st.markdown("Demonstrates feature gating based on Marketplace pricing plans.")

# Show current plan badge
badge_class = f"badge-{active_plan.lower()}"
st.markdown(
    f'<div style="text-align:center;">'
    f'<span class="plan-badge {badge_class}">Current Plan: {active_plan}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cup display
# ---------------------------------------------------------------------------
flash_target = st.session_state.get("flash_target", None)

bronze_class = "cup-icon flashing" if flash_target == "STANDARD" else "cup-icon"
silver_class = "cup-icon flashing" if flash_target == "PREMIUM" else "cup-icon"
gold_class   = "cup-icon flashing" if flash_target == "ENTERPRISE" else "cup-icon"

st.markdown(f"""
<div class="cup-container">
    <div class="cup-item">
        <span class="{bronze_class}">🥉</span>
        <div class="cup-label">Bronze</div>
    </div>
    <div class="cup-item">
        <span class="{silver_class}">🥈</span>
        <div class="cup-label">Silver</div>
    </div>
    <div class="cup-item">
        <span class="{gold_class}">🥇</span>
        <div class="cup-label">Gold</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Clear flash after render so it only shows once per click
if flash_target:
    st.session_state["flash_target"] = None

# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⚡ Standard", use_container_width=True):
        if has_access(active_plan, "STANDARD"):
            st.session_state["flash_target"] = "STANDARD"
            st.session_state["last_action"] = ("success", "STANDARD")
            st.rerun()
        else:
            st.session_state["last_action"] = ("upgrade", "STANDARD")
            st.rerun()

with col2:
    if st.button("⚡ Premium", use_container_width=True):
        if has_access(active_plan, "PREMIUM"):
            st.session_state["flash_target"] = "PREMIUM"
            st.session_state["last_action"] = ("success", "PREMIUM")
            st.rerun()
        else:
            st.session_state["last_action"] = ("upgrade", "PREMIUM")
            st.rerun()

with col3:
    if st.button("⚡ Enterprise", use_container_width=True):
        if has_access(active_plan, "ENTERPRISE"):
            st.session_state["flash_target"] = "ENTERPRISE"
            st.session_state["last_action"] = ("success", "ENTERPRISE")
            st.rerun()
        else:
            st.session_state["last_action"] = ("upgrade", "ENTERPRISE")
            st.rerun()

# ---------------------------------------------------------------------------
# Action feedback
# ---------------------------------------------------------------------------
last_action = st.session_state.get("last_action")
if last_action:
    action_type, target_plan = last_action
    st.session_state["last_action"] = None

    if action_type == "success":
        cup_name = {"STANDARD": "Bronze 🥉", "PREMIUM": "Silver 🥈", "ENTERPRISE": "Gold 🥇"}[target_plan]
        st.markdown(
            f'<div class="success-box">'
            f'<h3>Feature Activated!</h3>'
            f'<p>Your <b>{active_plan}</b> plan includes access to the <b>{cup_name}</b> cup.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif action_type == "upgrade":
        st.markdown(
            f'<div class="upgrade-box">'
            f'<h3>Upgrade Required</h3>'
            f'<p>The <b>{target_plan}</b> feature requires a <b>{target_plan}</b> plan or higher. '
            f'You are currently on the <b>{active_plan}</b> plan.</p>'
            f'<p style="margin-top:12px;">Contact your Snowflake account team or visit the '
            f'Marketplace listing to upgrade.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "This app demonstrates feature gating using `SYSTEM$GET_PURCHASE_ATTRIBUTES()`. "
    "In production, the plan is read from the Marketplace purchase. "
    "The sidebar demo selector simulates different plans for testing."
)
