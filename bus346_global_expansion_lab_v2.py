import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="BUS 346 | Global Expansion Decision Lab",
    page_icon="🌍",
    layout="wide",
)

# =========================================================
# Styling
# =========================================================
st.markdown(
    """
    <style>
    .main-title {font-size: 2.45rem; font-weight: 800; margin-bottom: 0.15rem;}
    .subtitle {font-size: 1.08rem; color: #555; margin-bottom: 1.2rem;}
    .stage-card {
        padding: 1rem 1.05rem;
        border: 1px solid #e6e6e6;
        border-radius: 14px;
        background: #fafafa;
        min-height: 142px;
    }
    .small-muted {color:#666; font-size:0.92rem;}
    .decision-box {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        background: #f5f7fb;
        border: 1px solid #dfe5ef;
    }
    .formula-box {
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: #fff8e8;
        border: 1px solid #f1dfad;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Illustrative teaching data
# =========================================================
COUNTRIES = {
    "United Arab Emirates": {
        "trade": 88, "development": 89, "globalization": 92,
        "political": 82, "legal": 86, "culture": 65, "ethics": 83,
        "integration": 78, "fx": 82, "monetary": 85,
        "market": 83, "competition": 72, "local_partner": 78, "control_need": 70,
        "note": "High-income, globally connected hub with strong infrastructure and regional access."
    },
    "India": {
        "trade": 74, "development": 72, "globalization": 75,
        "political": 67, "legal": 63, "culture": 58, "ethics": 61,
        "integration": 66, "fx": 64, "monetary": 68,
        "market": 95, "competition": 84, "local_partner": 82, "control_need": 63,
        "note": "Very large growth market, but institutional, regional, and competitive complexity matter."
    },
    "Germany": {
        "trade": 91, "development": 95, "globalization": 89,
        "political": 91, "legal": 94, "culture": 72, "ethics": 91,
        "integration": 95, "fx": 88, "monetary": 90,
        "market": 80, "competition": 88, "local_partner": 64, "control_need": 78,
        "note": "Advanced, rules-based market with excellent integration but intense competition and high standards."
    },
    "Vietnam": {
        "trade": 90, "development": 70, "globalization": 81,
        "political": 72, "legal": 62, "culture": 61, "ethics": 63,
        "integration": 79, "fx": 67, "monetary": 70,
        "market": 82, "competition": 67, "local_partner": 84, "control_need": 61,
        "note": "Fast-growing manufacturing and consumer economy integrated into Asian supply chains."
    },
    "Brazil": {
        "trade": 61, "development": 71, "globalization": 67,
        "political": 58, "legal": 57, "culture": 63, "ethics": 59,
        "integration": 60, "fx": 55, "monetary": 58,
        "market": 88, "competition": 74, "local_partner": 79, "control_need": 60,
        "note": "Large consumer market with major upside, alongside regulatory and macroeconomic complexity."
    },
}

INDUSTRIES = {
    "Consumer Technology": {"scale": 85, "local_adaptation": 65, "capital": 55, "speed": 85},
    "Food & Beverage": {"scale": 72, "local_adaptation": 88, "capital": 62, "speed": 70},
    "Financial Services": {"scale": 76, "local_adaptation": 70, "capital": 75, "speed": 58},
    "Manufacturing": {"scale": 84, "local_adaptation": 48, "capital": 92, "speed": 45},
    "Professional Services": {"scale": 58, "local_adaptation": 75, "capital": 30, "speed": 88},
}

CHAPTER_MAP = {
    "M1 — Identify Opportunities": [
        "Ch. 1 — Globalization",
        "Ch. 3 — Economic Development",
        "Ch. 6 — International Trade Theory",
    ],
    "M2 — Assess Risk": [
        "Ch. 2 — Political, Economic & Legal Systems",
        "Ch. 4 — Culture",
        "Ch. 5 — Ethics, CSR & Sustainability",
        "Ch. 7 — Government Policy & International Trade",
        "Ch. 9 — Regional Economic Integration",
        "Ch. 10 — Foreign Exchange Market",
        "Ch. 11 — International Monetary System",
    ],
    "M3 — Evaluate the Investment Case": [
        "Ch. 8 — Foreign Direct Investment",
    ],
    "M4 — Decide How to Enter & Compete": [
        "Ch. 13 — Strategy of International Business",
        "Ch. 14 — Organization of International Business",
        "Ch. 15 — Entering Developed & Emerging Markets",
    ],
}

# =========================================================
# Helper functions
# =========================================================
def normalize_weights(*weights):
    total = sum(weights)
    if total == 0:
        return [1 / len(weights)] * len(weights)
    return [w / total for w in weights]


def opportunity_breakdown(country, wg, wd, wt):
    """Return weighted contributions that sum to the Opportunity Score."""
    d = COUNTRIES[country]
    g_contrib = d["globalization"] * wg
    d_contrib = d["development"] * wd
    t_contrib = d["trade"] * wt
    score = g_contrib + d_contrib + t_contrib
    return g_contrib, d_contrib, t_contrib, score


def risk_components(country, shock="None"):
    d = COUNTRIES[country]
    components = {
        "Political / legal": 100 - (d["political"] * 0.55 + d["legal"] * 0.45),
        "Culture": 100 - d["culture"],
        "Ethics / sustainability": 100 - d["ethics"],
        "Trade policy": 100 - d["trade"],
        "Regional integration": 100 - d["integration"],
        "Foreign exchange": 100 - d["fx"],
        "Monetary system": 100 - d["monetary"],
    }

    shock_text = "No additional shock applied."
    if shock == "25% tariff introduced":
        components["Trade policy"] = min(100, components["Trade policy"] + 30)
        shock_text = "A tariff shock raises landed cost and may strengthen the case for local production."
    elif shock == "Currency depreciates 15%":
        components["Foreign exchange"] = min(100, components["Foreign exchange"] + 32)
        shock_text = "FX depreciation affects pricing, repatriated profits, sourcing costs, and hedging needs."
    elif shock == "Political instability rises":
        components["Political / legal"] = min(100, components["Political / legal"] + 35)
        shock_text = "Institutional uncertainty increases the value of flexibility and staged commitment."
    elif shock == "Major cultural backlash":
        components["Culture"] = min(100, components["Culture"] + 35)
        shock_text = "Weak local legitimacy can turn a commercially attractive launch into a strategic failure."
    elif shock == "Regional integration deepens":
        components["Regional integration"] = max(0, components["Regional integration"] - 25)
        shock_text = "Deeper integration can reduce fragmentation and expand the effective market."

    return components, shock_text


def adjusted_risk_score(country, exposure, adaptability, shock="None"):
    components, shock_text = risk_components(country, shock)
    raw_risk = np.mean(list(components.values()))
    adjusted = np.clip(
        raw_risk * (0.65 + exposure / 200) * (1.15 - adaptability / 250),
        0,
        100,
    )
    return float(adjusted), components, shock_text


def fdi_score(opportunity, risk, local_presence, control_ip, capital_capacity, risk_tolerance, motive_bonus=0):
    """Heuristic teaching score: higher means a stronger case for high-commitment FDI."""
    score = (
        0.28 * opportunity
        + 0.18 * local_presence
        + 0.18 * control_ip
        + 0.18 * capital_capacity
        + 0.18 * risk_tolerance
        - 0.25 * risk
        + motive_bonus
    )
    return float(np.clip(score, 0, 100))


# =========================================================
# Header and mission
# =========================================================
st.markdown('<div class="main-title">🌍 BUS 346 — Global Expansion Decision Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">You are the international strategy team. Identify the opportunity, diagnose risk, decide how much capital to commit, and choose how to enter and compete.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Your Mission")
    company = st.text_input("Company", "NorthStar Global")
    industry = st.selectbox("Industry", list(INDUSTRIES.keys()))
    home = st.selectbox("Home market", ["Canada", "United States", "United Kingdom", "UAE", "Singapore"])
    selected = st.multiselect(
        "Candidate markets",
        list(COUNTRIES.keys()),
        default=["United Arab Emirates", "India", "Germany"],
    )
    st.caption("Demo scores are illustrative teaching inputs—not live country-risk estimates.")

if not selected:
    st.warning("Select at least one candidate market in the sidebar.")
    st.stop()

# =========================================================
# Course journey
# =========================================================
cols = st.columns(4)
with cols[0]:
    st.markdown(
        "<div class='stage-card'><b>M1 · IDENTIFY OPPORTUNITIES</b><br><span class='small-muted'>Where is the upside?</span><br><br>Globalization · Development · Trade</div>",
        unsafe_allow_html=True,
    )
with cols[1]:
    st.markdown(
        "<div class='stage-card'><b>M2 · ASSESS RISK</b><br><span class='small-muted'>What could go wrong?</span><br><br>Institutions · Culture · Policy · FX</div>",
        unsafe_allow_html=True,
    )
with cols[2]:
    st.markdown(
        "<div class='stage-card'><b>M3 · INVESTMENT CASE</b><br><span class='small-muted'>How much should we commit?</span><br><br>FDI · Control · Capital · Irreversibility</div>",
        unsafe_allow_html=True,
    )
with cols[3]:
    st.markdown(
        "<div class='stage-card'><b>M4 · ENTER & COMPETE</b><br><span class='small-muted'>How should we execute?</span><br><br>Strategy · Organization · Entry Mode</div>",
        unsafe_allow_html=True,
    )

st.divider()

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔎 M1 · Opportunity Radar",
    "⚠️ M2 · Risk Lab",
    "🏭 M3 · Investment / FDI",
    "🚪 M4 · Entry Strategy",
    "🏁 Boardroom Decision",
])

# =========================================================
# M1 — Opportunity Radar
# =========================================================
with tab1:
    st.subheader("M1: Identify the Opportunity")
    st.write(
        "Choose what matters to the firm. The app converts those priorities into normalized weights and shows each factor's live contribution to the final Opportunity Score."
    )

    a, b, c = st.columns(3)
    w_global_raw = a.slider("Global connectivity priority", 0, 100, 30, help="Ch. 1 — Globalization", key="w_global")
    w_dev_raw = b.slider("Economic development / purchasing power priority", 0, 100, 40, help="Ch. 3 — Economic Development", key="w_dev")
    w_trade_raw = c.slider("Trade advantage / openness priority", 0, 100, 30, help="Ch. 6 — International Trade Theory", key="w_trade")

    wg, wd, wt = normalize_weights(w_global_raw, w_dev_raw, w_trade_raw)

    m1a, m1b, m1c = st.columns(3)
    m1a.metric("Effective globalization weight", f"{wg:.0%}")
    m1b.metric("Effective development weight", f"{wd:.0%}")
    m1c.metric("Effective trade weight", f"{wt:.0%}")

    opp_rows = []
    for country in selected:
        g_contrib, d_contrib, t_contrib, score = opportunity_breakdown(country, wg, wd, wt)
        opp_rows.append([
            country,
            round(g_contrib, 1),
            round(d_contrib, 1),
            round(t_contrib, 1),
            round(score, 1),
            COUNTRIES[country]["note"],
        ])

    opp_df = pd.DataFrame(
        opp_rows,
        columns=[
            "Market",
            "Globalization contribution",
            "Development contribution",
            "Trade contribution",
            "Opportunity Score",
            "Interpretation",
        ],
    ).sort_values("Opportunity Score", ascending=False)

    st.dataframe(opp_df, use_container_width=True, hide_index=True)
    st.bar_chart(opp_df.set_index("Market")["Opportunity Score"])

    leader = opp_df.iloc[0]
    st.success(f"Current opportunity leader: **{leader['Market']}** ({leader['Opportunity Score']}/100).")

    with st.expander("See the fixed country evidence behind the weighted contributions"):
        raw_rows = []
        for country in selected:
            d = COUNTRIES[country]
            raw_rows.append([country, d["globalization"], d["development"], d["trade"]])
        raw_df = pd.DataFrame(raw_rows, columns=["Market", "Globalization base", "Development base", "Trade base"])
        st.dataframe(raw_df, use_container_width=True, hide_index=True)
        st.caption(
            "These base scores are fixed demo evidence. The main table above changes because your sliders change the weight placed on each factor."
        )

    st.info(
        "Class prompt: Is the highest-growth or highest-income market automatically the best opportunity? What does trade theory add that market size alone misses?"
    )

# =========================================================
# M2 — Risk Lab
# =========================================================
with tab2:
    st.subheader("M2: Assess Risk")
    st.write("Opportunity is not enough. Stress-test one market using the institutional and cross-border risks covered in the course.")

    risk_country = st.selectbox("Market to stress-test", selected, key="risk_country")

    c1, c2, c3 = st.columns(3)
    shock = c1.selectbox(
        "Scenario shock",
        [
            "None",
            "25% tariff introduced",
            "Currency depreciates 15%",
            "Political instability rises",
            "Major cultural backlash",
            "Regional integration deepens",
        ],
        key="risk_shock",
    )
    exposure = c2.slider("Your firm's exposure to this market", 0, 100, 65, key="risk_exposure")
    adaptability = c3.slider("Ability to adapt locally", 0, 100, 60, key="risk_adaptability")

    adjusted_risk, components, shock_text = adjusted_risk_score(risk_country, exposure, adaptability, shock)
    risk_df = pd.DataFrame({
        "Risk dimension": list(components.keys()),
        "Risk (0=low, 100=high)": [round(v, 1) for v in components.values()],
    })

    left, right = st.columns([1, 2])
    with left:
        st.metric("Adjusted Risk Score", f"{adjusted_risk:.1f}/100", help="Higher = riskier")
        if adjusted_risk < 30:
            st.success("Risk level: LOW")
        elif adjusted_risk < 55:
            st.warning("Risk level: MODERATE")
        else:
            st.error("Risk level: HIGH")
        st.caption(shock_text)
    with right:
        st.bar_chart(risk_df.set_index("Risk dimension"))

    st.info("Class prompt: Which risks should change the decision to enter, and which should merely change *how* the firm enters?")

# =========================================================
# M3 — Investment / FDI Decision
# =========================================================
with tab3:
    st.subheader("M3: Evaluate the Investment / FDI Case")
    st.write(
        "Now ask a different question: is the opportunity strong enough to justify committing capital inside the foreign market rather than remaining flexible?"
    )

    investment_country = st.selectbox("Target market for the investment case", selected, key="investment_country")
    d_inv = COUNTRIES[investment_country]

    g_c, d_c, t_c, investment_opp = opportunity_breakdown(investment_country, wg, wd, wt)
    investment_risk, _, _ = adjusted_risk_score(
        investment_country,
        exposure,
        adaptability,
        shock if investment_country == risk_country else "None",
    )

    motive = st.selectbox(
        "Primary FDI motive",
        ["Market-seeking", "Efficiency-seeking", "Strategic-asset-seeking", "Resource-seeking"],
        key="fdi_motive",
    )

    # Small motive-specific teaching adjustment using available demo evidence.
    if motive == "Market-seeking":
        motive_bonus = (d_inv["market"] - 70) * 0.10
    elif motive == "Efficiency-seeking":
        motive_bonus = (d_inv["trade"] - 70) * 0.10
    elif motive == "Strategic-asset-seeking":
        motive_bonus = ((d_inv["development"] + d_inv["globalization"]) / 2 - 70) * 0.10
    else:
        motive_bonus = 0

    f1, f2, f3, f4 = st.columns(4)
    local_presence = f1.slider(
        "Need for local presence",
        0, 100, 65,
        help="Do tariffs, logistics, service requirements, or customer proximity make local operations valuable?",
        key="fdi_local_presence",
    )
    control_ip = f2.slider(
        "Need for control / IP protection",
        0, 100, int(d_inv["control_need"]),
        help="How important is ownership control over technology, brand, quality, or know-how?",
        key="fdi_control_ip",
    )
    capital_capacity = f3.slider(
        "Capital capacity",
        0, 100, 60,
        help="How much financial capacity does the firm have for a higher-commitment investment?",
        key="fdi_capital",
    )
    risk_tolerance = f4.slider(
        "Tolerance for irreversible commitment",
        0, 100, 55,
        help="Higher values mean the firm is more willing to commit despite uncertainty.",
        key="fdi_risk_tolerance",
    )

    current_fdi_score = fdi_score(
        investment_opp,
        investment_risk,
        local_presence,
        control_ip,
        capital_capacity,
        risk_tolerance,
        motive_bonus,
    )

    x1, x2, x3 = st.columns(3)
    x1.metric("Opportunity", f"{investment_opp:.1f}/100")
    x2.metric("Risk", f"{investment_risk:.1f}/100")
    x3.metric("FDI Commitment Score", f"{current_fdi_score:.1f}/100")

    if current_fdi_score >= 65:
        st.success("Investment signal: **Strong case for evaluating high-commitment FDI.**")
        commitment_label = "High commitment / FDI is plausible"
    elif current_fdi_score >= 45:
        st.warning("Investment signal: **Consider staged commitment, a partner, or a joint venture before full ownership.**")
        commitment_label = "Staged or shared commitment"
    else:
        st.error("Investment signal: **Preserve flexibility; a lower-commitment approach may be more defensible.**")
        commitment_label = "Low commitment / preserve flexibility"

    st.markdown(
        """
        <div class='formula-box'>
        <b>Teaching interpretation:</b> the FDI score rewards opportunity, local-presence needs, control needs, capital capacity and risk tolerance, while penalizing market risk. It is a discussion heuristic—not an investment valuation model.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Class prompt: What would have to be true for a firm to prefer FDI over exporting? Which assumptions make the investment difficult to reverse?"
    )

# =========================================================
# M4 — Entry Strategy
# =========================================================
with tab4:
    st.subheader("M4: Decide How to Enter & Compete")
    st.write(
        f"Use the investment case to choose an execution model for **{investment_country}**. The M3 FDI Commitment Score is carried into the recommendation below."
    )

    d = COUNTRIES[investment_country]
    ind = INDUSTRIES[industry]

    c1, c2, c3, c4 = st.columns(4)
    desired_control = c1.slider("Desired control", 0, 100, int(d["control_need"]), key="entry_control")
    speed = c2.slider("Need for speed", 0, 100, ind["speed"], key="entry_speed")
    capital = c3.slider("Capital available", 0, 100, capital_capacity, key="entry_capital")
    local_knowledge = c4.slider("Need for local knowledge", 0, 100, int(d["local_partner"]), key="entry_local_knowledge")

    fdi_readiness = current_fdi_score

    modes = {
        "Exporting": (
            66 + speed * 0.18 - desired_control * 0.18 - local_knowledge * 0.08
            + (100 - capital) * 0.06 + (100 - fdi_readiness) * 0.12
        ),
        "Licensing / Franchising": (
            62 + speed * 0.14 - desired_control * 0.24 + local_knowledge * 0.10
            + (100 - capital) * 0.10 + (100 - fdi_readiness) * 0.05
        ),
        "Strategic Alliance": (
            56 + local_knowledge * 0.24 + speed * 0.10 + desired_control * 0.05
            + (100 - capital) * 0.05 + fdi_readiness * 0.04
        ),
        "Joint Venture": (
            48 + desired_control * 0.08 + local_knowledge * 0.28 + capital * 0.08
            - speed * 0.03 + fdi_readiness * 0.10
        ),
        "Wholly Owned Subsidiary / FDI": (
            30 + desired_control * 0.32 + capital * 0.20 - local_knowledge * 0.05
            - speed * 0.08 + fdi_readiness * 0.22
        ),
    }

    mode_df = pd.DataFrame({
        "Entry mode": list(modes.keys()),
        "Strategic fit": [round(float(np.clip(v, 0, 100)), 1) for v in modes.values()],
    }).sort_values("Strategic fit", ascending=False)

    best_mode = mode_df.iloc[0]["Entry mode"]
    best_fit = mode_df.iloc[0]["Strategic fit"]

    st.dataframe(mode_df, use_container_width=True, hide_index=True)
    st.bar_chart(mode_df.set_index("Entry mode"))
    st.success(f"Recommended entry mode: **{best_mode}** — fit score {best_fit:.1f}/100")

    if desired_control > 70 and capital < 45:
        st.warning("Strategic tension: you want high control but have limited capital. Defend the trade-off.")
    if local_knowledge > 75 and best_mode == "Wholly Owned Subsidiary / FDI":
        st.warning("Strategic tension: strong local-knowledge needs may make a local partner valuable even if control matters.")
    if current_fdi_score < 45 and best_mode == "Wholly Owned Subsidiary / FDI":
        st.warning("Strategic tension: M3 favors flexibility, but M4 is pointing toward full ownership. Explain why the firm should override the investment-stage warning.")

    st.info("Class prompt: Why might two firms entering the same country rationally choose different entry modes?")

# =========================================================
# Boardroom
# =========================================================
with tab5:
    st.subheader("Boardroom Decision")
    st.write("Pull the entire course together. The goal is not to maximize a score—it is to make a defensible decision.")

    rows = []
    for country in selected:
        _, _, _, opp = opportunity_breakdown(country, wg, wd, wt)
        country_shock = shock if country == risk_country else "None"
        rsk, _, _ = adjusted_risk_score(country, exposure, adaptability, country_shock)
        attractiveness = opp - 0.60 * rsk
        rows.append([country, round(opp, 1), round(rsk, 1), round(attractiveness, 1)])

    board = pd.DataFrame(
        rows,
        columns=["Market", "Opportunity", "Risk", "Risk-adjusted attractiveness"],
    ).sort_values("Risk-adjusted attractiveness", ascending=False)

    st.dataframe(board, use_container_width=True, hide_index=True)
    st.bar_chart(board.set_index("Market")["Risk-adjusted attractiveness"])

    winner = board.iloc[0]["Market"]
    st.markdown(
        f"""
        <div class='decision-box'>
        <b>Demo recommendation:</b><br><br>
        Prioritize <b>{winner}</b> for deeper due diligence based on the current M1 and M2 assumptions.<br><br>
        Your M3 target is <b>{investment_country}</b>, with an FDI Commitment Score of <b>{current_fdi_score:.1f}/100</b>
        ({commitment_label}). Your current M4 execution recommendation is <b>{best_mode}</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if winner != investment_country:
        st.warning(
            f"Decision tension: M1–M2 currently rank **{winner}** highest, but you are building the investment case for **{investment_country}**. That is not necessarily wrong—defend why."
        )

    st.markdown("### 60-second Board Pitch")
    st.text_area(
        "Student response",
        placeholder=(
            "We recommend entering ______ because... The most important opportunity is... "
            "The biggest risk is... We recommend a ______ commitment level and would enter through ______ because..."
        ),
        height=160,
        key="board_pitch",
    )

    st.markdown("### Decision Check")
    confidence = st.slider("How confident are you in your recommendation?", 0, 100, 70, key="board_confidence")
    uncertainty = st.selectbox(
        "What could most change your decision?",
        [
            "New political / legal information",
            "A major FX movement",
            "A tariff or trade-policy change",
            "Evidence of different consumer preferences",
            "A competitor's move",
            "A change in financing conditions",
        ],
        key="board_uncertainty",
    )
    st.caption(f"Confidence: {confidence}/100 · Key unresolved uncertainty: {uncertainty}")

# =========================================================
# Instructor / chapter mapping
# =========================================================
st.divider()

with st.expander("📚 How the app maps to the BUS 346 framework"):
    for stage, chapters in CHAPTER_MAP.items():
        st.markdown(f"**{stage}**")
        for ch in chapters:
            st.write("• " + ch)

with st.expander("👩‍🏫 Instructor mode: suggested classroom uses"):
    st.markdown(
        """
        **Before class:** assign each group a company/industry and 3 candidate countries.  
        **M1:** teams identify the strongest opportunity and explain their weighting choices.  
        **M2:** reveal a shock and require teams to revise their risk diagnosis.  
        **M3:** teams decide whether the evidence justifies a high-commitment FDI position or a staged approach.  
        **M4:** teams select and defend an entry mode and organizational approach.  
        **Final:** each team delivers the 60-second board pitch or submits a one-page board memo.  
        **Assessment twist:** award marks for reasoning, assumptions and consistency—not for choosing the app's top-ranked market.
        """
    )

st.caption("BUS 346 teaching demo · Illustrative scores only · Designed for discussion, not real investment advice")
