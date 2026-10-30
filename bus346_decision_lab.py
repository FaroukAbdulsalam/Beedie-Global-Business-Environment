"""
BUS 346 — Global Business Environment
Global Market Entry Decision Lab (v2)

One lens per chapter (Ch. 1–14). Each group reflects on its chapter, diagnoses
how the app uses (or ignores) that chapter's learning outcomes, proposes an
upgrade, and tests the upgrade's effect on the investment decision in the
Upgrade Lab.

All country values are ILLUSTRATIVE, approximately calibrated to public sources
(World Bank WDI/WGI, KOF, Hofstede, TI CPI, ITUC, Yale EPI, WTO tariff profiles,
OECD FDI index, IMF AREAER, Damodaran CRP) circa 2024–25. Replacing them with
sourced, dated values is itself a group upgrade task.

Run:  streamlit run bus346_decision_lab.py
"""

import math
from datetime import datetime
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="BUS 346 | Global Market Entry Decision Lab", page_icon="🌍", layout="wide")


# =========================================================
# Display helpers (robust across Streamlit versions)
# =========================================================
def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except Exception:
        st.dataframe(df, use_container_width=True, **kw)


def show_chart(chart):
    try:
        st.altair_chart(chart, width="stretch")
    except Exception:
        st.altair_chart(chart, use_container_width=True)


def fmt(v, nd=1):
    if v is None:
        return "—"
    if isinstance(v, (float, np.floating)):
        return "—" if math.isnan(v) else f"{v:,.{nd}f}"
    if isinstance(v, (int, np.integer)):
        return f"{v:,}"
    return str(v)


def scale(x, lo, hi):
    """Linear rescale to 0–100, clipped."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return float("nan")
    return float(np.clip((x - lo) / (hi - lo) * 100, 0, 100))


st.markdown(
    """
    <style>
    .hero {font-size: 2.1rem; font-weight: 800; line-height: 1.15; margin-bottom: .2rem;}
    .sub {opacity: .75; font-size: 1.02rem; margin-bottom: 1rem; max-width: 70ch;}
    .stage {border: 1px solid rgba(127,127,127,.28); border-radius: 12px; padding: .8rem .9rem;
            background: rgba(127,127,127,.06); min-height: 132px;}
    .stage b {font-size: 1rem;}
    .stage .q {opacity: .75; font-size: .9rem;}
    .verdict {border-radius: 12px; padding: 1rem 1.2rem; border: 1px solid rgba(127,127,127,.3);
              background: rgba(90,130,200,.08);}
    .pill {display:inline-block; padding:.05rem .55rem; border-radius:999px; font-size:.8rem; margin:.1rem .25rem .1rem 0;
           border:1px solid rgba(127,127,127,.35);}
    .pill-Modeled {background: rgba(46,160,90,.18);}
    .pill-Partial {background: rgba(230,170,40,.20);}
    .pill-Gap {background: rgba(220,70,70,.18);}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Course structure: chapters, learning outcomes, coverage status
#   Modeled = enters a score; Partial = proxy, label or discussion prompt only;
#   Gap = not represented yet -> natural upgrade target for the group
# =========================================================
MOD, PAR, GAP = "Modeled", "Partial", "Gap"

CHAPTERS = {
    1: {"title": "Globalization", "short": "Globalization", "los": [
        ("1-1", "Understand what is meant by the term globalization.", PAR),
        ("1-2", "Recognize the main drivers of globalization.", GAP),
        ("1-3", "Describe the changing nature of the global economy.", MOD),
        ("1-4", "Explain the main arguments in the debate over the impact of globalization.", GAP),
        ("1-5", "Understand how the process of globalization is creating opportunities and challenges for management practice.", PAR)]},
    2: {"title": "National Differences in Political, Economic & Legal Systems", "short": "Pol/Econ/Legal", "los": [
        ("2-1", "Understand how the political systems of countries differ.", MOD),
        ("2-2", "Understand how the economic systems of countries differ.", PAR),
        ("2-3", "Understand how the legal systems of countries differ.", MOD),
        ("2-4", "Explain the implications for management practice of national differences in political economy.", MOD)]},
    3: {"title": "National Differences in Economic Development", "short": "Development", "los": [
        ("3-1", "Explain what determines the level of economic development of a nation.", MOD),
        ("3-2", "Identify the macropolitical and macroeconomic changes occurring worldwide.", GAP),
        ("3-3", "Describe how transition economies are moving toward market-based systems.", PAR),
        ("3-4", "Explain the implications for management practice of national difference in political economy.", MOD)]},
    4: {"title": "Differences in Culture", "short": "Culture", "los": [
        ("4-1", "Explain what is meant by the culture of a society.", PAR),
        ("4-2", "Identify the forces that lead to differences in social culture.", GAP),
        ("4-3", "Identify the business and economic implications of differences in culture.", MOD),
        ("4-4", "Recognize how differences in social culture influence values in business.", PAR),
        ("4-5", "Demonstrate an appreciation for the economic and business implications of cultural change.", GAP)]},
    5: {"title": "Ethics, CSR & Sustainability", "short": "Ethics & CSR", "los": [
        ("5-1", "Understand the ethical, CSR, and sustainability issues faced by international businesses.", MOD),
        ("5-2", "Recognize an ethical, CSR, and/or sustainability dilemma.", PAR),
        ("5-3", "Identify the causes of unethical behavior by managers.", GAP),
        ("5-4", "Describe the different philosophical approaches to business ethics that apply globally.", PAR),
        ("5-5", "Explain how global managers can incorporate ethical considerations into decision-making, CSR and sustainability.", MOD)]},
    6: {"title": "International Trade Theory", "short": "Trade theory", "los": [
        ("6-1", "Understand why nations trade with each other.", PAR),
        ("6-2", "Summarize the different theories explaining trade flows between nations.", MOD),
        ("6-3", "Recognize why many economists believe unrestricted free trade raises economic welfare.", GAP),
        ("6-4", "Explain arguments that government can promote national competitive advantage in certain industries.", GAP),
        ("6-5", "Understand the implications that international trade theory holds for management practice.", MOD)]},
    7: {"title": "Government Policy & International Trade", "short": "Trade policy", "los": [
        ("7-1", "Identify the policy instruments used by governments to influence international trade flows.", MOD),
        ("7-2", "Understand why governments sometimes intervene in international trade.", GAP),
        ("7-3", "Summarize and explain the arguments against strategic trade policy.", GAP),
        ("7-4", "Describe the development of the world trading system and the current trade issues.", PAR),
        ("7-5", "Explain the implications for managers of developments in the world trading system.", MOD)]},
    8: {"title": "Foreign Direct Investment", "short": "FDI regime", "los": [
        ("8-1", "Recognize current trends regarding FDI in the world economy.", GAP),
        ("8-2", "Explain the different theories of FDI.", MOD),
        ("8-3", "Understand how political ideology shapes a government's attitudes toward FDI.", PAR),
        ("8-4", "Describe the benefits and costs of FDI to home and host countries.", GAP),
        ("8-5", "Explain the range of policy instruments that governments use to influence FDI.", MOD),
        ("8-6", "Identify the implications for managers of FDI theory and government policies.", MOD)]},
    9: {"title": "Regional Economic Integration", "short": "Integration", "los": [
        ("9-1", "Describe the different levels of regional economic integration.", MOD),
        ("9-2", "Understand the economic and political arguments for regional economic integration.", MOD),
        ("9-3", "Understand the economic and political arguments against regional economic integration.", GAP),
        ("9-4", "Explain the history, scope, and prospects of the world's most important regional agreements.", PAR),
        ("9-5", "Understand the implications for management practice of regional integration agreements.", MOD)]},
    10: {"title": "The Foreign Exchange Market", "short": "FX market", "los": [
        ("10-1", "Describe the functions of the foreign exchange market.", PAR),
        ("10-2", "Understand what is meant by spot exchange rates.", PAR),
        ("10-3", "Recognize the role that forward exchange rates play in insuring against FX risk.", MOD),
        ("10-4", "Understand the theories explaining how exchange rates are determined.", MOD),
        ("10-5", "Identify the merits of different approaches toward exchange rate forecasting.", MOD),
        ("10-6", "Compare translation, transaction, and economic exposure and their implications.", PAR)]},
    11: {"title": "The International Monetary System", "short": "Monetary system", "los": [
        ("11-1", "Describe the historical development of the modern global monetary system.", GAP),
        ("11-2", "Explain the role of the World Bank and the IMF in the international monetary system.", PAR),
        ("11-3", "Compare and contrast fixed and floating exchange rate systems.", MOD),
        ("11-4", "Identify exchange rate regimes used today and why countries adopt them.", MOD),
        ("11-5", "Understand the debate surrounding the role of the IMF in financial crises.", PAR),
        ("11-6", "Explain the implications of the global monetary system for management practice.", MOD)]},
    12: {"title": "The Global Capital Market", "short": "Capital markets", "los": [
        ("12-1", "Describe the benefits of the global capital market.", PAR),
        ("12-2", "Identify why the global capital market has grown so rapidly.", GAP),
        ("12-3", "Understand the risks associated with the globalization of capital markets.", MOD),
        ("12-4", "Compare the Eurocurrency, global bond, and global equity markets.", GAP),
        ("12-5", "Understand how foreign exchange risks affect the cost of capital.", MOD)]},
    13: {"title": "The Strategy of International Business", "short": "Strategy fit", "los": [
        ("13-1", "Explain the concept of global strategy.", MOD),
        ("13-2", "Recognize how firms can profit by expanding globally.", PAR),
        ("13-3", "Understand how pressures for cost reductions and local responsiveness influence strategic choice.", MOD),
        ("13-4", "Identify and choose the different global strategies for competing in the global marketplace.", MOD)]},
    14: {"title": "The Organization of International Business", "short": "Org fit", "los": [
        ("14-1", "Explain what is meant by organizational architecture.", PAR),
        ("14-2", "Describe the different organizational architecture choices in an international business.", MOD),
        ("14-3", "Explain how organizational architecture can be matched to global strategy.", MOD),
        ("14-4", "Discuss what is required to change organizational architecture to match global strategy.", PAR)]},
}

STAGES = {
    "Opportunity": {"q": "Where is the upside?", "ch": [1, 3, 6]},
    "Operating environment": {"q": "Can we operate here effectively and legitimately?", "ch": [2, 4, 5]},
    "Cross-border rules": {"q": "What rules govern goods and capital crossing the border?", "ch": [7, 8, 9]},
    "Money": {"q": "What happens to the value of what we earn?", "ch": [10, 11, 12]},
    "Execution": {"q": "Are we built to win here?", "ch": [13, 14]},
}
CH_STAGE = {ch: s for s, v in STAGES.items() for ch in v["ch"]}


def ch_label(k):
    return f"Ch. {k} — {CHAPTERS[k]['title']}"


def ch_col(k):
    return f"{k:02d} {CHAPTERS[k]['short']}"


# =========================================================
# Illustrative data
# =========================================================
COUNTRY_ROWS = [
    dict(name="United Arab Emirates", region="Middle East", currency="AED",
         gdp_pc=50.0, growth=4.0, pop=10.5, hdi=0.94, kof=80, trade_open=180,
         reform="Diversifying away from hydrocarbons; rapid regulatory liberalization",
         pol_stab=70, rule_law=78, reg_quality=85,
         political_system="Federal monarchy; state-led diversified market economy",
         legal_system="Civil law with Sharia elements; common-law courts in DIFC/ADGM",
         pdi=74, idv=36, mas=52, uai=66, cpi=68, labour_rights=5, epi=50,
         labour_cost_adv=40, skill=72, infra=90, tariff=5.0, ntb=35,
         fdi_restrict=0.12, fdi_stance="Pragmatic, pro-FDI: full foreign ownership onshore in most sectors since 2021",
         incentives="Free zones (full ownership, customs relief); free-zone corporate tax relief",
         bloc="GCC", bloc_level="Customs union / partial common market", bloc_depth=2.5, bloc_gdp=2.2,
         inflation=2.0, fx_vol=0.5, fx_regime="Conventional peg to USD", regime_type="peg",
         imf="None", reserves_months=6.0, hedge="High", crp=0.9, bond10=4.6, mcap_gdp=180,
         note="Globally connected hub; small domestic market but a strong regional platform."),
    dict(name="India", region="South Asia", currency="INR",
         gdp_pc=2.7, growth=6.5, pop=1440, hdi=0.64, kof=63, trade_open=46,
         reform="Liberalizing mixed economy (reforms since 1991)",
         pol_stab=25, rule_law=55, reg_quality=50,
         political_system="Federal parliamentary democracy; mixed market economy",
         legal_system="Common law",
         pdi=77, idv=48, mas=56, uai=40, cpi=38, labour_rights=5, epi=28,
         labour_cost_adv=85, skill=55, infra=55, tariff=17.0, ntb=60,
         fdi_restrict=0.21, fdi_stance="Pragmatic nationalism: liberalizing, with sectoral caps and approval routes",
         incentives="Production-linked incentive (PLI) schemes; SEZs",
         bloc="SAFTA", bloc_level="Free trade area (shallow)", bloc_depth=1.0, bloc_gdp=4.6,
         inflation=4.0, fx_vol=4.0, fx_regime="Managed float (central bank intervention)", regime_type="managed",
         imf="None", reserves_months=11.0, hedge="Medium", crp=2.6, bond10=6.4, mcap_gdp=130,
         note="Very large growth market; institutional, regional and competitive complexity."),
    dict(name="Germany", region="Europe", currency="EUR",
         gdp_pc=54.0, growth=0.5, pop=84, hdi=0.95, kof=88, trade_open=85,
         reform="Mature social market economy",
         pol_stab=65, rule_law=90, reg_quality=92,
         political_system="Federal parliamentary democracy; social market economy",
         legal_system="Civil law (codified)",
         pdi=35, idv=67, mas=66, uai=65, cpi=75, labour_rights=1, epi=75,
         labour_cost_adv=15, skill=92, infra=88, tariff=5.0, ntb=45,
         fdi_restrict=0.02, fdi_stance="Free-market, with national-security screening of strategic sectors",
         incentives="Regional investment grants; EU-level programmes",
         bloc="European Union (euro area)", bloc_level="Economic and monetary union", bloc_depth=4.0, bloc_gdp=19.4,
         inflation=2.2, fx_vol=7.0, fx_regime="Free float (euro, ECB)", regime_type="euro",
         imf="None", reserves_months=float("nan"), hedge="High", crp=0.0, bond10=2.6, mcap_gdp=50,
         note="Advanced, rules-based market; intense competition and high standards."),
    dict(name="Vietnam", region="Southeast Asia", currency="VND",
         gdp_pc=4.7, growth=6.5, pop=101, hdi=0.73, kof=66, trade_open=165,
         reform="Transition economy (Đổi Mới reforms since 1986)",
         pol_stab=50, rule_law=50, reg_quality=40,
         political_system="Single-party socialist republic; socialist-oriented market economy",
         legal_system="Socialist civil law",
         pdi=70, idv=20, mas=40, uai=30, cpi=40, labour_rights=4, epi=33,
         labour_cost_adv=85, skill=55, infra=60, tariff=9.5, ntb=50,
         fdi_restrict=0.13, fdi_stance="Pragmatic: export-oriented FDI courted with incentives",
         incentives="Tax holidays in industrial and export-processing zones",
         bloc="ASEAN (+ RCEP, CPTPP)", bloc_level="Free trade area (ASEAN Economic Community)", bloc_depth=1.5, bloc_gdp=3.9,
         inflation=3.5, fx_vol=3.0, fx_regime="Stabilized arrangement vs USD", regime_type="crawl",
         imf="None", reserves_months=3.0, hedge="Low", crp=3.0, bond10=3.0, mcap_gdp=60,
         note="Fast-growing manufacturing and consumer economy in Asian supply chains."),
    dict(name="Brazil", region="Latin America", currency="BRL",
         gdp_pc=10.0, growth=2.5, pop=212, hdi=0.76, kof=63, trade_open=35,
         reform="Emerging market economy",
         pol_stab=30, rule_law=42, reg_quality=45,
         political_system="Federal presidential democracy; mixed market economy",
         legal_system="Civil law",
         pdi=69, idv=38, mas=49, uai=76, cpi=34, labour_rights=4, epi=45,
         labour_cost_adv=60, skill=55, infra=50, tariff=11.5, ntb=60,
         fdi_restrict=0.08, fdi_stance="Pragmatic nationalism: open to FDI; complex tax and local-content rules",
         incentives="Regional tax incentives (e.g., Manaus Free Trade Zone)",
         bloc="Mercosur", bloc_level="Customs union (imperfect)", bloc_depth=2.0, bloc_gdp=2.9,
         inflation=5.0, fx_vol=15.0, fx_regime="Free float + inflation targeting", regime_type="float_it",
         imf="None", reserves_months=14.0, hedge="High", crp=3.5, bond10=13.5, mcap_gdp=40,
         note="Large consumer market; regulatory and macroeconomic complexity."),
    dict(name="Mexico", region="North America", currency="MXN",
         gdp_pc=14.0, growth=1.0, pop=130, hdi=0.78, kof=72, trade_open=85,
         reform="Emerging market economy; nearshoring destination",
         pol_stab=20, rule_law=25, reg_quality=50,
         political_system="Federal presidential democracy; market economy with energy-sector nationalism",
         legal_system="Civil law",
         pdi=81, idv=30, mas=69, uai=82, cpi=26, labour_rights=4, epi=45,
         labour_cost_adv=65, skill=55, infra=60, tariff=7.0, ntb=40,
         fdi_restrict=0.19, fdi_stance="Free-market toward manufacturing; nationalist in energy",
         incentives="IMMEX maquila regime; nearshoring incentives",
         bloc="USMCA / CUSMA", bloc_level="Free trade area", bloc_depth=1.0, bloc_gdp=31.0,
         inflation=4.0, fx_vol=12.0, fx_regime="Free float + inflation targeting", regime_type="float_it",
         imf="Precautionary line", reserves_months=5.0, hedge="High", crp=2.5, bond10=9.5, mcap_gdp=30,
         note="Manufacturing platform into North America; security and rule-of-law concerns."),
    dict(name="Ghana", region="West Africa", currency="GHS",
         gdp_pc=2.4, growth=5.0, pop=34, hdi=0.63, kof=62, trade_open=70,
         reform="Emerging market recovering from 2022 debt crisis",
         pol_stab=45, rule_law=55, reg_quality=45,
         political_system="Presidential constitutional democracy; market economy",
         legal_system="Common law",
         pdi=80, idv=15, mas=40, uai=65, cpi=42, labour_rights=3, epi=32,
         labour_cost_adv=85, skill=45, infra=45, tariff=12.0, ntb=50,
         fdi_restrict=0.15, fdi_stance="Pragmatic: FDI welcome, minimum-capital rules for foreign investors",
         incentives="Free Zones regime; sector incentives",
         bloc="ECOWAS (+ AfCFTA)", bloc_level="Customs union (common external tariff)", bloc_depth=2.0, bloc_gdp=0.8,
         inflation=12.0, fx_vol=20.0, fx_regime="Floating", regime_type="float",
         imf="Programme (recent/active)", reserves_months=4.0, hedge="Low", crp=9.0, bond10=20.0, mcap_gdp=8,
         note="Stable democracy with strong growth potential; macro-financial fragility after default."),
]
BASE_DF = pd.DataFrame(COUNTRY_ROWS)
NUMERIC_COLS = ["gdp_pc", "growth", "pop", "hdi", "kof", "trade_open", "pol_stab", "rule_law", "reg_quality",
                "pdi", "idv", "mas", "uai", "cpi", "labour_rights", "epi", "labour_cost_adv", "skill", "infra",
                "tariff", "ntb", "fdi_restrict", "bloc_depth", "bloc_gdp", "inflation", "fx_vol",
                "reserves_months", "crp", "bond10", "mcap_gdp"]

HOMES = {
    "Canada": dict(currency="CAD", pdi=39, idv=80, mas=52, uai=48, inflation=2.0, fx_vol=6.0),
    "United States": dict(currency="USD", pdi=40, idv=91, mas=62, uai=46, inflation=2.8, fx_vol=0.0),
    "United Kingdom": dict(currency="GBP", pdi=35, idv=89, mas=66, uai=35, inflation=3.0, fx_vol=8.0),
    "United Arab Emirates": dict(currency="AED", pdi=74, idv=36, mas=52, uai=66, inflation=2.0, fx_vol=0.5),
    "Singapore": dict(currency="SGD", pdi=74, idv=20, mas=48, uai=8, inflation=1.5, fx_vol=4.0),
}
HOME_FTA = {  # in force, illustrative; verify before use
    "Canada": {"Germany": "CETA (Canada–EU)", "Mexico": "CUSMA + CPTPP", "Vietnam": "CPTPP"},
    "United States": {"Mexico": "USMCA"},
    "United Kingdom": {"Germany": "UK–EU TCA", "Vietnam": "UK–Vietnam FTA + CPTPP", "Mexico": "CPTPP",
                       "Ghana": "UK–Ghana TPA"},
    "United Arab Emirates": {"India": "UAE–India CEPA"},
    "Singapore": {"Vietnam": "ATIGA + CPTPP", "India": "CECA", "Germany": "EU–Singapore FTA", "Mexico": "CPTPP",
                  "United Arab Emirates": "GCC–Singapore FTA"},
}

INDUSTRIES = {
    "Consumer Technology": dict(cost=80, resp=45, labour_int=40, skill_int=70, ip=85, speed=85, regulated=40, ethics_exp=0.7, goods=0.8),
    "Food & Beverage": dict(cost=55, resp=85, labour_int=60, skill_int=35, ip=50, speed=70, regulated=50, ethics_exp=0.6, goods=0.6),
    "Financial Services": dict(cost=50, resp=80, labour_int=10, skill_int=90, ip=70, speed=55, regulated=90, ethics_exp=0.2, goods=0.1),
    "Industrial Manufacturing": dict(cost=85, resp=30, labour_int=70, skill_int=50, ip=65, speed=45, regulated=50, ethics_exp=0.9, goods=0.9),
    "Professional Services": dict(cost=35, resp=75, labour_int=10, skill_int=90, ip=60, speed=85, regulated=50, ethics_exp=0.2, goods=0.15),
    "Clean Energy Equipment": dict(cost=75, resp=55, labour_int=45, skill_int=65, ip=75, speed=50, regulated=75, ethics_exp=0.8, goods=0.8),
}

MOTIVES = {  # chapter-weight multipliers (Ch. 8 FDI motives)
    "Market-seeking": {3: 1.5, 4: 1.25, 9: 1.25},
    "Efficiency-seeking (export platform)": {6: 1.5, 7: 1.25, 9: 1.25},
    "Strategic-asset-seeking": {1: 1.25, 2: 1.25, 12: 1.25},
    "Resource-seeking": {2: 1.25, 6: 1.25},
}

STRATEGIES = ["Global standardization", "Localization", "Transnational", "International"]
STRAT_POINTS = {"Global standardization": (80, 25), "Localization": (35, 80), "Transnational": (80, 80), "International": (30, 30)}
STRUCTURES = ["Domestic structure + export department", "International division", "Worldwide area structure",
              "Worldwide product divisions", "Global matrix"]
COMPAT = {  # structure x required strategy fit (0–100), after Hill Ch. 14
    "Domestic structure + export department": {"Localization": 25, "International": 55, "Global standardization": 35, "Transnational": 10},
    "International division": {"Localization": 40, "International": 85, "Global standardization": 45, "Transnational": 25},
    "Worldwide area structure": {"Localization": 90, "International": 45, "Global standardization": 30, "Transnational": 50},
    "Worldwide product divisions": {"Localization": 35, "International": 70, "Global standardization": 90, "Transnational": 55},
    "Global matrix": {"Localization": 60, "International": 50, "Global standardization": 60, "Transnational": 90},
}
ARCH = {
    "Localization": {"Structure": "Worldwide area structure", "Decision rights": "Decentralized to country subsidiaries",
                     "Integrating mechanisms": "Low; little cross-unit coordination", "Controls": "Output controls (subsidiary P&L)",
                     "Incentives": "Tied to country or area performance", "Culture": "Low reliance on shared corporate culture"},
    "International": {"Structure": "International division, then worldwide product divisions",
                      "Decision rights": "Core competencies centralized; some local discretion",
                      "Integrating mechanisms": "Moderate", "Controls": "Output and personal controls",
                      "Incentives": "Mix of unit and product performance", "Culture": "Moderate"},
    "Global standardization": {"Structure": "Worldwide product divisions", "Decision rights": "Centralized product and process decisions",
                               "Integrating mechanisms": "High within product divisions", "Controls": "Output and bureaucratic (standards, process)",
                               "Incentives": "Tied to global product performance", "Culture": "Moderate to high"},
    "Transnational": {"Structure": "Global matrix plus informal networks ('matrix in the mind')",
                      "Decision rights": "Mixed: centralized or decentralized by activity",
                      "Integrating mechanisms": "Very high; knowledge flows in all directions", "Controls": "Cultural controls plus output",
                      "Incentives": "Team and global outcomes, not only unit P&L", "Culture": "Strong shared culture essential"},
}
REGIME_CRED = {"euro": 90, "peg": 80, "float_it": 75, "managed": 65, "crawl": 55, "float": 45}
HEDGE_PEN = {"High": 0, "Medium": 50, "Low": 100}
HEDGE_DOWN = {"High": "Medium", "Medium": "Low", "Low": "Low"}

SHOCKS = {
    "None": "",
    "Tariff escalation (+25 pp on imports)": "Ch. 7: higher landed cost of exports; strengthens the tariff-jumping case for local production.",
    "Currency crisis (sharp depreciation, higher volatility)": "Ch. 10–11: expected depreciation +10 pp, volatility +10 pp, hedging gets harder.",
    "Political instability (−25 pts stability)": "Ch. 2: institutional uncertainty raises the value of staged commitment.",
    "Cultural backlash against foreign brands": "Ch. 4 & 13: legitimacy falls; local-responsiveness pressure rises.",
    "Global capital tightening (+2 pp country risk premium)": "Ch. 12: higher hurdle rates and local borrowing costs.",
    "Regional integration deepens (deeper bloc + home FTA)": "Ch. 9: integration depth +1 level and a home-country FTA concluded.",
    "Supply-chain due-diligence law at home": "Ch. 5: ethics exposure rises 30% and the ethics threshold rises 15 points (applies to all markets).",
    "Geoeconomic fragmentation (trade hubs hit)": "Ch. 1 & 7: globalization index −8 in trade hubs, tariffs +8 pp.",
}

# =========================================================
# Chapter methods and upgrade prompts
# =========================================================
METHODS = {
    1: "**Score** = 0.6 × KOF globalization index + 0.4 × trade openness (% GDP, rescaled 20→180).\n\nTreats connectedness as upside only.",
    2: "**Score** = 0.40 × political stability + w × rule of law + (0.60 − w) × regulatory quality, where w = 0.25 + 0.20 × industry IP sensitivity.\n\nIP-heavy industries lean harder on rule of law. Political and legal *system type* is shown as a label but not scored.",
    3: "**Score** = 0.35 × market size (log GDP) + 0.30 × real growth + 0.20 × income (log GDP per capita) + 0.15 × HDI.",
    4: "**Cultural distance** = Kogut–Singh index over Hofstede PDI, IDV, MAS, UAI vs your home market.\n\n**Score** = 100 − distance × (0.5 + 0.5 × industry local-responsiveness need). Distance hurts adaptation-heavy industries more.",
    5: "**Base** = 0.4 × corruption perceptions + 0.3 × labour-rights protection + 0.3 × environmental performance.\n\n**Score** = 100 − (100 − base) × (0.6 + 0.4 × industry supply-chain exposure). In the Boardroom, the firm's ethics policy decides whether a low score is advisory, a due-diligence condition, or a veto.",
    6: "**Factor fit** (Heckscher–Ohlin) = industry labour intensity × labour-cost advantage + industry skill intensity × skill base (normalized).\n\n**Score** = 0.75 × factor fit + 0.25 × logistics infrastructure. Weighted up for efficiency-seeking FDI.",
    7: "**Effective tariff** = MFN applied tariff × industry goods share.\n\n**Score** = 100 − (0.6 × effective tariff rescaled 0→25 + 0.4 × non-tariff barrier index). Measures host policy barriers; preferential access is credited in Ch. 9, not here, to avoid double counting.",
    8: "**Score** = 100 − rescaled [FDI restrictiveness × (0.5 + industry regulatory sensitivity)].\n\nFDI theory (internalization, OLI) drives the entry-mode logic in the Boardroom.",
    9: "**Score** = 0.45 × bloc market reach (log bloc GDP) + 0.25 × integration depth (FTA→economic union) + 0.30 × home-country FTA access.",
    10: "**Expected depreciation** (relative PPP) = (1 + π host) / (1 + π home) − 1. **Volatility vs home** ≈ √(σ²host + σ²home), assuming independence.\n\n**Score** = 100 − (0.50 × depreciation + 0.35 × volatility + 0.15 × hedging difficulty).",
    11: "**Score** = 0.55 × regime credibility + 0.45 × reserve adequacy (months of imports) − 12 if an IMF programme is active or recent.",
    12: "**Score** = 0.55 × (inverse country risk premium) + 0.25 × equity market depth + 0.20 × (inverse local 10-yr yield).\n\nThe CRP also enters the hurdle rate in the Financial Case.",
    13: "**Required strategy** from the integration–responsiveness grid: cost pressure (industry) vs local-responsiveness pressure (industry, adjusted for cultural distance).\n\n**Score** = fit between the strategy this market demands and your firm's current strategy.",
    14: "**Score** = fit between your current organizational structure and the architecture the required strategy calls for (Hill's strategy–architecture match).",
}

PROMPTS = {
    1: ["Connectedness is scored as pure upside. Should exposure to geoeconomic fragmentation (the 1-4 debate) count as risk? Propose an indicator and a data source.",
        "Which drivers of globalization (1-2) matter most for our industry (falling barriers, technology, digital trade), and how would you measure them by country?",
        "Should services firms use digital connectivity instead of trade openness?"],
    2: ["Stability, rule of law and regulatory quality are averaged. Should a very low value act as a gate instead of lowering an average?",
        "Legal family is only a label. How should common vs civil law affect contract enforcement or the entry mode?",
        "Economic system (2-2) is not scored. Propose a measure (economic freedom, SOE share of output) and justify it."],
    3: ["Market size uses nominal GDP. Would PPP income, middle-class size, or inequality give a better read for our product?",
        "3-2 macro trends are missing. Propose a forward-looking indicator (reform momentum, demographic dividend).",
        "Transition economies: should the app reward the direction of reform, not just its level?"],
    4: ["Kogut–Singh uses four Hofstede dimensions. Critique this against 4-1 and propose additions (language, religion, GLOBE).",
        "Culture is static here. How would you capture cultural change (4-5)?",
        "Should cultural distance change the go/no-go decision, or only how we enter?"],
    5: ["Is ethics a weight, a gate, or both? Defend the firm's ethics policy with one philosophical approach (5-4).",
        "5-3 causes of unethical behaviour are inside the firm. Add a firm-side checklist (incentives, culture, pressure, leadership).",
        "Add a sustainability indicator specific to our industry (climate transition, water stress, conflict minerals)."],
    6: ["Factor fit is Heckscher–Ohlin. Where would Porter's diamond or new trade theory change the answer for our industry?",
        "6-3 welfare gains from free trade are not modeled. Should the app reward markets locked into deep trade rules?",
        "6-4 industrial policy: should host subsidies for our industry count as opportunity or as distortion risk?"],
    7: ["Only MFN tariffs and an NTB index are used. Add specific instruments from 7-1 (quotas, local content, antidumping, export controls).",
        "Calibrate the tariff shock to a real recent tariff episode and show how the decision moves.",
        "How should WTO dispute status or trade-remedy exposure enter the score (7-4)?"],
    8: ["One restrictiveness index hides sector caps, screening and incentives. Break it apart (8-5).",
        "8-4 host-country costs and benefits shape how politically durable our investment is. How would you score that?",
        "Which FDI theory should drive the entry-mode logic (internalization, OLI, product life cycle), and is the current formula consistent with it?"],
    9: ["Bloc GDP rewards big blocs regardless of rules of origin. Add an RoO or utilization factor.",
        "9-3 trade diversion: could a bloc we are outside of hurt our home-country exports?",
        "How should the score treat agreements that are signed but not ratified?"],
    10: ["Expected depreciation uses relative PPP. Compare with interest-rate parity and forward rates (10-3, 10-4).",
         "Volatility assumes currencies move independently. Replace with real cross-rate volatility data.",
         "Separate transaction, translation and economic exposure in the Financial Case (10-6)."],
    11: ["Regime credibility values are judgement calls. Ground them in the IMF's de facto regime classification.",
         "Reserve months exclude sovereign wealth funds. Should they count (the UAE case)?",
         "Is an IMF programme a risk signal or a credibility anchor (11-5)? Model both views and compare."],
    12: ["The country risk premium is added to the hurdle rate. Argue for or against this approach (12-5).",
         "Should local-currency borrowing be offered as a natural hedge? Add a financing-route selector.",
         "12-4: when would Eurobond or global equity financing beat local financing for this market?"],
    13: ["Local-responsiveness pressure only reflects industry and culture. What market-specific pressures (regulation, distribution channels) should raise it?",
         "13-2 location economies and experience effects: link the strategy score to the Ch. 6 factor fit.",
         "Should the firm run different strategies in different markets, or one strategy everywhere?"],
    14: ["Fit uses structure only. Add controls, incentives, processes and culture (14-1).",
         "Score the cost of changing architecture (14-4) and let it penalize markets that demand transnational capability.",
         "How would you represent the 'matrix in the mind' in an app?"],
}

# =========================================================
# Sidebar
# =========================================================
sb_setup = st.sidebar.container()
sb_data = st.sidebar.expander("📂 Replace the illustrative data (CSV)")

with sb_data:
    st.caption("Download the data, replace values with sourced figures (cite them in your proposal), "
               "and upload it back. New rows add new countries.")
    st.download_button("Download country data", BASE_DF.to_csv(index=False).encode(), "bus346_country_data.csv", "text/csv")
    upload = st.file_uploader("Upload revised country data", type="csv", key="data_upload")
    data_df = BASE_DF.copy()
    if upload is not None:
        try:
            new_df = pd.read_csv(upload)
            missing = [c for c in BASE_DF.columns if c not in new_df.columns]
            if missing:
                st.error(f"Upload ignored. Missing columns: {', '.join(missing)}")
            else:
                for col in NUMERIC_COLS:
                    new_df[col] = pd.to_numeric(new_df[col], errors="coerce")
                data_df = new_df
                st.success(f"Using uploaded data: {len(new_df)} countries.")
        except Exception as e:
            st.error(f"Upload ignored: {e}")

DATA = {r["name"]: r for r in data_df.to_dict("records")}

with sb_setup:
    st.header("🎯 Mission setup")
    company = st.text_input("Company", "NorthStar Global")
    industry = st.selectbox("Industry", list(INDUSTRIES))
    home = st.selectbox("Home market", list(HOMES))
    options = [c for c in DATA if c != home]
    default = [c for c in ["United Arab Emirates", "India", "Germany", "Vietnam"] if c in options]
    markets = st.multiselect("Candidate markets", options, default=default)
    focus = st.selectbox("Focus market (Financial Case and Boardroom)", markets) if markets else None
    motive = st.selectbox("Primary FDI motive (Ch. 8)", list(MOTIVES))

    with st.expander("Firm profile (Ch. 13–14)"):
        cur_strategy = st.selectbox("Current global strategy", STRATEGIES, index=3)
        cur_structure = st.selectbox("Current organizational structure", STRUCTURES, index=1)
        capital = st.slider("Capital available for this expansion", 0, 100, 60)
        speed = st.slider("Need for speed", 0, 100, INDUSTRIES[industry]["speed"], key=f"speed_{industry}")

    with st.expander("Ethics policy (Ch. 5)"):
        ethics_policy = st.radio("When a market falls below the threshold",
                                 ["Advisory only", "Enhanced due diligence required", "Hard veto"], index=1)
        ethics_thr = st.slider("Ethics threshold", 0, 100, 40)

    with st.expander("Scenario shock (instructor)"):
        shock = st.selectbox("Shock", list(SHOCKS))
        shock_target = st.selectbox("Applies to", ["All candidate markets"] + markets)

    with st.expander("Chapter weights (groups may propose changes)"):
        st.caption("1.0 = equal weight. Your FDI motive multiplies these.")
        user_w = {k: st.slider(f"Ch. {k} {CHAPTERS[k]['short']}", 0.0, 3.0, 1.0, 0.25, key=f"w_{k}") for k in CHAPTERS}

    st.caption("Illustrative teaching data, approximately calibrated to public sources. Not investment advice.")

if not markets:
    st.markdown('<div class="hero">🌍 Global Market Entry Decision Lab</div>', unsafe_allow_html=True)
    st.warning("Choose at least one candidate market in the sidebar to start.")
    st.stop()

# =========================================================
# Scenario shocks and context
# =========================================================
targets = set(markets) if shock_target == "All candidate markets" else {shock_target}
D = {m: dict(DATA[m]) for m in markets}
ctx = dict(home=HOMES[home], home_name=home, ind=INDUSTRIES[industry], fta_forced=set(), backlash=set(),
           crisis=set(), dd_law=False, cur_strategy=cur_strategy, cur_structure=cur_structure,
           capital=capital, speed=speed)

for m in targets:
    c = D[m]
    if shock.startswith("Tariff escalation"):
        c["tariff"] += 25
    elif shock.startswith("Currency crisis"):
        ctx["crisis"].add(m)
    elif shock.startswith("Political instability"):
        c["pol_stab"] = max(0, c["pol_stab"] - 25)
    elif shock.startswith("Cultural backlash"):
        ctx["backlash"].add(m)
    elif shock.startswith("Global capital tightening"):
        c["crp"] += 2.0 if c["crp"] >= 1 else 0.5
        c["bond10"] += 1.5
    elif shock.startswith("Regional integration"):
        c["bloc_depth"] = min(4.0, c["bloc_depth"] + 1)
        ctx["fta_forced"].add(m)
    elif shock.startswith("Geoeconomic fragmentation"):
        if c["trade_open"] > 100:
            c["kof"] = max(0, c["kof"] - 8)
        c["tariff"] += 8
if shock.startswith("Supply-chain"):
    ctx["dd_law"] = True

effective_thr = min(100, ethics_thr + (15 if ctx["dd_law"] else 0))

# Kogut–Singh variances across all countries in the data and home markets
_hof = pd.concat([data_df[["name", "pdi", "idv", "mas", "uai"]],
                  pd.DataFrame([{"name": k, **{d: v[d] for d in ["pdi", "idv", "mas", "uai"]}} for k, v in HOMES.items()])])
_hof = _hof.drop_duplicates("name")
HOF_VAR = {d: float(_hof[d].var(ddof=1)) for d in ["pdi", "idv", "mas", "uai"]}


def kogut_singh(c, h):
    return sum((c[d] - h[d]) ** 2 / HOF_VAR[d] for d in HOF_VAR) / 4


def required_strategy(cost, resp, thr=55):
    if cost >= thr and resp >= thr:
        return "Transnational"
    if cost >= thr:
        return "Global standardization"
    if resp >= thr:
        return "Localization"
    return "International"


def home_fta(name, ctx):
    if name in ctx["fta_forced"]:
        return HOME_FTA.get(ctx["home_name"], {}).get(name, "New agreement (scenario)")
    return HOME_FTA.get(ctx["home_name"], {}).get(name)


def fx_profile(c, name, ctx):
    h = ctx["home"]
    dep = ((1 + c["inflation"] / 100) / (1 + h["inflation"] / 100) - 1) * 100
    vol = math.sqrt(c["fx_vol"] ** 2 + h["fx_vol"] ** 2)
    hedge = c["hedge"] if c["hedge"] in HEDGE_PEN else "Medium"
    if name in ctx["crisis"]:
        dep += 10
        vol += 10
        hedge = HEDGE_DOWN[hedge]
    return dep, vol, hedge


# =========================================================
# Chapter lenses
# =========================================================
def compute_market(c, name, ctx):
    ind, h = ctx["ind"], ctx["home"]
    S, C, N = {}, {}, {}

    # Ch. 1 Globalization
    to = scale(c["trade_open"], 20, 180)
    S[1] = 0.6 * c["kof"] + 0.4 * to
    C[1] = {"KOF globalization index": c["kof"], "Trade openness, % GDP": c["trade_open"], "Openness (0–100)": to}
    N[1] = ("Highly" if S[1] >= 75 else "Moderately" if S[1] >= 55 else "Less") + " integrated into global flows."

    # Ch. 2 Political, economic, legal systems
    w_rl = 0.25 + 0.20 * ind["ip"] / 100
    S[2] = 0.40 * c["pol_stab"] + w_rl * c["rule_law"] + (0.60 - w_rl) * c["reg_quality"]
    C[2] = {"Political stability (pctile)": c["pol_stab"], "Rule of law (pctile)": c["rule_law"],
            "Regulatory quality (pctile)": c["reg_quality"], "Rule-of-law weight": f"{w_rl:.0%}"}
    N[2] = f"{c['political_system']}. Legal system: {c['legal_system']}."

    # Ch. 3 Development
    gdp_total = c["gdp_pc"] * c["pop"]  # $bn
    size = scale(math.log10(max(gdp_total, 1)), math.log10(50), math.log10(30000))
    growth = scale(c["growth"], -1, 8)
    income = scale(math.log10(max(c["gdp_pc"], 0.1)), 0, math.log10(80))
    hdi = scale(c["hdi"], 0.5, 0.95)
    S[3] = 0.35 * size + 0.30 * growth + 0.20 * income + 0.15 * hdi
    C[3] = {"GDP, $bn": gdp_total, "GDP per capita, $k": c["gdp_pc"], "Real growth, %": c["growth"],
            "Population, m": c["pop"], "HDI": c["hdi"], "Size score": size, "Growth score": growth}
    N[3] = c["reform"] + "."

    # Ch. 4 Culture
    ks = kogut_singh(c, h)
    dist = scale(ks, 0, 3.5)
    exposure = 0.5 + 0.5 * ind["resp"] / 100
    S[4] = 100 - dist * exposure - (20 if name in ctx["backlash"] else 0)
    C[4] = {"Power distance (host vs home)": f"{c['pdi']:.0f} vs {h['pdi']}",
            "Individualism": f"{c['idv']:.0f} vs {h['idv']}", "Masculinity": f"{c['mas']:.0f} vs {h['mas']}",
            "Uncertainty avoidance": f"{c['uai']:.0f} vs {h['uai']}", "Kogut–Singh index": ks,
            "Distance (0–100)": dist}
    N[4] = f"Cultural distance from {ctx['home_name']} is {'high' if dist >= 60 else 'moderate' if dist >= 30 else 'low'}." + \
           (" Backlash scenario active." if name in ctx["backlash"] else "")

    # Ch. 5 Ethics, CSR, sustainability
    lab = (5 - c["labour_rights"]) / 4 * 100
    epi = scale(c["epi"], 20, 80)
    base5 = 0.4 * c["cpi"] + 0.3 * lab + 0.3 * epi
    exp5 = min(1.0, ind["ethics_exp"] * (1.3 if ctx["dd_law"] else 1.0))
    S[5] = 100 - (100 - base5) * (0.6 + 0.4 * exp5)
    C[5] = {"Corruption perceptions (0–100)": c["cpi"], "Labour-rights rating (1 best, 5 worst)": c["labour_rights"],
            "Environmental performance": c["epi"], "Base ethics score": base5, "Industry exposure": exp5}
    N[5] = "Below the firm's ethics threshold." if S[5] < effective_thr else "Above the firm's ethics threshold."

    # Ch. 6 Trade theory
    lw, sw = ind["labour_int"], ind["skill_int"]
    fit = (lw * c["labour_cost_adv"] + sw * c["skill"]) / (lw + sw)
    S[6] = 0.75 * fit + 0.25 * c["infra"]
    C[6] = {"Labour-cost advantage": c["labour_cost_adv"], "Skill base": c["skill"], "Logistics infrastructure": c["infra"],
            "Factor-endowment fit": fit}
    N[6] = "Comparative advantage driven by " + ("cheap labour." if lw * c["labour_cost_adv"] > sw * c["skill"] else "skills.")

    # Ch. 7 Trade policy
    eff_t = c["tariff"] * ind["goods"]
    S[7] = 100 - (0.6 * scale(eff_t, 0, 25) + 0.4 * c["ntb"])
    C[7] = {"MFN applied tariff, %": c["tariff"], "Effective tariff for industry, %": eff_t, "Non-tariff barrier index": c["ntb"]}
    N[7] = "High barriers favour local production over exporting (tariff-jumping)." if eff_t > 10 else "Barriers are modest for this industry."

    # Ch. 8 FDI regime
    r_eff = c["fdi_restrict"] * (0.5 + ind["regulated"] / 100)
    S[8] = 100 - scale(r_eff, 0, 0.35)
    C[8] = {"FDI restrictiveness (0–1)": c["fdi_restrict"], "Industry regulatory sensitivity": ind["regulated"],
            "Effective restriction": r_eff}
    N[8] = f"{c['fdi_stance']}. Incentives: {c['incentives']}."

    # Ch. 9 Regional integration
    fta = home_fta(name, ctx)
    reach = scale(math.log10(max(c["bloc_gdp"], 0.1)), math.log10(0.5), math.log10(35))
    depth = scale(c["bloc_depth"], 1, 4)
    S[9] = 0.45 * reach + 0.25 * depth + 0.30 * (100 if fta else 0)
    C[9] = {"Bloc": c["bloc"], "Integration level": c["bloc_level"], "Bloc GDP, $tn": c["bloc_gdp"],
            f"FTA with {ctx['home_name']}": fta or "None"}
    N[9] = f"Member of {c['bloc']}; " + (f"preferential access from home via {fta}." if fta else "no home-country FTA.")

    # Ch. 10 FX market
    dep, vol, hedge = fx_profile(c, name, ctx)
    S[10] = 100 - (0.50 * scale(dep, -2, 15) + 0.35 * scale(vol, 0, 25) + 0.15 * HEDGE_PEN[hedge])
    C[10] = {f"Expected depreciation vs {h['currency']}, %/yr": dep, "Volatility vs home, %": vol, "Hedging market": hedge}
    N[10] = f"PPP implies the {c['currency']} " + ("depreciates" if dep > 0.25 else "appreciates" if dep < -0.25 else "holds steady") + \
            f" against the {h['currency']} by about {abs(dep):.1f}% a year."

    # Ch. 11 Monetary system
    cred = REGIME_CRED.get(c["regime_type"], 50)
    res = 100.0 if pd.isna(c["reserves_months"]) else scale(c["reserves_months"], 2, 12)
    pen = 12 if str(c["imf"]).startswith("Programme") else 0
    S[11] = 0.55 * cred + 0.45 * res - pen
    C[11] = {"Regime": c["fx_regime"], "Regime credibility": cred,
             "Reserves, months of imports": "Reserve-currency issuer" if pd.isna(c["reserves_months"]) else c["reserves_months"],
             "IMF engagement": c["imf"]}
    N[11] = f"{c['fx_regime']}; IMF: {c['imf']}."

    # Ch. 12 Capital markets
    S[12] = 0.55 * (100 - scale(c["crp"], 0, 12)) + 0.25 * scale(c["mcap_gdp"], 5, 150) + 0.20 * (100 - scale(c["bond10"], 2, 20))
    C[12] = {"Country risk premium, %": c["crp"], "10-yr local govt yield, %": c["bond10"], "Stock market cap, % GDP": c["mcap_gdp"]}
    N[12] = f"Adds about {c['crp']:.1f} pp to the hurdle rate."

    # Ch. 13 Strategy
    resp_m = float(np.clip(ind["resp"] + 0.3 * (dist - 50) + (15 if name in ctx["backlash"] else 0), 0, 100))
    req = required_strategy(ind["cost"], resp_m)
    px, py = STRAT_POINTS[ctx["cur_strategy"]]
    S[13] = float(np.clip(100 - math.hypot(ind["cost"] - px, resp_m - py) * 1.2, 0, 100))
    C[13] = {"Cost pressure (industry)": ind["cost"], "Local-responsiveness pressure (market-adjusted)": resp_m,
             "Strategy this market demands": req, "Your current strategy": ctx["cur_strategy"]}
    N[13] = f"Demands {req.lower()}; you run {ctx['cur_strategy'].lower()}."

    # Ch. 14 Organization
    S[14] = COMPAT[ctx["cur_structure"]][req]
    C[14] = {"Required strategy": req, "Your structure": ctx["cur_structure"], "Architecture fit": S[14],
             "Ideal structure": ARCH[req]["Structure"]}
    N[14] = "Architecture matches." if S[14] >= 70 else "Architecture change needed before scaling."

    S = {k: float(np.clip(v, 0, 100)) for k, v in S.items()}
    extras = dict(dist=dist, resp_m=resp_m, required=req, fta=fta, dep=dep, vol=vol, hedge=hedge, eff_tariff=eff_t)
    return dict(scores=S, comps=C, notes=N, extras=extras)


RESULTS = {m: compute_market(D[m], m, ctx) for m in markets}
SCORES_BASE = pd.DataFrame({m: RESULTS[m]["scores"] for m in markets}).T

# Prototype from the Upgrade Lab (read from session state so it can apply app-wide)
PROTO_ON = st.session_state.get("proto_on", False)
PROTO_CH = st.session_state.get("proto_ch", 4)
PROTO_W = st.session_state.get("proto_w", 0.3)
PROTO_NAME = st.session_state.get("proto_name", "")


def apply_proto(scores):
    out = scores.copy()
    for m in out.index:
        v = st.session_state.get(f"proto_val_{m}", 50)
        out.loc[m, PROTO_CH] = (1 - PROTO_W) * out.loc[m, PROTO_CH] + PROTO_W * v
    return out


SCORES = apply_proto(SCORES_BASE) if PROTO_ON else SCORES_BASE

mult = MOTIVES[motive]
WEIGHTS = {k: user_w[k] * mult.get(k, 1.0) for k in CHAPTERS}
if sum(WEIGHTS.values()) == 0:
    WEIGHTS = {k: 1.0 for k in CHAPTERS}


def composite(scores, w=None):
    w = pd.Series(w or WEIGHTS)
    return (scores[w.index] * w).sum(axis=1) / w.sum()


def stage_scores(scores):
    return pd.DataFrame({s: scores[v["ch"]].mean(axis=1) for s, v in STAGES.items()})


INDEX = composite(SCORES)


# =========================================================
# Financial case (Ch. 8, 10, 11, 12)
# =========================================================
def fin_case(c, name, ctx, p):
    h = ctx["home"]
    dep, vol, _ = fx_profile(c, name, ctx)
    pi_h, pi_0 = c["inflation"] / 100, h["inflation"] / 100
    d = dep / 100
    hurdle = p["wacc"] / 100 + c["crp"] / 100 + 0.25 * (vol / 100) * (1 - p["hedge"])
    g_loc = (1 + p["real_g"] / 100) * (1 + pi_h) - 1
    g_t = pi_0
    hurdle = max(hurdle, g_t + 0.02)
    rows, npv = [], {}
    for path in ["Naive: no FX change", "PPP-expected", "PPP + crisis in year 2"]:
        total = -p["invest"]
        cf_home = 0.0
        for t in range(1, p["H"] + 1):
            cf_loc = p["cf1"] * (1 + g_loc) ** (t - 1)
            fx = 1.0 if path.startswith("Naive") else (1 + d) ** (-t)
            if path.startswith("PPP + crisis") and t >= 2:
                hit = p["crisis"]
                fx *= 1 - hit * (1 - p["hedge"]) if t <= 3 else 1 - hit  # forwards cover only the near term
            cf_home = cf_loc * fx
            total += cf_home / (1 + hurdle) ** t
            rows.append(dict(Year=t, Path=path, CF=cf_home))
        tv = cf_home * (1 + g_t) / (hurdle - g_t)
        total += tv / (1 + hurdle) ** p["H"]
        npv[path] = total
    return dict(dep=dep, vol=vol, hurdle=hurdle * 100, npv=npv, df=pd.DataFrame(rows))


# =========================================================
# Entry modes (Ch. 2, 4, 7, 8, 13) and verdict
# =========================================================
def entry_modes(c, res, ctx, commitment="staged"):
    ind, ex, S = ctx["ind"], res["extras"], res["scores"]
    eff_pref = ex["eff_tariff"] * (0.2 if ex["fta"] else 1.0)
    T = scale(eff_pref, 0, 25) / 100                      # trade barrier faced by exports (Ch. 7, 9)
    L = ex["resp_m"] / 100                                 # local-responsiveness pressure (Ch. 13)
    CD = ex["dist"] / 100                                  # cultural distance (Ch. 4)
    R = float(np.clip(c["fdi_restrict"] * (0.5 + ind["regulated"] / 100) / 0.35, 0, 1))  # FDI restriction (Ch. 8)
    K = ctx["capital"] / 100
    Cc = 1 - K
    Sp = ctx["speed"] / 100
    Rk = 1 - S[2] / 100                                    # institutional risk (Ch. 2)
    IP = ind["ip"] / 100
    IPrisk = IP * (1 - c["rule_law"] / 100)                # dissipation risk if know-how is licensed (Ch. 8)
    depth = scale(c["mcap_gdp"], 5, 150) / 100             # availability of acquisition targets (Ch. 12)
    g = ind["goods"]
    LOC = S[6] / 100 * g                                   # location economies for producing goods locally (Ch. 6, 13)
    modes = {
        "Exporting": 0.20 * g + 0.35 * (1 - T) + 0.15 * (1 - L) + 0.15 * Rk + 0.15 * Cc,
        "Licensing / franchising": 0.30 * (1 - IPrisk) + 0.20 * Cc + 0.20 * Sp + 0.15 * L + 0.15 * (1 - IP),
        "Strategic alliance": 0.30 * CD + 0.20 * L + 0.20 * Sp + 0.15 * (1 - IPrisk) + 0.15 * Cc,
        "Joint venture": 0.25 * R + 0.25 * CD + 0.20 * L + 0.15 * Rk + 0.15 * K,
        "Greenfield wholly owned subsidiary": 0.15 * IP + 0.15 * K + 0.30 * T + 0.15 * (1 - R) + 0.10 * (1 - Rk) + 0.15 * LOC,
        "Acquisition": 0.15 * IP + 0.20 * K + 0.20 * Sp + 0.15 * (1 - R) + 0.15 * (1 - CD) + 0.15 * depth,
    }
    modes = {k: v * 100 for k, v in modes.items()}
    # Carry the commitment verdict into the mode choice (investment stage -> execution stage)
    adj = {"high": {"Greenfield wholly owned subsidiary": 8, "Acquisition": 8, "Joint venture": 3, "Exporting": -8, "Licensing / franchising": -8},
           "staged": {"Joint venture": 5, "Strategic alliance": 5},
           "low": {"Exporting": 8, "Licensing / franchising": 8, "Greenfield wholly owned subsidiary": -10, "Acquisition": -10, "Joint venture": -5}}
    for k, a in adj.get(commitment, {}).items():
        modes[k] += a
    return pd.Series({k: round(float(np.clip(v, 0, 100)), 1) for k, v in modes.items()}).sort_values(ascending=False)


def commitment_of(v):
    if v.startswith("GO: high"):
        return "high"
    if v.startswith("GO: staged"):
        return "staged"
    return "low"


def verdict(idx, S, npv_ppp, npv_crisis):
    gates, veto = [], False
    if S[5] < effective_thr:
        if ethics_policy == "Hard veto":
            veto = True
            gates.append("⛔ Ethics red line breached (Ch. 5)")
        elif ethics_policy == "Enhanced due diligence required":
            gates.append("⚠️ Enhanced ethics and ESG due diligence required (Ch. 5)")
        else:
            gates.append("ℹ️ Ethics score below threshold, advisory only (Ch. 5)")
    if S[2] < 35:
        gates.append("⚠️ Weak institutions: staged commitment only (Ch. 2)")
    if S[8] < 40:
        gates.append("⚠️ Restrictive FDI regime: local partner likely required (Ch. 8)")
    if S[11] < 40:
        gates.append("⚠️ Fragile monetary regime: stress-test FX before committing (Ch. 11)")
    blocking = any(g.startswith("⚠️") for g in gates)
    if veto:
        return "NO-GO", "Breaches the firm's ethics red line.", gates
    if idx < 45:
        return "NO-GO for now", "Composite readiness is too low. Revisit if conditions change.", gates
    if npv_ppp < 0:
        return "NOT YET: low-commitment entry", "Strategic fit exists, but the project does not clear the hurdle rate. Use exporting or licensing to buy information.", gates
    if idx >= 65 and npv_crisis >= 0 and not blocking:
        return "GO: high commitment", "Strong readiness and value survives an FX crisis.", gates
    return "GO: staged or partnered", "Positive value, but gates or crisis sensitivity argue for staging or a partner.", gates


# =========================================================
# Header
# =========================================================
st.markdown('<div class="hero">🌍 Global Market Entry Decision Lab</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub">{company} ({industry}, based in {home}) is deciding whether, where and how to invest. '
            'Fourteen chapter lenses feed one decision. Each group owns one lens: reflect on it, find what the app gets wrong, and upgrade it.</div>',
            unsafe_allow_html=True)
if shock != "None":
    st.warning(f"Scenario active: **{shock}** → {shock_target}. {SHOCKS[shock]}")
if PROTO_ON:
    st.info(f"Upgrade prototype active: **{PROTO_NAME or 'custom indicator'}** blended into {ch_label(PROTO_CH)} at {PROTO_W:.0%}.")

tabs = st.tabs(["🧭 Decision map", "🔍 Chapter lenses", "💱 Financial case", "🏛️ Boardroom", "🛠️ Upgrade lab", "👩‍🏫 Instructor"])

# =========================================================
# Tab 1: Decision map
# =========================================================
with tabs[0]:
    cols = st.columns(5)
    for col, (stage, v) in zip(cols, STAGES.items()):
        chs = ", ".join(f"Ch. {k}" for k in v["ch"])
        col.markdown(f"<div class='stage'><b>{stage}</b><br><span class='q'>{v['q']}</span><br><br>{chs}</div>",
                     unsafe_allow_html=True)

    st.markdown("#### How every chapter reads each market")
    st.caption("0 = unfavourable, 100 = favourable for investing. Hover a cell for detail; open the Chapter lenses tab for the method.")
    long = SCORES.copy()
    long.columns = [ch_col(k) for k in long.columns]
    long = long.reset_index().rename(columns={"index": "Market"}).melt("Market", var_name="Chapter", value_name="Score")
    long["Score"] = long["Score"].round(0)
    order = [ch_col(k) for k in CHAPTERS]
    base = alt.Chart(long).encode(x=alt.X("Chapter:N", sort=order, title=None, axis=alt.Axis(labelAngle=-40)),
                                  y=alt.Y("Market:N", title=None))
    heat = base.mark_rect().encode(color=alt.Color("Score:Q", scale=alt.Scale(domain=[0, 100], scheme="redyellowgreen"), legend=None),
                                   tooltip=["Market", "Chapter", "Score"])
    text = base.mark_text(fontSize=12).encode(text="Score:Q")
    show_chart((heat + text).properties(height=60 + 42 * len(markets)))

    st.markdown("#### Composite readiness")
    st.caption(f"Weighted average of chapter scores. Motive '{motive}' raises the weight on "
               + ", ".join(f"Ch. {k}" for k in mult) + ".")
    summary = stage_scores(SCORES).round(1)
    summary.insert(0, "Readiness index", INDEX.round(1))
    summary = summary.sort_values("Readiness index", ascending=False)
    cfg = {c: st.column_config.ProgressColumn(c, min_value=0, max_value=100, format="%.0f") for c in summary.columns}
    show_df(summary, column_config=cfg)
    leader = summary.index[0]
    st.success(f"Readiness leader: **{leader}** ({summary.iloc[0]['Readiness index']:.0f}/100). "
               "Readiness is not the decision: the Boardroom adds ethics gates, the financial case and entry mode.")

    with st.expander("How groups use this app across the term"):
        st.markdown(
            "1. **Reflect.** Present what your chapter teaches, mapped to its learning outcomes.\n"
            "2. **Diagnose.** Open your chapter lens. Which outcomes are modeled, partial, or missing? Where is the logic wrong?\n"
            "3. **Upgrade.** Propose a change: a new indicator, a gate, a shock, a better data source, or a different formula.\n"
            "4. **Test.** Prototype it in the Upgrade lab and show whether the investment decision changes.\n"
            "5. **Present.** Reflection plus upgrade. Strong upgrades are built into the next version of the app.")

# =========================================================
# Tab 2: Chapter lenses
# =========================================================
with tabs[1]:
    k = st.selectbox("Chapter", list(CHAPTERS), format_func=ch_label, key="lens_ch")
    st.markdown(f"### {ch_label(k)}")
    st.caption(f"Decision stage: {CH_STAGE[k]} · Current weight in the index: {WEIGHTS[k]:.2f}")

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("**Learning outcomes and how the app uses them**")
        for code, text, status in CHAPTERS[k]["los"]:
            st.markdown(f"<span class='pill pill-{status}'>{status}</span> **{code}** {text}", unsafe_allow_html=True)
    with right:
        st.markdown("**What the app currently assumes**")
        st.markdown(METHODS[k])

    sc = SCORES[[k]].rename(columns={k: "Score"}).reset_index().rename(columns={"index": "Market"})
    bar = alt.Chart(sc).mark_bar().encode(
        x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100])), y=alt.Y("Market:N", sort="-x", title=None),
        color=alt.Color("Score:Q", scale=alt.Scale(domain=[0, 100], scheme="redyellowgreen"), legend=None),
        tooltip=["Market", alt.Tooltip("Score:Q", format=".1f")])
    show_chart(bar.properties(height=40 + 36 * len(markets)))

    comp_tbl = pd.DataFrame({m: {kk: fmt(v) for kk, v in RESULTS[m]["comps"][k].items()} for m in markets})
    comp_tbl.loc["Chapter score"] = [fmt(SCORES.loc[m, k]) for m in markets]
    show_df(comp_tbl)
    for m in markets:
        st.caption(f"**{m}:** {RESULTS[m]['notes'][k]}")

    st.markdown("**Reflection → upgrade prompts for this chapter's group**")
    for i, p in enumerate(PROMPTS[k], 1):
        st.markdown(f"{i}. {p}")
    gaps = [f"{code}" for code, _, s in CHAPTERS[k]["los"] if s == GAP]
    if gaps:
        st.info("Unmodeled learning outcomes (upgrade targets): " + ", ".join(gaps))

# =========================================================
# Tab 3: Financial case
# =========================================================
with tabs[2]:
    st.markdown(f"### Financial case: {focus}")
    st.caption("Ch. 8 (commitment), Ch. 10 (PPP, hedging, exposure), Ch. 11 (regime), Ch. 12 (cost of capital). "
               f"Values in {ctx['home']['currency']} millions.")
    c_f = D[focus]
    a, b, c3, d4 = st.columns(4)
    invest = a.number_input("Up-front investment", 1.0, 1000.0, 50.0, 5.0)
    cf1 = b.number_input("Year-1 operating cash flow (at today's FX)", 0.0, 500.0, 7.0, 0.5)
    real_g = c3.slider("Real growth of cash flows, %", -2.0, 10.0, float(min(max(c_f["growth"], -2), 10)), 0.5, key=f"rg_{focus}")
    H = d4.slider("Horizon, years", 5, 15, 10)
    e, f, g5 = st.columns(3)
    wacc = e.slider("Home-market WACC, %", 4.0, 15.0, 8.0, 0.5)
    hedge_share = f.slider("Share of near-term cash flows hedged with forwards", 0.0, 1.0, 0.5, 0.05)
    crisis_hit = g5.slider("Crisis depreciation (one-off)", 0.0, 0.6, 0.3, 0.05)
    P = dict(invest=invest, cf1=cf1, real_g=real_g, H=H, wacc=wacc, hedge=hedge_share, crisis=crisis_hit)

    FIN = {}
    for m in markets:
        P_m = dict(P, real_g=real_g if m == focus else float(min(max(D[m]["growth"], -2), 10)))
        FIN[m] = fin_case(D[m], m, ctx, P_m)
    fc = FIN[focus]

    m1, m2, m3 = st.columns(3)
    m1.metric("Expected depreciation (PPP)", f"{fc['dep']:.1f}% / yr")
    m2.metric("FX volatility vs home", f"{fc['vol']:.1f}%")
    m3.metric("Hurdle rate", f"{fc['hurdle']:.1f}%", help="WACC + country risk premium + premium for unhedged FX volatility")
    n1, n2, n3 = st.columns(3)
    for col, path in zip([n1, n2, n3], fc["npv"]):
        col.metric(f"NPV, {path}", f"{fc['npv'][path]:,.1f}")

    line = alt.Chart(fc["df"]).mark_line(point=True).encode(
        x=alt.X("Year:O"), y=alt.Y("CF:Q", title=f"Cash flow, {ctx['home']['currency']} m"), color=alt.Color("Path:N", title=None),
        tooltip=["Year", "Path", alt.Tooltip("CF:Q", format=".2f")])
    show_chart(line.properties(height=300))

    st.markdown(
        "**Reading the paths.** Local cash flows grow with host inflation. The naive path converts them at today's rate and "
        "overstates value; relative PPP says high inflation is eaten by depreciation. In the crisis path, forwards protect only "
        "the hedged share of the next two years: hedging handles **transaction** exposure, while the permanent loss is "
        "**economic** exposure, which only operational choices (local sourcing, pricing power, local debt) can manage.")

    st.markdown("**Same project in every candidate market**")
    ft = pd.DataFrame({m: {"Hurdle, %": FIN[m]["hurdle"], "PPP depreciation, %/yr": FIN[m]["dep"],
                           "NPV naive": FIN[m]["npv"]["Naive: no FX change"], "NPV PPP": FIN[m]["npv"]["PPP-expected"],
                           "NPV crisis": FIN[m]["npv"]["PPP + crisis in year 2"]} for m in markets}).T.round(1)
    show_df(ft.sort_values("NPV PPP", ascending=False))
    st.caption("Other markets use their own real growth rate; the focus market uses the slider. A teaching model, not a valuation.")

# =========================================================
# Tab 4: Boardroom
# =========================================================
with tabs[3]:
    st.markdown("### Boardroom decision")
    rows, MODES = [], {}
    for m in markets:
        S_m = SCORES.loc[m].to_dict()
        v, why, gates = verdict(INDEX[m], S_m, FIN[m]["npv"]["PPP-expected"], FIN[m]["npv"]["PPP + crisis in year 2"])
        MODES[m] = entry_modes(D[m], RESULTS[m], ctx, commitment_of(v))
        rows.append({"Market": m, "Readiness": round(INDEX[m], 1), "NPV PPP": round(FIN[m]["npv"]["PPP-expected"], 1),
                     "NPV crisis": round(FIN[m]["npv"]["PPP + crisis in year 2"], 1), "Verdict": v,
                     "Best entry mode": MODES[m].index[0], "Strategy demanded": RESULTS[m]["extras"]["required"],
                     "Gates": len(gates)})
    board = pd.DataFrame(rows).sort_values(["Readiness"], ascending=False)
    show_df(board, hide_index=True,
            column_config={"Readiness": st.column_config.ProgressColumn("Readiness", min_value=0, max_value=100, format="%.0f")})

    S_f = SCORES.loc[focus].to_dict()
    v, why, gates = verdict(INDEX[focus], S_f, FIN[focus]["npv"]["PPP-expected"], FIN[focus]["npv"]["PPP + crisis in year 2"])
    req = RESULTS[focus]["extras"]["required"]
    best_mode = MODES[focus].index[0]
    st.markdown(
        f"<div class='verdict'><b>{focus}: {v}</b><br>{why}<br><br>"
        f"Readiness {INDEX[focus]:.0f}/100. NPV (PPP) {FIN[focus]['npv']['PPP-expected']:,.1f}; "
        f"NPV (crisis) {FIN[focus]['npv']['PPP + crisis in year 2']:,.1f}. Best-fit entry mode: <b>{best_mode}</b>. "
        f"Strategy demanded: <b>{req}</b>.</div>", unsafe_allow_html=True)
    for gte in gates:
        st.markdown(gte)

    l, r = st.columns(2)
    with l:
        st.markdown("**Entry-mode fit**")
        md = MODES[focus].reset_index()
        md.columns = ["Mode", "Fit"]
        show_chart(alt.Chart(md).mark_bar().encode(x=alt.X("Fit:Q", scale=alt.Scale(domain=[0, 100])),
                                                   y=alt.Y("Mode:N", sort="-x", title=None), tooltip=["Mode", "Fit"]).properties(height=230))
        st.caption("Draws on Ch. 7 (tariff-jumping), Ch. 8 (internalization: when to own rather than license), Ch. 2 (IP protection), "
                   "Ch. 4 (distance favours partners), Ch. 6 (location economies), Ch. 12 (acquisition targets) and Ch. 13 (responsiveness). "
                   "The verdict's commitment level tilts the ranking toward or away from ownership.")
    with r:
        st.markdown(f"**Organizational architecture for {req.lower()} (Ch. 14)**")
        arch = pd.DataFrame({"Recommended": ARCH[req]})
        show_df(arch)
        if S_f[14] < 70:
            st.caption(f"Your current structure ({cur_structure.lower()}) fits at {S_f[14]:.0f}/100. "
                       "Changing it means unfreezing, moving and refreezing structure, controls, incentives and culture (14-4).")

    tensions = []
    if board.iloc[0]["Market"] != focus:
        tensions.append(f"The readiness leader is **{board.iloc[0]['Market']}**, but your focus is **{focus}**. Defend the choice.")
    if gates and best_mode in ("Greenfield wholly owned subsidiary", "Acquisition") and any("partner" in g for g in gates):
        tensions.append("The FDI regime points to a partner, but entry-mode fit points to full ownership.")
    if FIN[focus]["npv"]["Naive: no FX change"] > 0 > FIN[focus]["npv"]["PPP-expected"]:
        tensions.append("The case is positive only if you ignore PPP. That is money illusion, not value.")
    if S_f[13] < 50:
        tensions.append(f"This market demands {req.lower()}, far from your current {cur_strategy.lower()} strategy.")
    if INDEX[focus] >= 65 and FIN[focus]["npv"]["PPP-expected"] < 0:
        tensions.append("High readiness but negative NPV: a good country can still be a bad project at this price.")
    for t in tensions:
        st.warning(t)

    st.markdown("#### 60-second board pitch")
    pitch = st.text_area("Your recommendation", height=150, key="board_pitch",
                         placeholder="We recommend ______ in ______ because… The chapter that most shaped our decision was… "
                                     "The biggest risk is… We enter through ______ and organize as ______ because…")
    cc1, cc2 = st.columns(2)
    confidence = cc1.slider("Confidence in the recommendation", 0, 100, 70, key="board_conf")
    swing = cc2.selectbox("Which chapter's evidence would most change your mind?", list(CHAPTERS), format_func=ch_label, key="board_swing")

    memo = [f"# Board memo: {company}", f"_{datetime.now():%Y-%m-%d %H:%M}_", "",
            f"**Industry:** {industry}  ", f"**Home market:** {home}  ", f"**FDI motive:** {motive}  ",
            f"**Scenario:** {shock} ({shock_target})  ", f"**Ethics policy:** {ethics_policy}, threshold {effective_thr}", "",
            f"## Recommendation for {focus}: {v}", why, ""]
    memo += [f"- {gte}" for gte in gates] + [""]
    memo += [f"Readiness {INDEX[focus]:.1f}/100. Hurdle {FIN[focus]['hurdle']:.1f}%. "
             f"NPV naive {FIN[focus]['npv']['Naive: no FX change']:.1f}, PPP {FIN[focus]['npv']['PPP-expected']:.1f}, "
             f"crisis {FIN[focus]['npv']['PPP + crisis in year 2']:.1f}.", "",
             f"Entry mode: {best_mode}. Strategy demanded: {req}. Recommended structure: {ARCH[req]['Structure']}.", "",
             "## Chapter scores", "| Chapter | Score |", "|---|---|"]
    memo += [f"| {ch_label(kk)} | {S_f[kk]:.0f} |" for kk in CHAPTERS]
    memo += ["", "## All candidate markets", "| " + " | ".join(board.columns) + " |", "|" + "---|" * len(board.columns)]
    memo += ["| " + " | ".join(str(x) for x in row) + " |" for row in board.itertuples(index=False)]
    memo += ["", "## Pitch", pitch or "(not written)", "", f"Confidence: {confidence}/100. Swing chapter: {ch_label(swing)}."]
    if tensions:
        memo += ["", "## Tensions acknowledged"] + [f"- {t}" for t in tensions]
    if PROTO_ON:
        memo += ["", f"_Prototype active: {PROTO_NAME} in {ch_label(PROTO_CH)} at {PROTO_W:.0%}._"]
    st.download_button("Download board memo (Markdown)", "\n".join(memo).encode(), f"board_memo_{focus}.md", "text/markdown")

# =========================================================
# Tab 5: Upgrade lab
# =========================================================
PROPOSAL_FILE = Path(__file__).with_name("bus346_proposals.csv")
PROPOSAL_COLS = ["Submitted", "Group", "Chapter", "LOs", "Type", "Problem", "Proposed change", "Data source", "Decision impact", "Test"]
if "proposals" not in st.session_state:
    try:
        st.session_state.proposals = pd.read_csv(PROPOSAL_FILE) if PROPOSAL_FILE.exists() else pd.DataFrame(columns=PROPOSAL_COLS)
    except Exception:
        st.session_state.proposals = pd.DataFrame(columns=PROPOSAL_COLS)

with tabs[4]:
    st.markdown("### Upgrade lab")
    st.caption("Turn your reflection into a concrete change, then test whether it changes the decision.")

    st.markdown("#### 1. Prototype a new indicator")
    p1, p2, p3 = st.columns([1.3, 1.3, 1])
    p1.text_input("Indicator name", "e.g., Language distance", key="proto_name")
    p2.selectbox("Blend into chapter", list(CHAPTERS), format_func=ch_label, key="proto_ch", index=3)
    p3.slider("Share of chapter score", 0.05, 0.8, 0.3, 0.05, key="proto_w")
    st.caption("Score each market 0–100 (100 = most favourable for investing). Note the source you would use for real values.")
    vcols = st.columns(min(len(markets), 4))
    for i, m in enumerate(markets):
        vcols[i % len(vcols)].slider(m, 0, 100, 50, key=f"proto_val_{m}")
    st.toggle("Apply this prototype across the whole app", key="proto_on")

    trial = apply_proto(SCORES_BASE)
    before, after = composite(SCORES_BASE), composite(trial)
    imp = pd.DataFrame({"Readiness before": before.round(1), "Readiness after": after.round(1)})
    imp["Change"] = (imp["Readiness after"] - imp["Readiness before"]).round(1)
    imp["Rank before"] = before.rank(ascending=False).astype(int)
    imp["Rank after"] = after.rank(ascending=False).astype(int)
    vb, va = {}, {}
    for m in markets:
        vb[m] = verdict(before[m], SCORES_BASE.loc[m].to_dict(), FIN[m]["npv"]["PPP-expected"], FIN[m]["npv"]["PPP + crisis in year 2"])[0]
        va[m] = verdict(after[m], trial.loc[m].to_dict(), FIN[m]["npv"]["PPP-expected"], FIN[m]["npv"]["PPP + crisis in year 2"])[0]
    imp["Verdict before"] = pd.Series(vb)
    imp["Verdict after"] = pd.Series(va)
    show_df(imp.sort_values("Readiness after", ascending=False))
    changed = [m for m in markets if vb[m] != va[m]]
    leader_b, leader_a = before.idxmax(), after.idxmax()
    if leader_b != leader_a or changed:
        msg = []
        if leader_b != leader_a:
            msg.append(f"the readiness leader moves from {leader_b} to {leader_a}")
        if changed:
            msg.append("verdicts change for " + ", ".join(changed))
        st.success("Your upgrade changes the decision: " + "; ".join(msg) + ".")
    else:
        st.info("Your upgrade shifts scores but not the decision. Is that a finding (the app was robust) or a sign the weight is too small?")

    st.markdown("#### 2. Submit the upgrade proposal")
    with st.form("proposal", clear_on_submit=True):
        q1, q2, q3 = st.columns(3)
        grp = q1.text_input("Group")
        pch = q2.selectbox("Chapter", list(CHAPTERS), format_func=ch_label)
        ptype = q3.selectbox("Upgrade type", ["New indicator", "Replace data with sourced values", "New gate or rule",
                                              "New scenario shock", "Change weights or formula", "New visual or explanation"])
        los = st.multiselect("Learning outcomes targeted", [f"{c_} {t}" for kk in CHAPTERS for c_, t, _ in CHAPTERS[kk]["los"]])
        prob = st.text_area("What the app gets wrong or misses now", height=80)
        change = st.text_area("Proposed change (be specific enough to code)", height=80)
        src = st.text_input("Data source(s)")
        impact = st.text_area("How it changes the investment decision", height=70)
        test = st.text_input("How you tested it (prototype result, example market)")
        if st.form_submit_button("Submit proposal"):
            new = pd.DataFrame([{"Submitted": datetime.now().strftime("%Y-%m-%d %H:%M"), "Group": grp, "Chapter": ch_label(pch),
                                 "LOs": "; ".join(x.split(" ")[0] for x in los), "Type": ptype, "Problem": prob,
                                 "Proposed change": change, "Data source": src, "Decision impact": impact, "Test": test}])
            st.session_state.proposals = pd.concat([st.session_state.proposals, new], ignore_index=True)
            try:
                st.session_state.proposals.to_csv(PROPOSAL_FILE, index=False)
            except Exception:
                pass
            st.success("Proposal submitted. Download the log below to keep a copy.")

    st.markdown("#### 3. Proposal log")
    show_df(st.session_state.proposals, hide_index=True)
    st.download_button("Download proposals (CSV)", st.session_state.proposals.to_csv(index=False).encode(),
                       "bus346_proposals.csv", "text/csv")
    st.caption("On hosted deployments the server file may reset; the downloaded CSV is the durable record.")

# =========================================================
# Tab 6: Instructor
# =========================================================
with tabs[5]:
    st.markdown("### Instructor view")

    st.markdown("#### Learning-outcome coverage")
    cov = pd.DataFrame([{"Chapter": ch_col(kk), "Status": s} for kk in CHAPTERS for _, _, s in CHAPTERS[kk]["los"]])
    cov_chart = alt.Chart(cov).mark_bar().encode(
        y=alt.Y("Chapter:N", sort=[ch_col(kk) for kk in CHAPTERS], title=None), x=alt.X("count():Q", title="Learning outcomes"),
        color=alt.Color("Status:N", scale=alt.Scale(domain=[MOD, PAR, GAP], range=["#2e9e5a", "#e0a82e", "#d24b4b"])),
        order=alt.Order("Status:N"))
    show_chart(cov_chart.properties(height=380))
    tot = cov["Status"].value_counts()
    st.caption(f"{tot.get(MOD, 0)} modeled, {tot.get(PAR, 0)} partial, {tot.get(GAP, 0)} gaps across "
               f"{len(cov)} learning outcomes. Gaps are the natural upgrade targets for each group.")

    st.markdown("#### Group presentation structure (about 15 minutes)")
    st.markdown(
        "1. **Reflection (6 min).** The chapter's key ideas mapped to its learning outcomes, with one current real-world example.\n"
        "2. **Diagnosis (3 min).** How the app uses the chapter today: what is modeled, partial, missing or wrong.\n"
        "3. **Upgrade (4 min).** The proposed change, its theory, its data source, and the Upgrade lab result.\n"
        "4. **Decision consequence (2 min).** Which market or entry mode changes, and whether that change is defensible.")

    st.markdown("#### Suggested rubric")
    rubric = pd.DataFrame([
        ["Reflection", "30%", "Accurate, covers the learning outcomes, connects to a current example"],
        ["Diagnosis", "20%", "Uses the coverage map; identifies a real weakness, not a cosmetic one"],
        ["Upgrade proposal", "30%", "Grounded in chapter theory, operationalized with a measurable and sourced indicator"],
        ["Test and consequence", "20%", "Prototype shown; explains whether and why the decision changes; states limitations"],
    ], columns=["Component", "Weight", "What earns full marks"])
    show_df(rubric, hide_index=True)

    st.markdown("#### Live session moves")
    st.markdown(
        "- Before a group presents, set the scenario shock that stresses their chapter and ask the class to predict the verdict change.\n"
        "- Switch the home market (Canada vs UAE vs Singapore) to show that cultural distance, PPP and FTAs are relative, not country traits.\n"
        "- Set ethics policy to *Hard veto* and ask who would override it, and on which philosophical grounds (Ch. 5).\n"
        "- Assess reasoning and consistency, not whether a team picks the top-ranked market.")

    with st.expander("Country data in use (after any scenario shock)"):
        show_df(pd.DataFrame(D).T)
    with st.expander("Known simplifications (good material for group critiques)"):
        st.markdown(
            "- All scores are linear rescalings with judgement-based bounds and weights.\n"
            "- FX volatility assumes currencies move independently of each other.\n"
            "- PPP holds smoothly every year; real exchange-rate swings are ignored except in the crisis path.\n"
            "- The country risk premium is added to the discount rate rather than modeled in cash flows.\n"
            "- Industry parameters are stylized averages; firms within an industry differ.\n"
            "- Entry-mode fit is a heuristic synthesis of chapter theory, not an estimated model.")

st.divider()
st.caption("BUS 346 Global Business Environment · Illustrative data for teaching · Not investment advice")
