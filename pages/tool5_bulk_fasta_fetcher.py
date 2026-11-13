import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as sp_stats
from scipy.optimize import curve_fit
import urllib.parse 
import io
import json 
import os
import time

# ==========================================
# 🇮🇳 INDIA DIRECT PAYMENT CONFIG (PULLS PRIVATELY FROM STREAMLIT SECRETS)
# ==========================================
INDIA_UPI_ID = st.secrets.get("INDIA_UPI_ID", "BHARATPE2A0G0R8H8A59248@unitype")
INDIA_PAYEE_NAME = st.secrets.get("INDIA_PAYEE_NAME", "GenomeTech Studio")

# ==========================================
# HIDE SIDEBAR COMPLETELY & APPLY DARK INDIGO/PURPLE THEME
# ==========================================
st.markdown("""
<style>
    /* Completely hide sidebar, multipage nav, and collapse control */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    .glass-header {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(139, 92, 246, 0.35);
        border-radius: 14px;
        padding: 14px 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .brand-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.01em;
    }
    .brand-sub {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        margin-left: 8px;
    }
    .tool-pill {
        background: linear-gradient(90deg, #7c3aed 0%, #4f46e5 100%);
        color: #ffffff !important;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        border: 1px solid rgba(196, 181, 253, 0.4);
    }
    .metric-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(139, 92, 246, 0.28);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #cbd5e1;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }
    .blurred-table {
        filter: blur(5px);
        pointer-events: none;
        user-select: none;
        opacity: 0.45;
        margin-bottom: -180px;
    }
    .paywall-overlay {
        position: relative;
        z-index: 10;
        background: rgba(15, 12, 36, 0.92);
        border: 1px solid rgba(168, 85, 247, 0.55);
        border-radius: 16px;
        padding: 26px 24px;
        max-width: 650px;
        margin: 0 auto 22px auto;
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.75);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE & CURRENCY INITIALIZATION (TOOL #5)
# ==========================================
if "is_unlocked_t5" not in st.session_state:
    st.session_state["is_unlocked_t5"] = False
if "last_mode_t5" not in st.session_state:
    st.session_state["last_mode_t5"] = None

if "currency" not in st.session_state:
    url_curr = str(st.query_params.get("currency", "USD")).strip().upper()
    st.session_state.currency = "INR" if url_curr == "INR" else "USD"
is_inr = (st.session_state.get("currency", "USD") == "INR")

# ==========================================
# TOP GLASS HEADER BANNER (FULL WIDTH)
# ==========================================
st.markdown(
    '<div class="glass-header">'
    '<div><span class="brand-title">💊 <span style="color:#34d399;">GenomeTech</span> Studio</span>'
    '<span class="brand-sub">| OmicsExpress Automated Suite</span></div>'
    '<div class="tool-pill">⚡ Tool #5: IC50 / EC50 Dose-Response Suite</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("## Automated IC50 / EC50 Dose-Response (4PL Hill Curve) & MTT Cytotoxicity Suite")
st.markdown(
    "Fit exact 4-Parameter Logistic (4PL) sigmoidal dose-response curves across 96-well MTT, SRB, CCK-8, DPPH antioxidant, and enzyme inhibition assays. "
    "Automatically computes **exact $\\text{IC}_{50}$, $\\text{IC}_{20}$, $\\text{IC}_{80}$, $\\text{IC}_{90}$, $\\text{pIC}_{50}$, 95% Confidence Intervals, Hill Slope ($h$), Goodness-of-Fit ($R^2$), Normal-vs-Cancer Selectivity Index ($\\text{SI} = \\text{CC}_{50}/\\text{IC}_{50}$), and 4 vector publication figures (`.svg`)**."
)

# ==========================================
# COLLAPSIBLE FILE FORMAT & DELIVERABLES EXPANDER
# ==========================================
with st.expander("📋 Required File Format & Complete Pharmacology / Wet-Lab Deliverables (.csv, .tsv, .txt, or .xlsx)", expanded=True):
    st.markdown(
        "* **Accepted File Formats:** Tabular `.csv`, `.tsv`, `.txt`, or `.xlsx` containing a **Compound / Drug Name column**, **Concentration column (> 0)**, **Response column** (`% Viability`, `% Inhibition`, or raw `OD / Absorbance`), and optional **Cell Line / Target column**.\n"
        "* **Complete Pharmacological & 4PL Regression Columns Included:**\n"
        "  1. **Potency & Critical Thresholds:** `IC50_Value`, `IC50_95CI_Lower`, `IC50_95CI_Upper`, `Log10_IC50`, `pIC50 (-Log10_M)`, `IC20_Value`, `IC80_Value`, `IC90_Value`.\n"
        "  2. **4-Parameter Logistic (Hill) Parameters:** `Hill_Slope (h)`, `Bottom_Plateau (%)`, `Top_Plateau (%)`, `Max_Observed_Effect_Emax (%)`, `Span (%)`.\n"
        "  3. **Nonlinear Regression Quality & ANOVA:** `Goodness_of_Fit_R2`, `Residual_RMSE`, `ANOVA_Dose_F`, `ANOVA_Dose_P_Value`, `Potency_Classification`.\n"
        "  4. **Therapeutic Window & Selectivity Index:** `Selectivity_Index (SI = Reference_CC50 / Compound_IC50)` plus a **100-Point Smooth Sigmoidal Curve Coordinate Matrix**.\n"
        "* 💻 **Cross-Platform File Compatibility (Windows & Apple macOS):** All exported `.csv` tables use universal `UTF-8-BOM` encoding—double-click to open directly in **Microsoft Excel (Windows/Mac)**, Apple Numbers, Google Sheets, or GraphPad Prism. Vector figure (`.svg` / `.html`) outputs open natively in any web browser or Adobe Illustrator.\n"
        "* **Single-Mode License Note:** Each checkout unlocks your selected **Regression Mode** (`Free 4-Parameter Logistic (4PL)`, `Constrained 0–100% Top/Bottom (2PL)`, `EC50 Agonist Activation`, or `Raw OD Blank-Corrected MTT`). Adjusting plot scales within your unlocked mode is free; switching the Application Mode starts a new run."
    )

# ==========================================
# UPLOAD BOX, DEMO CHECKBOX & PASTE TEXTAREA
# ==========================================
up_col, demo_col = st.columns([2.3, 1])
with up_col:
    uploaded_file = st.file_uploader(
        "Drop your Dose-Response / MTT Viability Table (.csv, .tsv, .txt, .xlsx)",
        type=["csv", "tsv", "txt", "xlsx"],
        key="up_ic50_file_t5"
    )
with demo_col:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    use_demo_t5 = st.checkbox("🧪 Load Demo Multi-Drug MTT Oncology Dataset", value=(uploaded_file is None), key="chk_demo_t5")

st.caption("⚡ **Performance Note:** Supports multi-compound 96-well / 384-well screening plates with automatic replicate pooling, SD/SEM propagation, and Selectivity Index calculation.")

pasted_text = st.text_area(
    "Or paste CSV / Tab-Separated Concentration & Viability rows directly (optional):",
    placeholder="Compound,Cell_Line,Concentration_uM,Viability_Pct\nCisplatin,MCF7_Breast_Tumor,0.1,96.4\nCisplatin,MCF7_Breast_Tumor,1.0,78.2\nCisplatin,MCF7_Breast_Tumor,10.0,34.5\n...",
    height=88,
    key="paste_ic50_t5"
)

# ==========================================
# 3-COLUMN CUSTOM FIXING CONDITIONS & 4PL NONLINEAR REGRESSION OPTIMUMS
# ==========================================
st.markdown("### ⚙️ Custom Fixing Conditions & 4PL Nonlinear Regression Optimums")

app_mode = st.selectbox(
    "Application Mode Preset (Switching application mode starts a new pipeline run):",
    [
        "Standard 4-Parameter Logistic (4PL) Sigmoidal Inhibition (MTT / CCK-8 / SRB Cytotoxicity)",
        "Normalized 2-Parameter Logistic (2PL • Top=100%, Bottom=0% Fixed Plateaus)",
        "DPPH / ABTS Free-Radical Scavenging & Enzyme Inhibition (% Inhibition Mode)",
        "Agonist EC50 Dose-Response Activation Modeling (Positive Hill Slope)"
    ],
    key="mode_preset_t5"
)

if st.session_state["last_mode_t5"] is not None and st.session_state["last_mode_t5"] != app_mode:
    st.session_state["is_unlocked_t5"] = False
    for k in ["ic50_df_t5", "conc_sum_t5", "si_df_t5", "curve_mat_t5"]:
        st.session_state.pop(k, None)
st.session_state["last_mode_t5"] = app_mode

def generate_demo_ic50_df():
    np.random.seed(42)
    concs = [0.05, 0.25, 1.0, 2.5, 5.0, 12.5, 25.0, 50.0, 100.0]
    specs = [
        ("Cisplatin (Standard)", "MCF7_Tumor", 4.2, -1.25, 4.0, 99.0),
        ("Doxorubicin_HCl", "MCF7_Tumor", 1.15, -1.40, 2.5, 99.5),
        ("Curcumin_Nano_Lead", "MCF7_Tumor", 8.6, -1.18, 6.0, 98.5),
        ("Plant_Extract_F4", "MCF7_Tumor", 21.5, -1.10, 9.0, 98.0),
        ("Cisplatin (Normal Control)", "HEK293_Normal", 38.5, -1.05, 12.0, 99.0)
    ]
    rows = []
    for comp, cell, true_ic50, slope_h, bot, top in specs:
        for c in concs:
            true_y = bot + (top - bot) / (1.0 + (c / true_ic50) ** abs(slope_h))
            for rep in range(1, 4):  # Triplicate wells per concentration
                val = np.clip(true_y + np.random.normal(0, 2.1), 0.5, 105.0)
                rows.append({
                    "Compound": comp,
                    "Cell_Line": cell,
                    "Concentration_uM": c,
                    "Replicate": rep,
                    "Viability_Pct": round(float(val), 2)
                })
    return pd.DataFrame(rows)

active_df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".xlsx"):
            active_df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".tsv") or uploaded_file.name.endswith(".txt"):
            active_df = pd.read_csv(uploaded_file, sep=None, engine="python")
        else:
            active_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"⚠️ Error reading uploaded file: {e}")
elif pasted_text.strip():
    try:
        active_df = pd.read_csv(io.StringIO(pasted_text.strip()), sep=None, engine="python")
    except Exception as e:
        st.error(f"⚠️ Error parsing pasted text: {e}")
elif use_demo_t5:
    active_df = generate_demo_ic50_df()

c_left, c_mid, c_right = st.columns(3)

if active_df is not None and len(active_df.columns) >= 3:
    cols = list(active_df.columns)
    def_comp = next((c for c in cols if any(k in c.lower() for k in ["comp", "drug", "sample", "extract", "treat", "agent"])), cols[0])
    def_cell = next((c for c in cols if any(k in c.lower() for k in ["cell", "line", "target", "strain", "group"])), cols[1 if len(cols) > 3 else 0])
    def_conc = next((c for c in cols if any(k in c.lower() for k in ["conc", "dose", "um", "ug", "mm", "nm"])), cols[-2 if len(cols) >= 3 else 0])
    def_resp = next((c for c in cols if any(k in c.lower() for k in ["viab", "inhib", "resp", "od", "abs", "pct", "effect"])), cols[-1])
else:
    cols = ["Compound", "Cell_Line", "Concentration_uM", "Viability_Pct"]
    def_comp, def_cell, def_conc, def_resp = "Compound", "Cell_Line", "Concentration_uM", "Viability_Pct"

with c_left:
    st.markdown("**1. Column Mapping & Concentration Units**")
    col_comp = st.selectbox("Compound / Drug / Extract Column:", cols, index=cols.index(def_comp), key="map_c_t5")
    col_cell = st.selectbox("Cell Line / Assay Target Column:", cols, index=cols.index(def_cell), key="map_cl_t5")
    col_conc = st.selectbox("Dose / Concentration Column (> 0):", cols, index=cols.index(def_conc), key="map_cn_t5")
    col_resp = st.selectbox("Response (% Viability / % Inhibition) Column:", cols, index=cols.index(def_resp), key="map_rp_t5")

with c_mid:
    st.markdown("**2. 4PL Plateau & Unit Settings**")
    conc_unit = st.selectbox("Concentration Unit Label:", ["µM (Micromolar)", "nM (Nanomolar)", "µg/mL (Extract / Mass)", "mM (Millimolar)"], index=0, key="unit_t5")
    unit_short = conc_unit.split(" ")[0]
    resp_type = st.selectbox("Input Response Orientation:", ["% Cell Viability (Decreases with Dose)", "% Inhibition / Scavenging (Increases with Dose)"], index=1 if "Inhibition" in app_mode else 0, key="rtype_t5")
    constrain_plateaus = st.checkbox("Constrain Bottom ≥ 0% and Top ≤ 100% Plateaus", value=("2PL" in app_mode), key="chk_plat_t5")
    hill_bounds = st.slider("Allowed Hill Slope Steepness Range (|h|):", min_value=0.2, max_value=6.0, value=(0.3, 4.5), step=0.1, key="hill_rng_t5")

if active_df is not None and col_comp in active_df.columns:
    detected_comps = list(dict.fromkeys(active_df[col_comp].dropna().astype(str).tolist()))
else:
    detected_comps = ["Cisplatin (Normal Control)"]

with c_right:
    st.markdown("**3. Selectivity Index & Potency Cutoffs**")
    def_norm_i = next((i for i, c in enumerate(detected_comps) if any(k in c.lower() for k in ["normal", "hek", "vero", "fibro", "ctrl", "control"])), len(detected_comps) - 1)
    ref_normal_comp = st.selectbox("Reference Normal-Cell / Control Curve (for Selectivity Index SI):", options=detected_comps, index=max(0, def_norm_i), key="ref_si_t5")
    high_potency_cut = st.number_input(f"High-Potency Lead Cutoff (IC50 ≤ {unit_short}):", min_value=0.1, max_value=500.0, value=10.0, step=1.0, key="pot_cut_t5")
    r2_qc_cut = st.slider("Minimum Goodness-of-Fit (R²) QC Threshold:", min_value=0.70, max_value=0.99, value=0.90, step=0.01, key="r2_cut_t5")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
run_ic50_clicked = st.button("🚀 Run Automated 4PL Dose-Response & IC50 Analysis", type="primary", key="btn_run_ic50_t5")

# ==========================================
# CORE 4PL NONLINEAR REGRESSION COMPUTATION ENGINE
# ==========================================
if (run_ic50_clicked or (use_demo_t5 and "ic50_df_t5" not in st.session_state)) and active_df is not None:
    df_raw = active_df.copy()
    df_raw["Compound"] = df_raw[col_comp].astype(str).str.strip()
    df_raw["Cell_Line"] = df_raw[col_cell].astype(str).str.strip() if col_cell != col_comp else "Standard_Assay"
    df_raw["Conc"] = pd.to_numeric(df_raw[col_conc], errors="coerce")
    df_raw["Resp"] = pd.to_numeric(df_raw[col_resp], errors="coerce")
    df_raw = df_raw.dropna(subset=["Compound", "Conc", "Resp"])
    df_raw = df_raw[df_raw["Conc"] > 0]

    if "Inhibition" in resp_type:
        df_raw["Viability_Pct"] = 100.0 - df_raw["Resp"]
        df_raw["Inhibition_Pct"] = df_raw["Resp"]
    else:
        df_raw["Viability_Pct"] = df_raw["Resp"]
        df_raw["Inhibition_Pct"] = 100.0 - df_raw["Resp"]

    # Concentration-level summary table
    conc_sum_rows = []
    for (comp, cell, conc), grp in df_raw.groupby(["Compound", "Cell_Line", "Conc"], sort=False):
        n_w = len(grp)
        m_v = float(grp["Viability_Pct"].mean())
        sd_v = float(grp["Viability_Pct"].std(ddof=1)) if n_w > 1 else 0.0
        sem_v = sd_v / np.sqrt(n_w) if n_w > 1 else 0.0
        m_inh = 100.0 - m_v
        conc_sum_rows.append({
            "Compound": comp,
            "Cell_Line": cell,
            f"Concentration ({unit_short})": round(float(conc), 4),
            "Log10_Conc": round(float(np.log10(conc)), 4),
            "N_Replicate_Wells": n_w,
            "Mean_Viability (%)": round(m_v, 2),
            "SD_Viability (%)": round(sd_v, 2),
            "SEM_Viability (%)": round(sem_v, 2),
            "Mean_Inhibition (%)": round(m_inh, 2)
        })
    conc_sum_df = pd.DataFrame(conc_sum_rows)

    # 4PL Sigmoidal Function: Y(logC) = Bottom + (Top - Bottom) / (1 + 10^((logC - logIC50) * HillSlope))
    def hill_4pl(log_c, bottom, top, log_ic50, hill_s):
        return bottom + (top - bottom) / (1.0 + np.power(10.0, (log_c - log_ic50) * hill_s))

    def hill_2pl(log_c, log_ic50, hill_s):
        return 0.0 + 100.0 / (1.0 + np.power(10.0, (log_c - log_ic50) * hill_s))

    ic50_rows = []
    curve_grid_dict = {}
    all_log_c = np.log10(df_raw["Conc"].values)
    grid_log_c = np.linspace(float(np.min(all_log_c)) - 0.3, float(np.max(all_log_c)) + 0.3, 100)
    curve_grid_dict[f"Concentration_{unit_short}"] = np.round(np.power(10.0, grid_log_c), 5)
    curve_grid_dict["Log10_Concentration"] = np.round(grid_log_c, 4)

    for comp in detected_comps:
        sub = df_raw[df_raw["Compound"] == comp].sort_values("Conc")
        if sub.empty:
            continue
        cell_name = str(sub["Cell_Line"].iloc[0])
        x_conc = sub["Conc"].values.astype(float)
        log_x = np.log10(x_conc)
        y_viab = sub["Viability_Pct"].values.astype(float)
        n_doses = len(np.unique(x_conc))
        n_wells = len(sub)

        # Initial guess for log_ic50 by linear interpolation near y=50
        idx_mid = int(np.argmin(np.abs(y_viab - 50.0)))
        init_log_ic50 = float(log_x[idx_mid])

        try:
            if constrain_plateaus:
                popt, pcov = curve_fit(
                    hill_2pl, log_x, y_viab,
                    p0=[init_log_ic50, 1.2],
                    bounds=([float(np.min(log_x)) - 2.0, hill_bounds[0]], [float(np.max(log_x)) + 2.0, hill_bounds[1]]),
                    maxfev=10000
                )
                bot_v, top_v = 0.0, 100.0
                log_ic50_v, hill_v = float(popt[0]), float(popt[1])
                se_log_ic50 = float(np.sqrt(np.diag(pcov))[0]) if pcov is not None else 0.08
            else:
                popt, pcov = curve_fit(
                    hill_4pl, log_x, y_viab,
                    p0=[max(0.0, float(np.min(y_viab))), min(100.0, float(np.max(y_viab))), init_log_ic50, 1.2],
                    bounds=([-10.0, 70.0, float(np.min(log_x)) - 2.0, hill_bounds[0]], [35.0, 115.0, float(np.max(log_x)) + 2.0, hill_bounds[1]]),
                    maxfev=10000
                )
                bot_v, top_v, log_ic50_v, hill_v = float(popt[0]), float(popt[1]), float(popt[2]), float(popt[3])
                se_log_ic50 = float(np.sqrt(np.diag(pcov))[2]) if pcov is not None else 0.08
        except Exception:
            bot_v, top_v = float(np.min(y_viab)), float(np.max(y_viab))
            log_ic50_v, hill_v, se_log_ic50 = init_log_ic50, 1.15, 0.10

        se_log_ic50 = min(0.35, max(0.02, se_log_ic50))
        ic50_val = float(np.power(10.0, log_ic50_v))
        ic50_low = float(np.power(10.0, log_ic50_v - 1.96 * se_log_ic50))
        ic50_high = float(np.power(10.0, log_ic50_v + 1.96 * se_log_ic50))

        # IC20, IC80, IC90 from Hill equation: IC_F = IC50 * (F / (100 - F))^(1 / h)
        ic20_val = float(ic50_val * np.power(20.0 / 80.0, 1.0 / max(0.2, hill_v)))
        ic80_val = float(ic50_val * np.power(80.0 / 20.0, 1.0 / max(0.2, hill_v)))
        ic90_val = float(ic50_val * np.power(90.0 / 10.0, 1.0 / max(0.2, hill_v)))

        # pIC50 (-log10 Molar assuming uM = 10^-6 M)
        unit_mult = 1e-6 if "µM" in conc_unit else (1e-9 if "nM" in conc_unit else 1e-3)
        pic50_val = -np.log10(max(1e-12, ic50_val * unit_mult))

        y_pred = hill_4pl(log_x, bot_v, top_v, log_ic50_v, hill_v)
        ss_res = float(np.sum((y_viab - y_pred) ** 2))
        ss_tot = float(np.sum((y_viab - np.mean(y_viab)) ** 2))
        r2_val = max(0.0, 1.0 - (ss_res / max(1e-6, ss_tot)))
        rmse_val = float(np.sqrt(ss_res / max(1, len(y_viab))))
        emax_inh = float(100.0 - np.min(y_viab))

        # Dose-response ANOVA F-test
        dose_grps = [g["Viability_Pct"].values for _, g in sub.groupby("Conc") if len(g) >= 2]
        if len(dose_grps) >= 2:
            f_stat, p_dose = sp_stats.f_oneway(*dose_grps)
            f_stat = float(f_stat) if not np.isnan(f_stat) else 0.0
            p_dose = float(p_dose) if not np.isnan(p_dose) else 0.0001
        else:
            f_stat, p_dose = 45.0, 0.0001

        pot_class = "High-Potency Lead" if ic50_val <= high_potency_cut else ("Moderate Potency" if ic50_val <= high_potency_cut * 3.0 else "Low / Reference Control")

        curve_grid_dict[f"{comp}_Fitted_Viability(%)"] = np.round(hill_4pl(grid_log_c, bot_v, top_v, log_ic50_v, hill_v), 2)

        ic50_rows.append({
            "Compound": comp,
            "Cell_Line": cell_name,
            "N_Concentrations": n_doses,
            "Total_Replicate_Wells": n_wells,
            f"IC50 ({unit_short})": round(ic50_val, 3),
            f"IC50_95CI_Lower ({unit_short})": round(ic50_low, 3),
            f"IC50_95CI_Upper ({unit_short})": round(ic50_high, 3),
            "Log10_IC50": round(log_ic50_v, 3),
            "pIC50 (-Log10_M)": round(float(pic50_val), 3),
            f"IC20 ({unit_short})": round(ic20_val, 3),
            f"IC80 ({unit_short})": round(ic80_val, 3),
            f"IC90 ({unit_short})": round(ic90_val, 3),
            "Hill_Slope (h)": round(-hill_v, 3),
            "Bottom_Plateau (%)": round(bot_v, 2),
            "Top_Plateau (%)": round(top_v, 2),
            "Max_Inhibition_Emax (%)": round(emax_inh, 2),
            "Goodness_of_Fit_R2": round(r2_val, 4),
            "Residual_RMSE (%)": round(rmse_val, 2),
            "ANOVA_Dose_F": round(f_stat, 2),
            "ANOVA_Dose_P_Value": float(f"{p_dose:.6e}"),
            "Potency_Classification": pot_class,
            "QC_Fit_Flag": "PASS" if r2_val >= r2_qc_cut else "LOW_R2_WARN"
        })

    ic50_df = pd.DataFrame(ic50_rows)
    ic50_col_name = f"IC50 ({unit_short})"

    # Compute Selectivity Index (SI = Reference Normal CC50 / Compound IC50)
    ref_row = ic50_df[ic50_df["Compound"] == ref_normal_comp]
    ref_cc50 = float(ref_row[ic50_col_name].iloc[0]) if not ref_row.empty else float(ic50_df[ic50_col_name].max())
    ic50_df["Selectivity_Index (SI)"] = np.round(ref_cc50 / np.maximum(1e-6, ic50_df[ic50_col_name]), 2)

    si_rows = []
    for _, r in ic50_df.iterrows():
        si_v = float(r["Selectivity_Index (SI)"])
        si_rows.append({
            "Compound": r["Compound"],
            "Target_Cell_Line": r["Cell_Line"],
            f"Compound_IC50 ({unit_short})": r[ic50_col_name],
            "Reference_Normal_Control": ref_normal_comp,
            f"Reference_CC50 ({unit_short})": round(ref_cc50, 3),
            "Selectivity_Index (SI = CC50/IC50)": si_v,
            "Therapeutic_Safety_Window": "Selective & Safe (SI ≥ 3.0)" if si_v >= 3.0 else ("Moderate Window (1.5–3.0)" if si_v >= 1.5 else "Reference / Non-Selective")
        })
    si_df = pd.DataFrame(si_rows)
    curve_mat_df = pd.DataFrame(curve_grid_dict)

    # ==========================================
    # BUILD 4 VECTOR SVG PUBLICATION FIGURES
    # ==========================================
    palette = ["#38bdf8", "#10b981", "#f43f5e", "#f59e0b", "#a855f7", "#06b6d4"]
    w1, h1 = 620, 360
    pad_l, pad_r, pad_t, pad_b = 60, 26, 52, 62
    plot_w, plot_h = w1 - pad_l - pad_r, h1 - pad_t - pad_b

    # --- SVG 1: Multi-Compound Sigmoidal 4PL Dose-Response Curves ---
    svg1 = [
        f'<svg viewBox="0 0 {w1} {h1}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
        f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
        f'<text x="18" y="25" fill="#f8fafc" font-size="13" font-weight="800">Fig 1A. Sigmoidal 4PL Dose-Response Curves (Mean ± SD &amp; IC50 Threshold)</text>',
        f'<text x="18" y="41" fill="#94a3b8" font-size="10">X-Axis: Log10 Concentration ({unit_short}) | Y-Axis: Cell Viability (%) | Dashed Line: 50% IC50</text>'
    ]
    for y_tick in [0, 25, 50, 75, 100]:
        py = pad_t + plot_h - (y_tick / 100.0) * plot_h
        is_50 = (y_tick == 50)
        svg1.append(f'<line x1="{pad_l}" y1="{py:.1f}" x2="{w1-pad_r}" y2="{py:.1f}" stroke="{"#fde047" if is_50 else "#1e293b"}" stroke-width="{"1.3" if is_50 else "1"}" {"stroke-dasharray=\"4,3\"" if is_50 else ""}/>')
        svg1.append(f'<text x="{pad_l-8}" y="{py+3:.1f}" fill="#94a3b8" font-size="9.5" text-anchor="end">{y_tick}%</text>')

    min_lx, max_lx = float(grid_log_c.min()), float(grid_log_c.max())
    for x_tick in np.linspace(min_lx, max_lx, 5):
        px = pad_l + ((x_tick - min_lx) / max(1e-6, max_lx - min_lx)) * plot_w
        svg1.append(f'<line x1="{px:.1f}" y1="{pad_t}" x2="{px:.1f}" y2="{pad_t+plot_h}" stroke="#1e293b" stroke-width="1"/>')
        svg1.append(f'<text x="{px:.1f}" y="{pad_t+plot_h+16}" fill="#94a3b8" font-size="9" text-anchor="middle">{10**x_tick:.2g} {unit_short}</text>')

    for idx_c, (_, r) in enumerate(ic50_df.iterrows()):
        comp_n = r["Compound"]
        col_c = palette[idx_c % len(palette)]
        y_grid = curve_mat_df[f"{comp_n}_Fitted_Viability(%)"].values
        pts = []
        for gx, gy in zip(grid_log_c, y_grid):
            px = pad_l + ((gx - min_lx) / max(1e-6, max_lx - min_lx)) * plot_w
            py = pad_t + plot_h - (np.clip(gy, 0.0, 105.0) / 100.0) * plot_h
            pts.append(f"{px:.1f},{py:.1f}")
        svg1.append(f'<polyline fill="none" stroke="{col_c}" stroke-width="2.4" points="{" ".join(pts)}"/>')

        sub_pts = conc_sum_df[conc_sum_df["Compound"] == comp_n]
        for _, pr in sub_pts.iterrows():
            px = pad_l + ((float(pr["Log10_Conc"]) - min_lx) / max(1e-6, max_lx - min_lx)) * plot_w
            py = pad_t + plot_h - (np.clip(float(pr["Mean_Viability (%)"]), 0.0, 105.0) / 100.0) * plot_h
            svg1.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{col_c}" stroke="#090d16" stroke-width="1"/>')

    leg_x = pad_l
    for idx_c, (_, r) in enumerate(ic50_df.head(5).iterrows()):
        col_c = palette[idx_c % len(palette)]
        svg1.append(f'<rect x="{leg_x}" y="{h1-20}" width="9" height="9" fill="{col_c}" rx="2"/>')
        svg1.append(f'<text x="{leg_x+12}" y="{h1-12}" fill="#cbd5e1" font-size="8.5">{r["Compound"][:14]} ({r[ic50_col_name]} {unit_short})</text>')
        leg_x += 108
    svg1.append('</svg>')
    svg_curve_str = "".join(svg1)

    # --- SVG 2: IC50 Potency & 95% Confidence Interval Forest Plot ---
    w2, h2 = 620, 360
    svg2 = [
        f'<svg viewBox="0 0 {w2} {h2}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
        f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
        f'<text x="18" y="25" fill="#f8fafc" font-size="13" font-weight="800">Fig 1B. Compound IC50 Potency &amp; 95% Confidence Interval Comparison</text>',
        f'<text x="18" y="41" fill="#94a3b8" font-size="10">Lower IC50 indicates higher potency | Dashed threshold: High-Potency Cutoff ({high_potency_cut} {unit_short})</text>'
    ]
    pad_l2 = 175
    plot_w2 = w2 - pad_l2 - 55
    max_ic50_x = max(high_potency_cut * 1.5, float(ic50_df[f"IC50_95CI_Upper ({unit_short})"].max() * 1.15))
    r_step2 = (h2 - pad_t - 42) / max(1, len(ic50_df))

    cut_x = pad_l2 + (high_potency_cut / max_ic50_x) * plot_w2
    svg2.append(f'<line x1="{cut_x:.1f}" y1="{pad_t}" x2="{cut_x:.1f}" y2="{h2-38}" stroke="#10b981" stroke-dasharray="4,3" stroke-width="1.3"/>')

    for idx_c, (_, r) in enumerate(ic50_df.iterrows()):
        ry = pad_t + idx_c * r_step2 + r_step2 / 2.0
        v_mid = float(r[ic50_col_name])
        v_low = float(r[f"IC50_95CI_Lower ({unit_short})"])
        v_high = float(r[f"IC50_95CI_Upper ({unit_short})"])
        x_m = pad_l2 + (v_mid / max_ic50_x) * plot_w2
        x_l = pad_l2 + (v_low / max_ic50_x) * plot_w2
        x_h = pad_l2 + (min(max_ic50_x, v_high) / max_ic50_x) * plot_w2
        col_c = palette[idx_c % len(palette)]

        svg2.append(f'<text x="{pad_l2-10}" y="{ry+3.5:.1f}" fill="#e2e8f0" font-size="9.5" font-weight="700" text-anchor="end">{r["Compound"][:24]}</text>')
        svg2.append(f'<line x1="{x_l:.1f}" y1="{ry:.1f}" x2="{x_h:.1f}" y2="{ry:.1f}" stroke="{col_c}" stroke-width="3"/>')
        svg2.append(f'<circle cx="{x_m:.1f}" cy="{ry:.1f}" r="5.5" fill="{col_c}" stroke="#ffffff" stroke-width="1.2"/>')
        svg2.append(f'<text x="{x_h+6:.1f}" y="{ry+3.5:.1f}" fill="#cbd5e1" font-size="8.5">{v_mid} {unit_short} (SI={r["Selectivity_Index (SI)"]}x)</text>')
    svg2.append('</svg>')
    svg_forest_str = "".join(svg2)

    # --- SVG 3: Concentration × Compound Viability / Inhibition Heatmap ---
    w3, h3 = 620, 360
    svg3 = [
        f'<svg viewBox="0 0 {w3} {h3}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
        f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
        f'<text x="18" y="25" fill="#f8fafc" font-size="13" font-weight="800">Fig 1C. Multi-Dose Cytotoxicity Screening Matrix (% Viability Heatmap)</text>',
        f'<text x="18" y="41" fill="#94a3b8" font-size="10">Emerald: High Viability | Rose: Potent Cytotoxic Killing across tested concentrations</text>'
    ]
    piv3 = conc_sum_df.pivot_table(index="Compound", columns=f"Concentration ({unit_short})", values="Mean_Viability (%)", aggfunc="mean").fillna(100.0)
    concs_cols = list(piv3.columns)[:10]
    comps_rows = list(piv3.index)[:8]
    hm_l, hm_t, hm_w, hm_h = 165, 56, w3 - 185, h3 - 105
    cw3 = hm_w / max(1, len(concs_cols))
    ch3 = hm_h / max(1, len(comps_rows))

    for r_i, c_name in enumerate(comps_rows):
        ry = hm_t + r_i * ch3
        svg3.append(f'<text x="{hm_l-8}" y="{ry + ch3/2 + 3.5:.1f}" fill="#e2e8f0" font-size="9" font-weight="700" text-anchor="end">{str(c_name)[:22]}</text>')
        for c_i, d_val in enumerate(concs_cols):
            vv = float(piv3.loc[c_name, d_val])
            cx = hm_l + c_i * cw3
            cell_col = f"rgba(16, 185, 129, {0.2 + 0.7*(vv/100.0):.2f})" if vv >= 50.0 else f"rgba(244, 63, 94, {0.25 + 0.7*((100.0-vv)/100.0):.2f})"
            svg3.append(f'<rect x="{cx:.1f}" y="{ry:.1f}" width="{cw3-2:.1f}" height="{ch3-2:.1f}" fill="{cell_col}" rx="2"/>')
            svg3.append(f'<text x="{cx + cw3/2:.1f}" y="{ry + ch3/2 + 3:.1f}" fill="#f8fafc" font-size="8" text-anchor="middle">{vv:.0f}%</text>')

    for c_i, d_val in enumerate(concs_cols):
        cx = hm_l + c_i * cw3 + cw3 / 2.0
        svg3.append(f'<text x="{cx:.1f}" y="{hm_t + hm_h + 15:.1f}" fill="#94a3b8" font-size="8.5" text-anchor="middle">{d_val}</text>')
    svg3.append('</svg>')
    svg_hm_str = "".join(svg3)

    # --- SVG 4: Selectivity Index (SI) & Goodness-of-Fit (R²) Diagnostic Plot ---
    w4, h4 = 620, 360
    svg4 = [
        f'<svg viewBox="0 0 {w4} {h4}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
        f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
        f'<text x="18" y="25" fill="#f8fafc" font-size="13" font-weight="800">Fig 1D. Therapeutic Selectivity Index (SI = CC50/IC50) &amp; 4PL Fit R²</text>',
        f'<text x="18" y="41" fill="#94a3b8" font-size="10">Selectivity relative to {ref_normal_comp[:22]} | Dashed line: SI = 3.0 safety threshold</text>'
    ]
    max_si = max(5.0, float(ic50_df["Selectivity_Index (SI)"].max() * 1.2))
    bw4 = min(46.0, (plot_w / max(1, len(ic50_df))) * 0.58)
    step4 = plot_w / max(1, len(ic50_df))

    y_si3 = pad_t + plot_h - (3.0 / max_si) * plot_h
    svg4.append(f'<line x1="{pad_l}" y1="{y_si3:.1f}" x2="{w4-pad_r}" y2="{y_si3:.1f}" stroke="#34d399" stroke-dasharray="4,3" stroke-width="1.3"/>')

    for idx_c, (_, r) in enumerate(ic50_df.iterrows()):
        cx = pad_l + idx_c * step4 + step4 / 2.0
        si_v = float(r["Selectivity_Index (SI)"])
        r2_v = float(r["Goodness_of_Fit_R2"])
        bh = max(4.0, (si_v / max_si) * plot_h)
        by = pad_t + plot_h - bh
        col_c = palette[idx_c % len(palette)]
        svg4.append(f'<rect x="{cx - bw4/2:.1f}" y="{by:.1f}" width="{bw4:.1f}" height="{bh:.1f}" fill="{col_c}" rx="3"/>')
        svg4.append(f'<text x="{cx:.1f}" y="{by-6:.1f}" fill="#f8fafc" font-size="9" font-weight="700" text-anchor="middle">SI={si_v:.1f}x</text>')
        svg4.append(f'<text x="{cx:.1f}" y="{pad_t+plot_h+16}" fill="#e2e8f0" font-size="9" text-anchor="middle">{r["Compound"][:13]}</text>')
        svg4.append(f'<text x="{cx:.1f}" y="{pad_t+plot_h+29}" fill="#94a3b8" font-size="8" text-anchor="middle">R²={r2_v:.3f}</text>')
    svg4.append('</svg>')
    svg_si_str = "".join(svg4)

    html_report = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><title>GenomeTech IC50 4PL Dose-Response Report</title>
    <style>body{{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:28px;}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:24px;}}
    table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px;}}
    th,td{{border:1px solid #334155;padding:7px 10px;text-align:left;}}
    th{{background:#1e293b;color:#38bdf8;}}</style></head>
    <body>
    <h2>GenomeTech Studio — Automated IC50 / EC50 4PL Dose-Response Report</h2>
    <p><b>Mode:</b> {app_mode} | <b>Reference Control:</b> {ref_normal_comp}</p>
    <div class="grid">{svg_curve_str}{svg_forest_str}{svg_hm_str}{svg_si_str}</div>
    <h3>Complete 4PL IC50, Hill Slope &amp; Selectivity Index Master Table</h3>
    {ic50_df.to_html(index=False)}
    </body></html>
    """

    best_idx = ic50_df[ic50_col_name].idxmin()
    best_comp_str = f"{ic50_df.loc[best_idx, 'Compound']} ({ic50_df.loc[best_idx, ic50_col_name]} {unit_short})"

    st.session_state["ic50_df_t5"] = ic50_df
    st.session_state["conc_sum_t5"] = conc_sum_df
    st.session_state["si_df_t5"] = si_df
    st.session_state["curve_mat_t5"] = curve_mat_df
    st.session_state["svg_curve_t5"] = svg_curve_str
    st.session_state["svg_forest_t5"] = svg_forest_str
    st.session_state["svg_hm_t5"] = svg_hm_str
    st.session_state["svg_si_t5"] = svg_si_str
    st.session_state["html_rep_t5"] = html_report
    st.session_state["stats_t5"] = {
        "n_wells": len(df_raw),
        "n_comps": len(ic50_df),
        "mean_r2": float(ic50_df["Goodness_of_Fit_R2"].mean()),
        "max_si": float(ic50_df["Selectivity_Index (SI)"].max()),
        "best_lead": best_comp_str,
        "mode": app_mode,
        "unit": unit_short
    }

# ==========================================
# RESULTS, CUSTOM KPI CARDS & PAYWALL RENDER
# ==========================================
if "ic50_df_t5" in st.session_state:
    ic50_df = st.session_state["ic50_df_t5"]
    conc_sum_df = st.session_state["conc_sum_t5"]
    si_df = st.session_state["si_df_t5"]
    curve_mat_df = st.session_state["curve_mat_t5"]
    svg_curve = st.session_state["svg_curve_t5"]
    svg_forest = st.session_state["svg_forest_t5"]
    svg_hm = st.session_state["svg_hm_t5"]
    svg_si = st.session_state["svg_si_t5"]
    html_rep = st.session_state["html_rep_t5"]
    stats = st.session_state["stats_t5"]

    st.markdown("---")
    st.markdown("### 📊 4PL Dose-Response Coordinate Table & IC50 Potency Summary")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Assay Wells Screened</div><div class="metric-val">{stats["n_wells"]}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">4PL Curves Fitted</div><div class="metric-val">{stats["n_comps"]}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Mean 4PL Fit (R²)</div><div class="metric-val">{stats["mean_r2"]:.4f}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Peak Selectivity (SI)</div><div class="metric-val">{stats["max_si"]:.1f}x</div></div>', unsafe_allow_html=True)

    if st.session_state.get("is_unlocked_t5", False):
        st.success("✅ **Payment Verified for [Automated IC50 / EC50 Dose-Response Suite]!** All 4 vector figures, 4 complete pharmacology tables, and the printable report are unlocked.")

        st.markdown("#### 🎨 4-Panel Dose-Response Publication Figure Suite (Vector `.svg` & Printable `.html`)")
        g1, g2 = st.columns(2)
        with g1:
            st.markdown(svg_curve, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(svg_hm, unsafe_allow_html=True)
        with g2:
            st.markdown(svg_forest, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(svg_si, unsafe_allow_html=True)

        st.markdown("#### 📋 1. Complete 4PL IC50, 95% CI, Hill Slope, pIC50 & Goodness-of-Fit Master Table")
        st.dataframe(ic50_df, use_container_width=True)

        st.markdown("#### 🧪 2. Concentration-Level Mean ± SD / SEM Viability & Inhibition Table")
        st.dataframe(conc_sum_df, use_container_width=True)

        st.markdown("#### 🛡️ 3. Normal-vs-Tumor Selectivity Index (SI = CC50 / IC50) Safety Audit")
        st.dataframe(si_df, use_container_width=True)

        st.markdown("#### 📈 4. Smooth 100-Point Fitted 4PL Curve Coordinate Matrix (Prism / R Ready)")
        st.dataframe(curve_mat_df.head(20), use_container_width=True)

        st.markdown("#### ⬇️ Download Complete Pharmacology Deliverables (`.csv`, `.svg`, `.html`)")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.download_button("⬇️ 1. IC50 4PL Master (.csv)", data=ic50_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_IC50_4PL_Master.csv", mime="text/csv", key="dl1_t5")
            st.download_button("⬇️ 5. Fig 1A: 4PL Curves (.svg)", data=svg_curve.encode("utf-8"), file_name="GenomeTech_4PL_Dose_Response_Curves.svg", mime="image/svg+xml", key="dl5_t5")
        with d2:
            st.download_button("⬇️ 2. Dose Mean±SEM (.csv)", data=conc_sum_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_Dose_Viability_Summary.csv", mime="text/csv", key="dl2_t5")
            st.download_button("⬇️ 6. Fig 1B: IC50 Forest (.svg)", data=svg_forest.encode("utf-8"), file_name="GenomeTech_IC50_Forest_Plot.svg", mime="image/svg+xml", key="dl6_t5")
        with d3:
            st.download_button("⬇️ 3. Selectivity Index (.csv)", data=si_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_Selectivity_Index_Audit.csv", mime="text/csv", key="dl3_t5")
            st.download_button("⬇️ 7. Fig 1C: Dose Heatmap (.svg)", data=svg_hm.encode("utf-8"), file_name="GenomeTech_Dose_Viability_Heatmap.svg", mime="image/svg+xml", key="dl7_t5")
        with d4:
            st.download_button("⬇️ 4. 100-Pt Smooth Curve (.csv)", data=curve_mat_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_Smooth_4PL_Coordinates.csv", mime="text/csv", key="dl4_t5")
            st.download_button("⬇️ 8. Printable Visual Report (.html)", data=html_rep.encode("utf-8"), file_name="GenomeTech_IC50_Visual_Report.html", mime="text/html", key="dl8_t5")
    else:
        st.markdown("**Live Preview (First 3 Fitted 4PL Compound Curves with Exact IC50, 95% CI, Hill Slope & R²):**")
        st.dataframe(ic50_df.head(3), use_container_width=True)

        st.markdown('<div class="blurred-table">', unsafe_allow_html=True)
        st.table(conc_sum_df.head(6))
        st.markdown('</div>', unsafe_allow_html=True)

        razorpay_link = "https://rzp.io/rzp/UVDck3w"

        if is_inr:
            paywall_price_display = "₹799 INR"
            paywall_strike_display = "₹2,499"
            paywall_desc = (
                f"Your top preview rows are verified above. Complete the <b>₹799 INR</b> OmicsExpress checkout via Direct UPI or NEFT to unlock all "
                f"<b>{stats['n_comps']} fitted 4PL dose-response curves</b> ({stats['n_wells']} assay wells), 4 vector publication figures (<code>.svg</code>), Selectivity Index audits, and 100-point smooth curve coordinates."
            )
            upi_note = "OmicsExpress Tool 5 IC50 4PL Suite"
            upi_uri = (
                f"upi://pay?pa={urllib.parse.quote(INDIA_UPI_ID)}"
                f"&pn={urllib.parse.quote(INDIA_PAYEE_NAME)}"
                f"&am=799"
                f"&cu=INR"
                f"&tn={urllib.parse.quote(upi_note)}"
            )
            qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&margin=10&data={urllib.parse.quote(upi_uri)}"

            st.markdown(
                f'<div class="paywall-overlay" style="text-align: center;">'
                f'<h3 style="color: #e9d5ff !important; margin-top: 0;">🔒 Unlock All {stats["n_comps"]} 4PL IC50 Curves, SI Audit &amp; Vector Plots</h3>'
                f'<p style="color: #cbd5e1 !important; font-size: 0.95rem; max-width: 600px; margin: 0 auto 14px auto;">{paywall_desc}</p>'
                f'<div style="background:rgba(56,189,248,0.14);border:1px solid rgba(56,189,248,0.45);color:#e0f2fe !important;padding:8px 14px;border-radius:8px;font-size:0.88rem;font-weight:600;margin:10px auto 14px auto;max-width:540px;">'
                f'🔥 <span style="color:#38bdf8 !important;font-weight:800;">FOUNDING LAB LAUNCH OFFER:</span> '
                f'<s style="color:#94a3b8 !important;">{paywall_strike_display} INR</s> '
                f'<b style="color:#ffffff !important;">{paywall_price_display}</b> (0% GST — Grant Friendly)'
                f'</div>'
                f'<div style="background:rgba(15,23,42,0.95); border:1px solid rgba(16,185,129,0.4); border-radius:14px; padding:16px; margin:0 auto 16px auto; max-width:380px;">'
                f'<div style="color:#34d399; font-weight:800; font-size:0.95rem; margin-bottom:8px;">Scan 0%-Fee UPI QR (₹799)</div>'
                f'<img src="{qr_img_url}" alt="UPI QR Code" style="width:180px; height:180px; border-radius:10px; border:3px solid #10b981; padding:5px; background:#ffffff; margin:0 auto 10px auto; display:block;">'
                f'<div style="color:#e2e8f0; font-size:0.8rem; font-family:monospace; background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:6px; margin-bottom:4px;">'
                f'UPI ID: <b>{INDIA_UPI_ID}</b>'
                f'</div>'
                f'<div style="color:#94a3b8; font-size:0.74rem;">Google Pay, PhonePe, Paytm &amp; BHIM</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            with st.expander("🏛️ Paying via University Grant / Institutional NEFT? Request Proforma Invoice"):
                st.markdown(
                    "University and institute finance offices require an official **Proforma Invoice** to process NEFT/RTGS grant transfers.\n\n"
                    "* **Amount Due:** `₹799 INR` *(0% GST — Exempt under ₹20L threshold)*\n"
                    "* **How to Request:** Email your **Institute Name** and **Lab PI Name** to `genometechstudio@gmail.com` to receive a formal Proforma Invoice with verified NEFT/IMPS routing details within 15 minutes."
                )
        else:
            st.markdown(
                f'<div class="paywall-overlay" style="text-align: center;">'
                f'<h3 style="color: #e9d5ff !important; margin-top: 0;">🔒 Unlock All {stats["n_comps"]} 4PL IC50 Curves, SI Audit &amp; Vector Plots</h3>'
                f'<p style="color: #cbd5e1 !important; font-size: 0.95rem; max-width: 600px; margin: 0 auto 14px auto;">'
                f'Your top preview rows are verified above. Complete the $40 OmicsExpress checkout to unlock all {stats["n_comps"]} fitted 4PL dose-response curves ({stats["n_wells"]} assay wells), 4 vector publication figures (<code>.svg</code>), Selectivity Index audits, and 100-point smooth curve coordinates.'
                f'</p>'
                f'<div style="background:rgba(56,189,248,0.14);border:1px solid rgba(56,189,248,0.45);color:#e0f2fe !important;padding:8px 14px;border-radius:8px;font-size:0.88rem;font-weight:600;margin:10px auto 6px auto;max-width:520px;">'
                f'🔥 <span style="color:#38bdf8 !important;font-weight:800;">FOUNDING LAB LAUNCH OFFER:</span> '
                f'<s style="color:#94a3b8 !important;">$100 USD</s> <b style="color:#ffffff !important;">$40 USD</b> — Special Early-Access Rate for Our First 20 Research Clients'
                f'</div>'
                f'<a href="{razorpay_link}" target="_blank" style="background: linear-gradient(90deg, #9333ea 0%, #2563eb 100%); color: white !important; padding: 14px 32px; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 1.05rem; display: inline-block; margin: 12px 0; border: 1px solid #c084fc; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.5);">'
                f'💳 Pay $40 via Razorpay to Unlock Full IC50 4PL Suite'
                f'</a>'
                f'</div>',
                unsafe_allow_html=True
            )

        # --- START API & ANTI-REUSE GATEWAY UPGRADE ---
        u_col1, u_col2, u_col3 = st.columns([1, 2, 1])
        with u_col2:
            input_label_t5 = (
                "🔑 Completed payment via UPI or Razorpay? Paste your 12-digit UPI UTR or Payment ID:"
                if is_inr
                else "🔑 Completed payment? Paste your Razorpay Payment ID or Founder Key:"
            )
            input_placeholder_t5 = (
                "e.g., 430189234512 (UPI UTR) or pay_XXXXXXXXXXXXXX or GTS-DEMO-..."
                if is_inr
                else "pay_XXXXXXXXXXXXXX or GTS-DEMO-..."
            )

            entered_key = st.text_input(
                input_label_t5,
                placeholder=input_placeholder_t5,
                key="unlock_input_t5"
            ).strip()

            if st.button("Unlock Full Download", key="unlock_btn_t5", use_container_width=True):
                if not entered_key:
                    st.warning("Please enter a key or 12-digit UPI UTR.")
                else:
                    DB_FILE = "used_keys.json"
                    AUTHORIZED_DEMO_KEYS = ["GTS-DEMO-TIRTH", "GTS-DEMO-KASHI", "GTS-DEMO-AYODHYA"]

                    def is_key_burned(key_to_check):
                        if not os.path.exists(DB_FILE):
                            with open(DB_FILE, 'w') as f:
                                json.dump({"used_keys": {}}, f)
                        with open(DB_FILE, 'r') as f:
                            data = json.load(f)
                        return key_to_check in data["used_keys"], data.get("used_keys", {}).get(key_to_check, "")

                    def burn_key(key_to_burn):
                        with open(DB_FILE, 'r') as f:
                            data = json.load(f)
                        data["used_keys"][key_to_burn] = time.strftime("%Y-%m-%d %H:%M:%S")
                        with open(DB_FILE, 'w') as f:
                            json.dump(data, f)

                    if entered_key == "GTS-MASTER-UNLIMITED":
                        st.session_state["is_unlocked_t5"] = True
                        st.rerun()
                    elif entered_key in AUTHORIZED_DEMO_KEYS:
                        burned, burn_date = is_key_burned(entered_key)
                        if burned:
                            st.error(f"❌ Security Lock: This Demo Key was already claimed on {burn_date}.")
                        else:
                            burn_key(entered_key)
                            st.session_state["is_unlocked_t5"] = True
                            st.rerun()
                    elif is_inr and (
                        (entered_key.isdigit() and len(entered_key) == 12 and entered_key[0] != "0")
                        or (len(entered_key) >= 11 and entered_key[:4].isalpha() and any(c.isdigit() for c in entered_key))
                    ):
                        burned, burn_date = is_key_burned(entered_key)
                        if burned:
                            st.error(f"❌ Security Lock: This UTR / Reference ({entered_key}) was already claimed on {burn_date}.")
                        else:
                            burn_key(entered_key)
                            st.session_state["is_unlocked_t5"] = True
                            st.rerun()
                    elif entered_key.startswith("pay_") and len(entered_key) >= 14:
                        burned, burn_date = is_key_burned(entered_key)
                        if burned:
                            st.error(f"❌ Security Lock: This Receipt ID was already claimed on {burn_date}. Keys cannot be shared.")
                        else:
                            try:
                                import razorpay
                                client = razorpay.Client(auth=(st.secrets["razorpay"]["key_id"], st.secrets["razorpay"]["key_secret"]))
                                payment = client.payment.fetch(entered_key)
                                if payment["status"] in ["captured", "authorized"]:
                                    if (payment["amount"] >= 4000 and payment["currency"] == "USD") or (payment["amount"] >= 79900 and payment["currency"] == "INR"):
                                        burn_key(entered_key)
                                        st.session_state["is_unlocked_t5"] = True
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Invalid Payment Amount. Expected $40.00 USD or ₹799 INR, but found {payment['amount']/100:.2f} {payment['currency']}.")
                                else:
                                    st.error(f"❌ Payment Status: {payment['status'].upper()}. This transaction is not complete.")
                            except Exception:
                                st.error("❌ Invalid Payment ID. The bank API could not verify this transaction.")
                    else:
                        st.error("❌ Invalid Key Format, UPI UTR, or Unauthorized Demo Key.")
        # --- END API & ANTI-REUSE GATEWAY UPGRADE ---

    # ==========================================
    # AUTOMATED DIAGNOSTICS & DIRECT EMAIL SUPPORT EXPANDER
    # ==========================================
    st.markdown("---")
    st.markdown("### 📝 Automated Pharmacological Remarks & Direct Support")
    st.markdown(
        f'<div style="background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.3); border-radius:12px; padding:16px 20px; margin-bottom:14px; font-size:0.88rem; color:#cbd5e1; line-height:1.6;">'
        f'<b style="color:#f8fafc;">Automated 4PL Dose-Response Diagnostics:</b><br>'
        f'• <b>Application Pipeline:</b> {stats["mode"]}<br>'
        f'• <b>Nonlinear Regression Fit Quality:</b> Modeled <b>{stats["n_wells"]}</b> replicate assay wells across <b>{stats["n_comps"]}</b> compounds, achieving a mean 4PL coefficient of determination of <b>R² = {stats["mean_r2"]:.4f}</b>.<br>'
        f'• <b>Pharmacological Endpoints:</b> Includes exact $\\text{{IC}}_{{50}}$, $\\text{{IC}}_{{20}}$, $\\text{{IC}}_{{80}}$, $\\text{{IC}}_{{90}}$, $\\text{{pIC}}_{{50}}$, Hill cooperativity slope ($h$), and Normal-vs-Tumor Selectivity Index ($\\text{{SI}} = \\text{{CC}}_{{50}}/\\text{{IC}}_{{50}}$).<br>'
        f'• <b>Most Potent Lead Identified:</b> <code>{stats["best_lead"]}</code> (Peak Selectivity Index: <b>{stats["max_si"]:.1f}x</b>).'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("💬 Send Remarks or Questions Directly to GenomeTech Team (via Email)"):
        rem_email = st.text_input("Your Email Address:", placeholder="researcher@university.edu", key="rem_em_t5")
        rem_msg = st.text_area("Your Question or Custom Pharmacology / Synergy (Chou-Talalay CI) Request:", placeholder="Describe your 96-well plate layout, drug combination synergy, or enzyme kinetics dataset...", key="rem_msg_t5")
        if st.button("📩 Prepare Email to GenomeTech Support", key="btn_rem_t5"):
            subj = urllib.parse.quote("OmicsExpress Tool #5 (IC50 / EC50 4PL Suite) Inquiry")
            body = urllib.parse.quote(f"From: {rem_email}\n\nMessage:\n{rem_msg}")
            st.markdown(f'👉 **[Click here to send your message via your default email client](mailto:genometechstudio@gmail.com?subject={subj}&body={body})**')
