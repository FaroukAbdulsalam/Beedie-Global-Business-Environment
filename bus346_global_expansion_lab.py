import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="BUS 346 | Global Expansion Decision Lab", page_icon="🌍", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {font-size: 2.45rem; font-weight: 800; margin-bottom: 0.15rem;}
    .subtitle {font-size: 1.08rem; color: #555; margin-bottom: 1.2rem;}
    .stage-card {padding: 1rem 1.1rem; border: 1px solid #e6e6e6; border-radius: 14px; background: #fafafa;}
    .big-score {font-size: 2.25rem; font-weight: 800;}
    .small-muted {color:#666; font-size:0.92rem;}
    .decision-box {padding: 1rem 1.2rem; border-radius: 14px; background: #f5f7fb; border: 1px solid #dfe5ef;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Demo data
# -----------------------------
COUNTRIES = {
    "United Arab Emirates": {
        "opportunity": 84, "risk": 24, "trade": 88, "development": 89, "globalization": 92,
        "political": 82, "legal": 86, "culture": 65, "ethics": 83, "integration": 78, "fx": 82, "monetary": 85,
        "market": 83, "competition": 72, "local_partner": 78, "control_need": 70,
        "note": "High-income, globally connected hub with strong infrastructure and regional access."
    },
    "India": {
        "opportunity": 91, "risk": 47, "trade": 74, "development": 72, "globalization": 75,
        "political": 67, "legal": 63, "culture": 58, "ethics": 61, "integration": 66, "fx": 64, "monetary": 68,
        "market": 95, "competition": 84, "local_partner": 82, "control_need": 63,
        "note": "Very large growth market, but institutional, regional, and competitive complexity matter."
    },
    "Germany": {
        "opportunity": 78, "risk": 18, "trade": 91, "development": 95, "globalization": 89,
        "political": 91, "legal": 94, "culture": 72, "ethics": 91, "integration": 95, "fx": 88, "monetary": 90,
        "market": 80, "competition": 88, "local_partner": 64, "control_need": 78,
        "note": "Advanced, rules-based market with excellent integration but intense competition and high standards."
    },
    "Vietnam": {
        "opportunity": 86, "risk": 39, "trade": 90, "development": 70, "globalization": 81,
        "political": 72, "legal": 62, "culture": 61, "ethics": 63, "integration": 79, "fx": 67, "monetary": 70,
        "market": 82, "competition": 67, "local_partner": 84, "control_need": 61,
        "note": "Fast-growing manufacturing and consumer economy integrated into Asian supply chains."
    },
    "Brazil": {
        "opportunity": 82, "risk": 52, "trade": 61, "development": 71, "globalization": 67,
        "political": 58, "legal": 57, "culture": 63, "ethics": 59, "integration": 60, "fx": 55, "monetary": 58,
        "market": 88, "competition": 74, "local_partner": 79, "control_need": 60,
        "note": "Large consumer market with major upside, alongside regulatory and macroeconomic complexity."
    }
}

INDUSTRIES = {
    "Consumer Technology": {"scale": 85, "local_adaptation": 65, "capital": 55, "speed": 85},
    "Food & Beverage": {"scale": 72, "local_adaptation": 88, "capital": 62, "speed": 70},
    "Financial Services": {"scale": 76, "local_adaptation": 70, "capital": 75, "speed": 58},
    "Manufacturing": {"scale": 84, "local_adaptation": 48, "capital": 92, "speed": 45},
    "Professional Services": {"scale": 58, "local_adaptation": 75, "capital": 30, "speed": 88},
}

CHAPTER_MAP = {
    "Opportunity": [
        "Ch. 1 — Globalization", "Ch. 3 — Economic Development", "Ch. 6 — International Trade Theory"
    ],
    "Risk": [
        "Ch. 2 — Political, Economic & Legal Systems", "Ch. 4 — Culture", "Ch. 5 — Ethics, CSR & Sustainability",
        "Ch. 7 — Government Policy & International Trade", "Ch. 9 — Regional Economic Integration",
        "Ch. 10 — Foreign Exchange Market", "Ch. 11 — International Monetary System"
    ],
    "Decision": [
        "Ch. 8 — Foreign Direct Investment", "Ch. 13 — Strategy of International Business",
        "Ch. 14 — Organization of International Business", "Ch. 15 — Entering Developed & Emerging Markets"
    ]
}

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="main-title">🌍 BUS 346 — Global Expansion Decision Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">You are the international strategy team. Your job: identify an attractive market, diagnose its risks, and recommend an entry strategy.</div>',
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
        default=["United Arab Emirates", "India", "Germany"]
    )
    st.caption("Demo data are illustrative for teaching—not live country-risk estimates.")

if not selected:
    st.warning("Select at least one candidate market in the sidebar.")
    st.stop()

# -----------------------------
# Course journey
# -----------------------------
cols = st.columns(3)
with cols[0]:
    st.markdown("<div class='stage-card'><b>1 · IDENTIFY OPPORTUNITIES</b><br><span class='small-muted'>Where is the upside?</span><br><br>Globalization · Development · Trade</div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown("<div class='stage-card'><b>2 · ASSESS RISK</b><br><span class='small-muted'>What could go wrong?</span><br><br>Institutions · Culture · Policy · FX · Monetary System</div>", unsafe_allow_html=True)
with cols[2]:
    st.markdown("<div class='stage-card'><b>3 · ENTER & COMPETE</b><br><span class='small-muted'>What should we actually do?</span><br><br>FDI · Strategy · Organization · Entry Mode</div>", unsafe_allow_html=True)

st.divider()

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔎 1. Opportunity Radar", "⚠️ 2. Risk Lab", "🚪 3. Entry Strategy", "🏁 Boardroom Decision"
])

# Opportunity weights
with tab1:
    st.subheader("Module 1: Identify the Opportunity")
    st.write("Adjust what matters to your company. The ranking changes as your strategic priorities change.")

    a, b, c = st.columns(3)
    w_global = a.slider("Global connectivity", 0, 100, 30, help="Ch. 1 — Globalization")
    w_dev = b.slider("Economic development / purchasing power", 0, 100, 40, help="Ch. 3 — Economic Development")
    w_trade = c.slider("Trade advantage / openness", 0, 100, 30, help="Ch. 6 — International Trade Theory")
    total = max(w_global + w_dev + w_trade, 1)

    opp_rows = []
    for country in selected:
        d = COUNTRIES[country]
        score = (d["globalization"]*w_global + d["development"]*w_dev + d["trade"]*w_trade) / total
        opp_rows.append([country, round(score,1), d["globalization"], d["development"], d["trade"], d["note"]])
    opp_df = pd.DataFrame(opp_rows, columns=["Market", "Opportunity Score", "Globalization", "Development", "Trade", "Interpretation"])
    opp_df = opp_df.sort_values("Opportunity Score", ascending=False)
    st.dataframe(opp_df, use_container_width=True, hide_index=True)
    st.bar_chart(opp_df.set_index("Market")["Opportunity Score"])

    leader = opp_df.iloc[0]
    st.success(f"Current opportunity leader: **{leader['Market']}** ({leader['Opportunity Score']}/100).")
    st.info("Class prompt: Is the highest-growth or highest-income market automatically the best opportunity? What does trade theory add that market size alone misses?")

with tab2:
    st.subheader("Module 2: Risk Lab")
    st.write("Opportunity is not enough. Stress-test the markets using the institutional and cross-border risks covered in the course.")

    risk_country = st.selectbox("Market to stress-test", selected, key="risk_country")
    d = COUNTRIES[risk_country]

    c1, c2, c3 = st.columns(3)
    shock = c1.selectbox("Scenario shock", ["None", "25% tariff introduced", "Currency depreciates 15%", "Political instability rises", "Major cultural backlash", "Regional integration deepens"])
    exposure = c2.slider("Your firm's exposure to this market", 0, 100, 65)
    adaptability = c3.slider("Ability to adapt locally", 0, 100, 60)

    base_components = {
        "Political / legal": 100-d["political"]*.55-d["legal"]*.45,
        "Culture": 100-d["culture"],
        "Ethics / sustainability": 100-d["ethics"],
        "Trade policy": 100-d["trade"],
        "Regional integration": 100-d["integration"],
        "Foreign exchange": 100-d["fx"],
        "Monetary system": 100-d["monetary"]
    }

    impact = 0
    shock_text = "No additional shock applied."
    if shock == "25% tariff introduced":
        base_components["Trade policy"] = min(100, base_components["Trade policy"] + 30)
        impact = 9
        shock_text = "A tariff shock increases landed cost and can change the preferred entry mode."
    elif shock == "Currency depreciates 15%":
        base_components["Foreign exchange"] = min(100, base_components["Foreign exchange"] + 32)
        impact = 8
        shock_text = "FX depreciation changes pricing, repatriated profits, sourcing costs, and hedging needs."
    elif shock == "Political instability rises":
        base_components["Political / legal"] = min(100, base_components["Political / legal"] + 35)
        impact = 10
        shock_text = "Institutional uncertainty raises the option value of flexible, lower-commitment entry."
    elif shock == "Major cultural backlash":
        base_components["Culture"] = min(100, base_components["Culture"] + 35)
        impact = 8
        shock_text = "Low local legitimacy can turn a commercially attractive launch into a strategic failure."
    elif shock == "Regional integration deepens":
        base_components["Regional integration"] = max(0, base_components["Regional integration"] - 25)
        impact = -5
        shock_text = "Deeper integration can reduce market fragmentation and expand the effective addressable market."

    risk_df = pd.DataFrame({"Risk dimension": list(base_components.keys()), "Risk (0=low, 100=high)": [round(v,1) for v in base_components.values()]})
    raw_risk = risk_df["Risk (0=low, 100=high)"].mean()
    adjusted_risk = np.clip(raw_risk * (0.65 + exposure/200) * (1.15 - adaptability/250) + impact, 0, 100)

    left, right = st.columns([1,2])
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

with tab3:
    st.subheader("Module 4: Choose the Entry Strategy")
    st.write("Now convert your analysis into an actionable international strategy.")

    entry_country = st.selectbox("Target market", selected, key="entry_country")
    d = COUNTRIES[entry_country]
    ind = INDUSTRIES[industry]

    c1, c2, c3, c4 = st.columns(4)
    desired_control = c1.slider("Desired control", 0, 100, int(d["control_need"]))
    speed = c2.slider("Need for speed", 0, 100, ind["speed"])
    capital = c3.slider("Capital available", 0, 100, 60)
    local_knowledge = c4.slider("Need for local knowledge", 0, 100, int(d["local_partner"]))

    # Heuristic suitability scores for teaching
    modes = {
        "Exporting": 78 + speed*.18 - desired_control*.22 - local_knowledge*.08 + (100-capital)*.05,
        "Licensing / Franchising": 70 + speed*.15 - desired_control*.28 + local_knowledge*.12 + (100-capital)*.10,
        "Joint Venture": 58 + desired_control*.08 + local_knowledge*.32 + capital*.08 - speed*.04,
        "Wholly Owned Subsidiary / FDI": 42 + desired_control*.40 + capital*.26 - local_knowledge*.06 - speed*.12,
        "Strategic Alliance": 61 + local_knowledge*.27 + speed*.10 + desired_control*.06 + (100-capital)*.06,
    }
    mode_df = pd.DataFrame({"Entry mode": modes.keys(), "Strategic fit": [round(np.clip(v,0,100),1) for v in modes.values()]})
    mode_df = mode_df.sort_values("Strategic fit", ascending=False)

    best_mode = mode_df.iloc[0]["Entry mode"]
    best_fit = mode_df.iloc[0]["Strategic fit"]
    st.dataframe(mode_df, use_container_width=True, hide_index=True)
    st.bar_chart(mode_df.set_index("Entry mode"))
    st.success(f"Recommended entry mode: **{best_mode}** — fit score {best_fit:.1f}/100")

    if desired_control > 70 and capital < 45:
        st.warning("Strategic tension detected: you want high control but have limited capital. Defend the trade-off.")
    if local_knowledge > 75 and best_mode == "Wholly Owned Subsidiary / FDI":
        st.warning("Strategic tension detected: strong local-knowledge needs may make a local partner valuable even if control is important.")

    st.info("Class prompt: Why might two firms entering the same country rationally choose different entry modes?")

with tab4:
    st.subheader("Boardroom Decision")
    st.write("Pull the entire course together. The goal is not to maximize a score—it is to make a defensible decision.")

    # Recompute a common ranking using default / current opportunity weights
    rows = []
    for country in selected:
        d = COUNTRIES[country]
        opportunity = (d["globalization"]*w_global + d["development"]*w_dev + d["trade"]*w_trade) / total
        institutional_risk = np.mean([
            100-d["political"], 100-d["legal"], 100-d["culture"], 100-d["ethics"],
            100-d["integration"], 100-d["fx"], 100-d["monetary"]
        ])
        attractiveness = opportunity - 0.60*institutional_risk
        rows.append([country, round(opportunity,1), round(institutional_risk,1), round(attractiveness,1)])

    board = pd.DataFrame(rows, columns=["Market", "Opportunity", "Risk", "Risk-adjusted attractiveness"]).sort_values("Risk-adjusted attractiveness", ascending=False)
    st.dataframe(board, use_container_width=True, hide_index=True)
    st.bar_chart(board.set_index("Market")["Risk-adjusted attractiveness"])

    winner = board.iloc[0]["Market"]
    st.markdown(
        f"""
        <div class='decision-box'>
        <b>Executive recommendation generated by the demo:</b><br><br>
        Prioritize <b>{winner}</b> for deeper due diligence. The current assumptions produce the strongest risk-adjusted attractiveness among the selected markets. Before final approval, the management team should validate the key assumptions, identify the most decision-relevant uncertainty, and choose an entry mode consistent with control, capital, speed, and local-knowledge needs.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 60-second Board Pitch")
    st.text_area(
        "Student response",
        placeholder="We recommend entering ______ because... The most important opportunity is... The biggest risk is... We would enter through... because...",
        height=150,
    )

    st.markdown("### Decision Check")
    confidence = st.slider("How confident are you in your recommendation?", 0, 100, 70)
    uncertainty = st.selectbox("What could most change your decision?", [
        "New political / legal information", "A major FX movement", "A tariff or trade-policy change",
        "Evidence of different consumer preferences", "A competitor's move", "A change in financing conditions"
    ])
    st.caption(f"Confidence: {confidence}/100 · Key unresolved uncertainty: {uncertainty}")

st.divider()
with st.expander("📚 How the app maps to the BUS 346 chapters"):
    for stage, chapters in CHAPTER_MAP.items():
        st.markdown(f"**{stage}**")
        for ch in chapters:
            st.write("• " + ch)

with st.expander("👩‍🏫 Instructor mode: suggested classroom uses"):
    st.markdown(
        """
        **Before class:** assign each group a company/industry and 3 candidate countries.  
        **During class:** reveal a shock in the Risk Lab and require teams to revise their decision.  
        **After class:** students submit a one-page board memo defending the final country and entry mode.  
        **Assessment twist:** award marks for reasoning and assumptions—not for choosing the app's top-ranked market.
        """
    )

st.caption("BUS 346 teaching demo · Illustrative scores only · Designed for discussion, not real investment advice")
