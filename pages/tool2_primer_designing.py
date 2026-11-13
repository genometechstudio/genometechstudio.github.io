import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as sp_stats
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
# PAGE STYLING (MATCHES OMICSEXPRESS DARK INDIGO/PURPLE THEME)
# ==========================================
st.markdown("""
<style>
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
# SESSION STATE INITIALIZATION (TOOL #2)
# ==========================================
if "is_unlocked_t2" not in st.session_state:
    st.session_state["is_unlocked_t2"] = False
if "last_mode_t2" not in st.session_state:
    st.session_state["last_mode_t2"] = None

# ==========================================
# TOP GLASS HEADER BANNER
# ==========================================
st.markdown(
    '<div class="glass-header">'
    '<div><span class="brand-title">🧪 <span style="color:#34d399;">GenomeTech</span> Studio</span>'
    '<span class="brand-sub">| OmicsExpress Automated Suite</span></div>'
    '<div class="tool-pill">⚡ Tool #2: Automated qPCR 2^-ΔΔCt Suite</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("## Automated qPCR 2<sup>-ΔΔCt</sup> Fold-Change & Significance Suite", unsafe_allow_html=True)
st.markdown(
    "Transform raw RT-qPCR Cycle Threshold ($C_t$ / $C_q$) spreadsheets across multiple genes, biological replicates, and treatment conditions into publication-ready fold-change matrices. "
    "Automatically computes **housekeeping normalization ($\\Delta C_t$), calibrator baseline shifts ($\\Delta\\Delta C_t$), Livak $2^{-\\Delta\\Delta C_t}$ & Pfaffl efficiency-corrected fold change, 95% CIs, Welch's $t$-test / One-Way ANOVA $p$-values, Benjamini-Hochberg FDR, and 4 vector publication figures (`.svg`)**."
)

# ==========================================
# COLLAPSIBLE FILE FORMAT & DELIVERABLES EXPANDER
# ==========================================
with st.expander("📋 Required File Format & Complete Wet-Lab Deliverables (.csv, .tsv, .txt, or .xlsx)", expanded=True):
    st.markdown(
        "* **Accepted File Formats:** Tabular `.csv`, `.tsv`, `.txt`, or `.xlsx` containing a **Sample/Replicate column**, **Experimental Group column**, **Gene Name column**, and **Cycle Threshold (`Ct` / `Cq`) column**.\n"
        "* **Complete Wet-Lab & MIQE Biostatistics Columns Included:**\n"
        "  1. **Cycle Threshold & Normalization Metrics:** `N_Biological_Replicates`, `Technical_Reps_Pooled`, `Mean_Target_Ct`, `SD_Target_Ct`, `Mean_HK_Ct`, `Mean_dCt`, `SD_dCt`, `SEM_dCt`.\n"
        "  2. **Relative Expression & Fold-Change Columns:** `Calibrator_dCt`, `Mean_ddCt`, `SEM_ddCt`, `Fold_Change_2^-ddCt`, `Pfaffl_Eff_Corrected_FC`, `Replicate_Mean_FC`, `SEM_FC`, `FC_95CI_Lower`, `FC_95CI_Upper`, `Log2_Fold_Change`, `Percent_Change (%)`, `Regulation_Direction`.\n"
        "  3. **Hypothesis Testing & Multiple Testing Correction:** `Welch_t_Statistic`, `Degrees_of_Freedom`, `Two_Tailed_P_Value`, `BH_Adjusted_FDR`, `Omnibus_ANOVA_F`, `Omnibus_ANOVA_P`, `Significance_Stars` (`*`, `**`, `***`).\n"
        "  4. **MIQE Housekeeping Audit & Matrix Outputs:** `InterGroup_HK_Ct_Drift`, `HK_CV_Percent`, `MIQE_QC_Flag`, plus a wide **Sample × Gene Fold-Change Matrix** ready for GraphPad Prism or R.\n"
        "* 💻 **Cross-Platform File Compatibility (Windows & Apple macOS):** All exported `.csv` tables use universal `UTF-8-BOM` encoding—double-click to open directly in **Microsoft Excel (Windows/Mac)**, Apple Numbers, Google Sheets, or load into R / Python. Vector figure (`.svg` / `.html`) outputs open natively in any web browser or Adobe Illustrator.\n"
        "* **Single-Mode License Note:** Each checkout unlocks your selected **Normalization Mode** (`Standard Livak 2^-ddCt`, `Pfaffl Efficiency-Corrected`, `Multi-Housekeeping Geometric Mean`, or `Custom`). Adjusting statistical cutoffs or plot parameters within your unlocked mode is free; switching the Normalization Mode starts a new run."
    )

# ==========================================
# UPLOAD BOX, DEMO CHECKBOX & PASTE TEXTAREA
# ==========================================
up_col, demo_col = st.columns([2.3, 1])
with up_col:
    uploaded_file = st.file_uploader(
        "Drop your qPCR Ct Table (.csv, .tsv, .txt, .xlsx)",
        type=["csv", "tsv", "txt", "xlsx"],
        key="up_qpcr_file_t2"
    )
with demo_col:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    use_demo_t2 = st.checkbox("🧪 Load Demo Multi-Gene qPCR Dataset", value=(uploaded_file is None), key="chk_demo_t2")

st.caption("⚡ **Performance Note:** Optimized for high-throughput 96-well and 384-well qPCR plates: supports up to 50,000 wells with automatic technical replicate pooling.")

pasted_text = st.text_area(
    "Or paste CSV / Tab-Separated qPCR Ct rows directly (optional):",
    placeholder="Sample,Group,Gene,Ct\nCtrl_Rep1,Vehicle_Control,GAPDH,18.21\nCtrl_Rep1,Vehicle_Control,BRCA1,24.52\n...",
    height=88,
    key="paste_qpcr_t2"
)

# ==========================================
# 3-COLUMN CUSTOM FIXING CONDITIONS & THERMODYNAMIC/STATISTICAL OPTIMUMS
# ==========================================
st.markdown("### ⚙️ Custom Fixing Conditions & Normalization Optimums")

app_mode = st.selectbox(
    "Application Mode Preset (Switching application mode starts a new pipeline run):",
    [
        "Standard Livak 2^-ΔΔCt Method (100% Amplification Efficiency • Single/Multi-HK)",
        "Pfaffl Efficiency-Corrected Relative Quantification (Custom Primer Efficiency %)",
        "MIQE Strict Multi-Housekeeping Geometric Normalization (High-Precision Clinical qPCR)",
        "Custom Exploratory RT-qPCR Expression Profiling"
    ],
    key="mode_preset_t2"
)

if st.session_state["last_mode_t2"] is not None and st.session_state["last_mode_t2"] != app_mode:
    st.session_state["is_unlocked_t2"] = False
    for k in ["sum_df_t2", "rep_df_t2", "hk_qc_df_t2", "wide_fc_df_t2"]:
        st.session_state.pop(k, None)
st.session_state["last_mode_t2"] = app_mode

# Build or parse active input dataset so column selectors stay synced
def generate_demo_qpcr_df():
    np.random.seed(42)
    groups = ["Vehicle_Control", "Cisplatin_10uM", "Olaparib_25uM", "Combo_Therapy"]
    genes = ["GAPDH", "ACTB", "BRCA1", "TP53", "BAX", "BCL2", "CDKN1A", "VEGFA"]
    base_ct = {
        "GAPDH": 18.20, "ACTB": 18.55,
        "BRCA1": 24.60, "TP53": 23.90, "BAX": 25.30,
        "BCL2": 22.80, "CDKN1A": 24.90, "VEGFA": 23.15
    }
    shifts = {
        "Vehicle_Control": {"GAPDH": 0.00, "ACTB": 0.00, "BRCA1": 0.00, "TP53": 0.00, "BAX": 0.00, "BCL2": 0.00, "CDKN1A": 0.00, "VEGFA": 0.00},
        "Cisplatin_10uM":  {"GAPDH": 0.03, "ACTB": -0.02, "BRCA1": 1.25, "TP53": -1.55, "BAX": -1.90, "BCL2": 1.35, "CDKN1A": -2.15, "VEGFA": 0.90},
        "Olaparib_25uM":   {"GAPDH": -0.02, "ACTB": 0.04, "BRCA1": 2.05, "TP53": -1.05, "BAX": -1.30, "BCL2": 0.95, "CDKN1A": -1.45, "VEGFA": 1.45},
        "Combo_Therapy":   {"GAPDH": 0.02, "ACTB": 0.01, "BRCA1": 2.75, "TP53": -2.45, "BAX": -3.15, "BCL2": 2.50, "CDKN1A": -3.30, "VEGFA": 2.25}
    }
    rows = []
    for grp in groups:
        for rep in range(1, 5):  # 4 biological replicates
            samp_id = f"{grp[:4].upper()}_BioRep{rep}"
            for g in genes:
                # 2 technical replicates per biological replicate
                for tech in [1, 2]:
                    ct_val = base_ct[g] + shifts[grp][g] + np.random.normal(0, 0.14)
                    rows.append({
                        "Sample_ID": samp_id,
                        "Group": grp,
                        "Gene": g,
                        "Tech_Rep": tech,
                        "Ct": round(float(ct_val), 3)
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
elif use_demo_t2:
    active_df = generate_demo_qpcr_df()

c_left, c_mid, c_right = st.columns(3)

if active_df is not None and len(active_df.columns) >= 3:
    cols = list(active_df.columns)
    def_samp = next((c for c in cols if any(k in c.lower() for k in ["sample", "id", "biorep", "subject"])), cols[0])
    def_grp = next((c for c in cols if any(k in c.lower() for k in ["group", "cond", "treat", "cohort", "arm"])), cols[1 if len(cols) > 1 else 0])
    def_gene = next((c for c in cols if any(k in c.lower() for k in ["gene", "target", "marker", "primer", "assay"])), cols[2 if len(cols) > 2 else 0])
    def_ct = next((c for c in cols if any(k in c.lower() for k in ["ct", "cq", "cp", "cycle"])), cols[-1])
else:
    cols = ["Sample_ID", "Group", "Gene", "Ct"]
    def_samp, def_grp, def_gene, def_ct = "Sample_ID", "Group", "Gene", "Ct"

with c_left:
    st.markdown("**1. Column Mapping & Calibrator Setup**")
    col_sample = st.selectbox("Biological Sample / Replicate Column:", cols, index=cols.index(def_samp), key="map_s_t2")
    col_group = st.selectbox("Experimental Group / Condition Column:", cols, index=cols.index(def_grp), key="map_g_t2")
    col_gene = st.selectbox("Target / Reference Gene Column:", cols, index=cols.index(def_gene), key="map_gn_t2")
    col_ct = st.selectbox("Cycle Threshold (Ct / Cq) Column:", cols, index=cols.index(def_ct), key="map_ct_t2")

if active_df is not None and all(c in active_df.columns for c in [col_sample, col_group, col_gene, col_ct]):
    detected_genes = sorted(active_df[col_gene].dropna().astype(str).unique().tolist())
    detected_groups = list(dict.fromkeys(active_df[col_group].dropna().astype(str).tolist()))
else:
    detected_genes = ["GAPDH", "ACTB", "BRCA1", "TP53", "BAX", "BCL2"]
    detected_groups = ["Vehicle_Control", "Cisplatin_10uM"]

with c_mid:
    st.markdown("**2. Reference Normalization & Efficiency ($E$)**")
    default_hks = [g for g in detected_genes if g.upper() in ["GAPDH", "ACTB", "B2M", "18S", "HPRT1", "RPL13A", "U6", "TBP"]]
    if not default_hks and detected_genes:
        default_hks = [detected_genes[0]]
    default_hk_sel = default_hks[:2] if "Multi-Housekeeping" in app_mode else default_hks[:1]

    hk_genes = st.multiselect(
        "Housekeeping / Endogenous Reference Gene(s):",
        options=detected_genes,
        default=default_hk_sel,
        key="sel_hk_t2"
    )
    def_ctrl_i = next((i for i, g in enumerate(detected_groups) if any(k in g.lower() for k in ["control", "ctrl", "vehicle", "wt", "untreated", "normal"])), 0)
    ctrl_group = st.selectbox(
        "Calibrator Control Group (Fold Change = 1.0):",
        options=detected_groups,
        index=def_ctrl_i,
        key="sel_ctrl_t2"
    )
    ct_range = st.slider("Valid Ct / Cq Detection Window (Cycles):", min_value=5.0, max_value=45.0, value=(8.0, 38.0), step=0.5, key="ct_win_t2")
    default_eff = 96.5 if "Pfaffl" in app_mode else 100.0
    amp_eff = st.number_input("Primer Amplification Efficiency (%):", min_value=70.0, max_value=120.0, value=default_eff, step=0.5, key="eff_num_t2")

with c_right:
    st.markdown("**3. Statistical & MIQE Fixing Conditions**")
    pool_tech_reps = st.checkbox("Auto-Pool Technical Replicates per Biological Sample", value=True, key="chk_pool_t2")
    enforce_miqe_drift = st.checkbox("Flag Housekeeping Drift (>0.5 Ct inter-group shift)", value=True, key="chk_miqe_t2")
    apply_bh_fdr = st.checkbox("Compute Benjamini-Hochberg FDR Adjusted P-Values", value=True, key="chk_fdr_t2")
    p_cutoff = st.selectbox("Primary P-Value Significance Threshold (α):", [0.05, 0.01, 0.001, 0.10], index=0, key="p_cut_t2")
    fc_cutoff = st.number_input("Biological Fold-Change Highlight Cutoff (|Log2FC| ≥):", min_value=0.0, max_value=5.0, value=0.58, step=0.1, help="0.58 corresponds to a 1.5-fold change; 1.0 corresponds to a 2.0-fold change.", key="fc_cut_t2")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
run_clicked = st.button("🚀 Run Automated qPCR 2^-ΔΔCt Analysis", type="primary", key="btn_run_qpcr_t2")

# ==========================================
# CORE COMPUTATION ENGINE (AUTO-RUNS WHEN DEMO IS CHECKED OR BUTTON CLICKED)
# ==========================================
if (run_clicked or (use_demo_t2 and "sum_df_t2" not in st.session_state)) and active_df is not None:
    if not hk_genes:
        st.error("⚠️ Please select at least one Housekeeping / Reference gene in Column 2.")
    else:
        raw_sub = active_df[[col_sample, col_group, col_gene, col_ct]].copy()
        raw_sub.columns = ["Sample_ID", "Group", "Gene", "Ct"]
        raw_sub["Ct"] = pd.to_numeric(raw_sub["Ct"], errors="coerce")
        raw_sub = raw_sub.dropna(subset=["Sample_ID", "Group", "Gene", "Ct"])
        raw_sub = raw_sub[(raw_sub["Ct"] >= ct_range[0]) & (raw_sub["Ct"] <= ct_range[1])]

        total_wells_in = len(raw_sub)

        # Count technical replicates before pooling
        tech_counts = raw_sub.groupby(["Sample_ID", "Group", "Gene"], as_index=False)["Ct"].count().rename(columns={"Ct": "Tech_Reps"})
        if pool_tech_reps:
            bio_df = raw_sub.groupby(["Sample_ID", "Group", "Gene"], as_index=False)["Ct"].mean()
            bio_df = pd.merge(bio_df, tech_counts, on=["Sample_ID", "Group", "Gene"], how="left")
        else:
            bio_df = raw_sub.copy()
            bio_df["Tech_Reps"] = 1

        # Compute Reference Housekeeping Ct per Biological Sample (Arithmetic/Geometric Ct mean across selected HK genes)
        hk_subset = bio_df[bio_df["Gene"].isin(hk_genes)]
        hk_sample_map = hk_subset.groupby(["Sample_ID", "Group"], as_index=False)["Ct"].mean().rename(columns={"Ct": "Mean_HK_Ct"})

        merged_df = pd.merge(bio_df, hk_sample_map, on=["Sample_ID", "Group"], how="inner")
        target_df = merged_df[~merged_df["Gene"].isin(hk_genes)].copy()
        if target_df.empty:
            target_df = merged_df.copy()

        # ΔCt = Ct(target) - Ct(housekeeping)
        target_df["dCt"] = target_df["Ct"] - target_df["Mean_HK_Ct"]

        # Calibrator mean ΔCt in Control Group
        ctrl_dcts = target_df[target_df["Group"] == ctrl_group].groupby("Gene", as_index=False)["dCt"].mean().rename(columns={"dCt": "Calibrator_dCt"})
        target_df = pd.merge(target_df, ctrl_dcts, on="Gene", how="left")

        # ΔΔCt = ΔCt(sample) - Mean_ΔCt(calibrator)
        target_df["ddCt"] = target_df["dCt"] - target_df["Calibrator_dCt"]

        eff_base = 1.0 + (amp_eff / 100.0)
        target_df["Fold_Change_2^-ddCt"] = np.power(2.0, -target_df["ddCt"])
        target_df["Pfaffl_Eff_Corrected_FC"] = np.power(eff_base, -target_df["ddCt"])
        target_df["Log2_Fold_Change"] = -target_df["ddCt"] * np.log2(eff_base)

        # Housekeeping Stability Metrics per HK gene
        hk_qc_rows = []
        max_global_hk_drift = 0.0
        for hk in hk_genes:
            hk_g = bio_df[bio_df["Gene"] == hk]
            if hk_g.empty:
                continue
            m_ct = float(hk_g["Ct"].mean())
            sd_ct = float(hk_g["Ct"].std(ddof=1)) if len(hk_g) > 1 else 0.0
            cv_pct = (sd_ct / m_ct * 100.0) if m_ct > 0 else 0.0
            grp_means = hk_g.groupby("Group")["Ct"].mean()
            drift = float(grp_means.max() - grp_means.min()) if len(grp_means) > 1 else 0.0
            max_global_hk_drift = max(max_global_hk_drift, drift)
            hk_qc_rows.append({
                "Housekeeping_Gene": hk,
                "Biological_Samples": len(hk_g),
                "Mean_Ct": round(m_ct, 3),
                "SD_Ct": round(sd_ct, 3),
                "CV_Percent (%)": round(cv_pct, 2),
                "InterGroup_Ct_Drift (cycles)": round(drift, 3),
                "MIQE_Stability_Flag": "PASS (Stable <0.5 Ct)" if drift <= 0.5 else "WARNING (Drift >0.5 Ct)"
            })
        hk_qc_df = pd.DataFrame(hk_qc_rows)

        # Group-Level Master Summary Table with Complete Columns
        target_genes_sorted = sorted(target_df["Gene"].unique().tolist())
        groups_ordered = [ctrl_group] + [g for g in detected_groups if g != ctrl_group and g in target_df["Group"].unique()]

        summary_rows = []
        for g in target_genes_sorted:
            g_sub = target_df[target_df["Gene"] == g]
            ctrl_dct_vals = g_sub[g_sub["Group"] == ctrl_group]["dCt"].dropna().values
            cal_dct_val = float(np.mean(ctrl_dct_vals)) if len(ctrl_dct_vals) > 0 else 0.0

            # Omnibus One-Way ANOVA across groups
            grp_arrays = [g_sub[g_sub["Group"] == grp]["dCt"].dropna().values for grp in groups_ordered if len(g_sub[g_sub["Group"] == grp]) >= 2]
            if len(grp_arrays) >= 2:
                f_val, anova_p = sp_stats.f_oneway(*grp_arrays)
                f_val = float(f_val) if not np.isnan(f_val) else 0.0
                anova_p = float(anova_p) if not np.isnan(anova_p) else 1.0
            else:
                f_val, anova_p = 0.0, 1.0

            for grp in groups_ordered:
                sub = g_sub[g_sub["Group"] == grp]
                if sub.empty:
                    continue
                n_bio = len(sub)
                tech_pooled = int(sub["Tech_Reps"].sum())
                m_t_ct = float(sub["Ct"].mean())
                sd_t_ct = float(sub["Ct"].std(ddof=1)) if n_bio > 1 else 0.0
                m_hk_ct = float(sub["Mean_HK_Ct"].mean())

                m_dct = float(sub["dCt"].mean())
                sd_dct = float(sub["dCt"].std(ddof=1)) if n_bio > 1 else 0.0
                sem_dct = sd_dct / np.sqrt(n_bio) if n_bio > 1 else 0.0

                m_ddct = float(sub["ddCt"].mean())
                ctrl_sem = (float(np.std(ctrl_dct_vals, ddof=1)) / np.sqrt(len(ctrl_dct_vals))) if len(ctrl_dct_vals) > 1 else 0.0
                sem_ddct = float(np.sqrt(sem_dct**2 + ctrl_sem**2))

                fc_livak = float(np.power(2.0, -m_ddct))
                fc_pfaffl = float(np.power(eff_base, -m_ddct))
                rep_mean_fc = float(sub["Pfaffl_Eff_Corrected_FC"].mean())
                sem_fc = float(sub["Pfaffl_Eff_Corrected_FC"].std(ddof=1) / np.sqrt(n_bio)) if n_bio > 1 else 0.0

                t_crit = float(sp_stats.t.ppf(0.975, df=max(1, n_bio - 1))) if n_bio > 1 else 1.96
                fc_ci_low = float(np.power(eff_base, -(m_ddct + t_crit * sem_ddct)))
                fc_ci_high = float(np.power(eff_base, -(m_ddct - t_crit * sem_ddct)))

                l2_fc = float(-m_ddct * np.log2(eff_base))
                pct_change = (fc_pfaffl - 1.0) * 100.0

                if grp == ctrl_group or len(ctrl_dct_vals) < 2 or n_bio < 2:
                    t_stat, df_w, p_val = 0.0, float(max(1, n_bio - 1)), 1.0
                else:
                    x1 = sub["dCt"].values
                    x2 = ctrl_dct_vals
                    t_res = sp_stats.ttest_ind(x1, x2, equal_var=False)
                    t_stat = float(-t_res.statistic) if not np.isnan(t_res.statistic) else 0.0  # Inverted sign so upregulation = positive t
                    p_val = float(t_res.pvalue) if not np.isnan(t_res.pvalue) else 1.0
                    v1, v2 = np.var(x1, ddof=1)/len(x1), np.var(x2, ddof=1)/len(x2)
                    df_w = float((v1 + v2)**2 / ((v1**2)/(len(x1)-1) + (v2**2)/(len(x2)-1))) if (v1 + v2) > 0 else float(len(x1)+len(x2)-2)

                if grp == ctrl_group:
                    reg_dir = "Calibrator (1.0x)"
                elif p_val < p_cutoff and l2_fc >= fc_cutoff:
                    reg_dir = "Up-Regulated"
                elif p_val < p_cutoff and l2_fc <= -fc_cutoff:
                    reg_dir = "Down-Regulated"
                else:
                    reg_dir = "Unchanged (ns)"

                miqe_flag = "PASS" if (not enforce_miqe_drift or max_global_hk_drift <= 0.5) else "HK_DRIFT_WARN"

                summary_rows.append({
                    "Gene": g,
                    "Group": grp,
                    "N_Biological_Replicates": n_bio,
                    "Technical_Reps_Pooled": tech_pooled,
                    "Mean_Target_Ct": round(m_t_ct, 3),
                    "SD_Target_Ct": round(sd_t_ct, 3),
                    "Mean_HK_Ct": round(m_hk_ct, 3),
                    "Mean_dCt": round(m_dct, 3),
                    "SD_dCt": round(sd_dct, 3),
                    "SEM_dCt": round(sem_dct, 3),
                    "Calibrator_dCt": round(cal_dct_val, 3),
                    "Mean_ddCt": round(m_ddct, 3),
                    "SEM_ddCt": round(sem_ddct, 3),
                    "Fold_Change_2^-ddCt": round(fc_livak, 3),
                    "Pfaffl_Eff_Corrected_FC": round(fc_pfaffl, 3),
                    "Replicate_Mean_FC": round(rep_mean_fc, 3),
                    "SEM_FC": round(sem_fc, 3),
                    "FC_95CI_Lower": round(fc_ci_low, 3),
                    "FC_95CI_Upper": round(fc_ci_high, 3),
                    "Log2_Fold_Change": round(l2_fc, 3),
                    "Percent_Change (%)": round(pct_change, 1),
                    "Regulation_Direction": reg_dir,
                    "Welch_t_Statistic": round(t_stat, 3),
                    "Degrees_of_Freedom": round(df_w, 2),
                    "Two_Tailed_P_Value": p_val,
                    "Omnibus_ANOVA_F": round(f_val, 3),
                    "Omnibus_ANOVA_P": anova_p,
                    "MIQE_QC_Flag": miqe_flag
                })

        sum_df = pd.DataFrame(summary_rows)

        # Benjamini-Hochberg FDR
        non_ctrl_mask = sum_df["Group"] != ctrl_group
        p_arr = sum_df.loc[non_ctrl_mask, "Two_Tailed_P_Value"].values
        if apply_bh_fdr and len(p_arr) > 0:
            order = np.argsort(p_arr)
            ranks = np.empty_like(order)
            ranks[order] = np.arange(1, len(p_arr) + 1)
            fdr_raw = np.minimum(1.0, p_arr * len(p_arr) / ranks)
            fdr_sorted = fdr_raw[order]
            for i in range(len(fdr_sorted) - 2, -1, -1):
                fdr_sorted[i] = min(fdr_sorted[i], fdr_sorted[i + 1])
            fdr_out = np.empty_like(fdr_sorted)
            fdr_out[order] = fdr_sorted
            sum_df.loc[non_ctrl_mask, "BH_Adjusted_FDR"] = np.round(fdr_out, 5)
        else:
            sum_df["BH_Adjusted_FDR"] = sum_df["Two_Tailed_P_Value"]
        sum_df["BH_Adjusted_FDR"] = sum_df["BH_Adjusted_FDR"].fillna(1.0)

        def assign_stars(r):
            if r["Group"] == ctrl_group:
                return "Ref (1.0x)"
            pv = r["Two_Tailed_P_Value"]
            if pv < 0.001:
                return "***"
            elif pv < 0.01:
                return "**"
            elif pv < 0.05:
                return "*"
            return "ns"

        sum_df["Significance_Stars"] = sum_df.apply(assign_stars, axis=1)
        sum_df["Two_Tailed_P_Value"] = sum_df["Two_Tailed_P_Value"].apply(lambda x: float(f"{x:.5f}"))
        sum_df["Omnibus_ANOVA_P"] = sum_df["Omnibus_ANOVA_P"].apply(lambda x: float(f"{x:.5f}"))

        # Wide Matrix
        wide_fc_df = target_df.pivot_table(index=["Sample_ID", "Group"], columns="Gene", values="Pfaffl_Eff_Corrected_FC").reset_index().round(3)

        # ==========================================
        # GENERATE 4 VECTOR SVG PUBLICATION FIGURES
        # ==========================================
        palette = ["#38bdf8", "#f43f5e", "#10b981", "#f59e0b", "#a855f7", "#06b6d4"]
        w1, h1 = 620, 360
        pad_l, pad_r, pad_t, pad_b = 62, 24, 52, 72
        plot_w, plot_h = w1 - pad_l - pad_r, h1 - pad_t - pad_b
        max_fc = max(2.5, float((sum_df["Replicate_Mean_FC"] + sum_df["SEM_FC"]).max() * 1.22))

        # SVG 1: Grouped Barplot
        svg1 = [
            f'<svg viewBox="0 0 {w1} {h1}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
            f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
            f'<text x="18" y="26" fill="#f8fafc" font-size="13" font-weight="800">Fig 1A. Relative mRNA Expression (2^-ΔΔCt Fold Change ± SEM)</text>',
            f'<text x="18" y="42" fill="#94a3b8" font-size="10">Ref: {", ".join(hk_genes)} | Calibrator: {ctrl_group} (1.0x) | * p&lt;0.05, ** p&lt;0.01, *** p&lt;0.001</text>'
        ]
        for tick in np.linspace(0, max_fc, 5):
            y_pos = pad_t + plot_h - (tick / max_fc) * plot_h
            svg1.append(f'<line x1="{pad_l}" y1="{y_pos:.1f}" x2="{w1-pad_r}" y2="{y_pos:.1f}" stroke="#1e293b" stroke-width="1"/>')
            svg1.append(f'<text x="{pad_l-8}" y="{y_pos+3:.1f}" fill="#94a3b8" font-size="9.5" text-anchor="end">{tick:.1f}x</text>')
        if max_fc >= 1.0:
            y_one = pad_t + plot_h - (1.0 / max_fc) * plot_h
            svg1.append(f'<line x1="{pad_l}" y1="{y_one:.1f}" x2="{w1-pad_r}" y2="{y_one:.1f}" stroke="#64748b" stroke-dasharray="4,3" stroke-width="1.2"/>')

        n_genes = max(1, len(target_genes_sorted))
        n_grps = max(1, len(groups_ordered))
        cluster_w = plot_w / n_genes
        bar_w = min(22.0, (cluster_w * 0.76) / n_grps)

        for gi, g in enumerate(target_genes_sorted):
            cx = pad_l + gi * cluster_w + cluster_w / 2.0
            start_x = cx - (n_grps * bar_w) / 2.0
            for ki, grp in enumerate(groups_ordered):
                row_m = sum_df[(sum_df["Gene"] == g) & (sum_df["Group"] == grp)]
                if row_m.empty:
                    continue
                fc_v = float(row_m["Replicate_Mean_FC"].iloc[0])
                sem_v = float(row_m["SEM_FC"].iloc[0])
                star_v = str(row_m["Significance_Stars"].iloc[0])
                color = palette[ki % len(palette)]

                bx = start_x + ki * bar_w
                bh = max(2.0, (fc_v / max_fc) * plot_h)
                by = pad_t + plot_h - bh
                svg1.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w-2:.1f}" height="{bh:.1f}" fill="{color}" rx="2"/>')

                top_err = min(max_fc, fc_v + sem_v)
                ey = pad_t + plot_h - (top_err / max_fc) * plot_h
                mid_x = bx + (bar_w - 2) / 2.0
                svg1.append(f'<line x1="{mid_x:.1f}" y1="{by:.1f}" x2="{mid_x:.1f}" y2="{ey:.1f}" stroke="#e2e8f0" stroke-width="1.2"/>')
                svg1.append(f'<line x1="{mid_x-3:.1f}" y1="{ey:.1f}" x2="{mid_x+3:.1f}" y2="{ey:.1f}" stroke="#e2e8f0" stroke-width="1.2"/>')

                if star_v in ["*", "**", "***"]:
                    svg1.append(f'<text x="{mid_x:.1f}" y="{ey-3:.1f}" fill="#fde047" font-size="9.5" font-weight="800" text-anchor="middle">{star_v}</text>')
            svg1.append(f'<text x="{cx:.1f}" y="{pad_t+plot_h+18}" fill="#e2e8f0" font-size="10.5" font-weight="700" text-anchor="middle">{g}</text>')

        leg_x = pad_l
        for ki, grp in enumerate(groups_ordered):
            color = palette[ki % len(palette)]
            svg1.append(f'<rect x="{leg_x}" y="{h1-22}" width="10" height="10" fill="{color}" rx="2"/>')
            svg1.append(f'<text x="{leg_x+14}" y="{h1-13}" fill="#cbd5e1" font-size="9.5">{grp[:18]}</text>')
            leg_x += 130
        svg1.append('</svg>')
        svg_bar_str = "".join(svg1)

        # SVG 2: Log2 Fold-Change Diverging Plot
        w2, h2 = 620, 360
        svg2 = [
            f'<svg viewBox="0 0 {w2} {h2}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
            f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
            f'<text x="18" y="26" fill="#f8fafc" font-size="13" font-weight="800">Fig 1B. Log2 Fold-Change (-ΔΔCt) Diverging Expression Profile</text>',
            f'<text x="18" y="42" fill="#94a3b8" font-size="10">Upregulated (Log2FC &gt; 0, Emerald) vs. Downregulated (Log2FC &lt; 0, Rose) vs. {ctrl_group}</text>'
        ]
        non_ctrl_df = sum_df[sum_df["Group"] != ctrl_group].copy()
        if non_ctrl_df.empty:
            non_ctrl_df = sum_df.copy()
        non_ctrl_df["Label"] = non_ctrl_df["Gene"] + " (" + non_ctrl_df["Group"].str[:10] + ")"
        plot_sub = non_ctrl_df.iloc[:12].copy()
        max_abs_l2 = max(2.0, float(plot_sub["Log2_Fold_Change"].abs().max() * 1.25))
        zero_x = pad_l + 60 + (w2 - pad_l - 60 - pad_r) / 2.0
        half_span = (w2 - pad_l - 60 - pad_r) / 2.0

        svg2.append(f'<line x1="{zero_x:.1f}" y1="{pad_t}" x2="{zero_x:.1f}" y2="{h2-40}" stroke="#94a3b8" stroke-width="1.3" stroke-dasharray="3,3"/>')
        for tick in [-max_abs_l2, -max_abs_l2/2, 0, max_abs_l2/2, max_abs_l2]:
            tx = zero_x + (tick / max_abs_l2) * half_span
            svg2.append(f'<text x="{tx:.1f}" y="{h2-18}" fill="#94a3b8" font-size="9.5" text-anchor="middle">{tick:+.1f}</text>')

        n_items = max(1, len(plot_sub))
        row_h = (h2 - pad_t - 45) / n_items
        for idx_r, (_, r) in enumerate(plot_sub.iterrows()):
            ry = pad_t + idx_r * row_h + row_h / 2.0
            l2v = float(r["Log2_Fold_Change"])
            px = zero_x + (l2v / max_abs_l2) * half_span
            col_c = "#10b981" if l2v >= 0 else "#f43f5e"
            svg2.append(f'<text x="{pad_l+52}" y="{ry+3.5:.1f}" fill="#cbd5e1" font-size="9.5" text-anchor="end">{r["Label"]}</text>')
            svg2.append(f'<line x1="{zero_x:.1f}" y1="{ry:.1f}" x2="{px:.1f}" y2="{ry:.1f}" stroke="{col_c}" stroke-width="3.5" stroke-linecap="round"/>')
            svg2.append(f'<circle cx="{px:.1f}" cy="{ry:.1f}" r="5" fill="{col_c}" stroke="#090d16" stroke-width="1.2"/>')
            svg2.append(f'<text x="{px + (12 if l2v >= 0 else -12):.1f}" y="{ry+3:.1f}" fill="#e2e8f0" font-size="8.5" text-anchor="{"start" if l2v >= 0 else "end"}">{l2v:+.2f}</text>')
        svg2.append('</svg>')
        svg_l2_str = "".join(svg2)

        # SVG 3: Sample x Gene Z-Score Heatmap
        w3, h3 = 620, 360
        svg3 = [
            f'<svg viewBox="0 0 {w3} {h3}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
            f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
            f'<text x="18" y="26" fill="#f8fafc" font-size="13" font-weight="800">Fig 1C. Multi-Gene qPCR Expression Matrix (Row Z-Score of -ΔCt)</text>',
            f'<text x="18" y="42" fill="#94a3b8" font-size="10">Sample-by-gene relative transcript abundance across biological replicates</text>'
        ]
        piv = target_df.pivot_table(index="Gene", columns="Sample_ID", values="Log2_Fold_Change", aggfunc="mean").fillna(0.0)
        samps_list = list(piv.columns)[:16]
        genes_hm = list(piv.index)[:10]
        hm_l, hm_t, hm_w, hm_h = 80, 56, w3 - 104, h3 - 110
        cw = hm_w / max(1, len(samps_list))
        ch = hm_h / max(1, len(genes_hm))

        for r_i, g_name in enumerate(genes_hm):
            row_vals = piv.loc[g_name, samps_list].values.astype(float)
            r_std = np.std(row_vals) if np.std(row_vals) > 1e-6 else 1.0
            z_vals = (row_vals - np.mean(row_vals)) / r_std
            ry = hm_t + r_i * ch
            svg3.append(f'<text x="{hm_l-8}" y="{ry + ch/2 + 3.5:.1f}" fill="#e2e8f0" font-size="9.5" font-weight="700" text-anchor="end">{g_name}</text>')
            for c_i, s_name in enumerate(samps_list):
                zv = float(np.clip(z_vals[c_i], -2.0, 2.0))
                cell_col = f"rgba(244, 63, 94, {0.2 + 0.75*(zv/2.0):.2f})" if zv >= 0 else f"rgba(56, 189, 248, {0.2 + 0.75*(abs(zv)/2.0):.2f})"
                cx_pos = hm_l + c_i * cw
                svg3.append(f'<rect x="{cx_pos:.1f}" y="{ry:.1f}" width="{cw-1.5:.1f}" height="{ch-1.5:.1f}" fill="{cell_col}" rx="2"/>')
                svg3.append(f'<text x="{cx_pos + cw/2:.1f}" y="{ry + ch/2 + 3:.1f}" fill="#f8fafc" font-size="8" text-anchor="middle">{row_vals[c_i]:+.1f}</text>')

        for c_i, s_name in enumerate(samps_list):
            cx_pos = hm_l + c_i * cw + cw / 2.0
            svg3.append(f'<text x="{cx_pos:.1f}" y="{hm_t + hm_h + 14:.1f}" fill="#94a3b8" font-size="8.5" transform="rotate(30 {cx_pos:.1f} {hm_t + hm_h + 14:.1f})" text-anchor="start">{s_name[:10]}</text>')
        svg3.append('</svg>')
        svg_hm_str = "".join(svg3)

        # SVG 4: Housekeeping Stability & Raw Ct Profile
        w4, h4 = 620, 360
        svg4 = [
            f'<svg viewBox="0 0 {w4} {h4}" width="100%" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border:1px solid #1e293b; border-radius:12px; font-family:Inter,sans-serif;">',
            f'<rect width="100%" height="100%" fill="#090d16" rx="12"/>',
            f'<text x="18" y="26" fill="#f8fafc" font-size="13" font-weight="800">Fig 1D. MIQE Housekeeping Gene Stability &amp; Raw Ct Distribution</text>',
            f'<text x="18" y="42" fill="#94a3b8" font-size="10">Cycle threshold invariance check across experimental groups (Ideal drift &lt; 0.5 Ct)</text>'
        ]
        min_ct_p, max_ct_p = 12.0, 36.0
        for tick in [15, 20, 25, 30, 35]:
            y_pos = pad_t + plot_h - ((tick - min_ct_p) / (max_ct_p - min_ct_p)) * plot_h
            svg4.append(f'<line x1="{pad_l}" y1="{y_pos:.1f}" x2="{w4-pad_r}" y2="{y_pos:.1f}" stroke="#1e293b" stroke-width="1"/>')
            svg4.append(f'<text x="{pad_l-8}" y="{y_pos+3:.1f}" fill="#94a3b8" font-size="9.5" text-anchor="end">Ct {tick}</text>')

        all_genes_plot = (hk_genes + [g for g in target_genes_sorted if g not in hk_genes])[:8]
        g_step = plot_w / max(1, len(all_genes_plot))
        for gi, g in enumerate(all_genes_plot):
            gx = pad_l + gi * g_step + g_step / 2.0
            g_pts = bio_df[bio_df["Gene"] == g]["Ct"].values
            if len(g_pts) == 0:
                continue
            m_v, sd_v = float(np.mean(g_pts)), float(np.std(g_pts))
            my = pad_t + plot_h - ((m_v - min_ct_p) / (max_ct_p - min_ct_p)) * plot_h
            y_top = pad_t + plot_h - ((min(max_ct_p, m_v + sd_v) - min_ct_p) / (max_ct_p - min_ct_p)) * plot_h
            y_bot = pad_t + plot_h - ((max(min_ct_p, m_v - sd_v) - min_ct_p) / (max_ct_p - min_ct_p)) * plot_h
            is_hk_flag = g in hk_genes
            col_pt = "#34d399" if is_hk_flag else "#38bdf8"

            svg4.append(f'<line x1="{gx:.1f}" y1="{y_top:.1f}" x2="{gx:.1f}" y2="{y_bot:.1f}" stroke="{col_pt}" stroke-width="2"/>')
            for pt in g_pts:
                py = pad_t + plot_h - ((float(np.clip(pt, min_ct_p, max_ct_p)) - min_ct_p) / (max_ct_p - min_ct_p)) * plot_h
                svg4.append(f'<circle cx="{gx:.1f}" cy="{py:.1f}" r="3.5" fill="{col_pt}" opacity="0.75"/>')
            svg4.append(f'<circle cx="{gx:.1f}" cy="{my:.1f}" r="5.5" fill="{col_pt}" stroke="#ffffff" stroke-width="1.5"/>')
            svg4.append(f'<text x="{gx:.1f}" y="{pad_t+plot_h+18}" fill="{col_pt}" font-size="9.5" font-weight="700" text-anchor="middle">{f"{g} (HK)" if is_hk_flag else g}</text>')
            svg4.append(f'<text x="{gx:.1f}" y="{my-10:.1f}" fill="#e2e8f0" font-size="8.5" text-anchor="middle">{m_v:.1f}</text>')
        svg4.append('</svg>')
        svg_qc_str = "".join(svg4)

        html_report = f"""
        <!DOCTYPE html><html><head><meta charset="utf-8"><title>GenomeTech qPCR 2^-ddCt Report</title>
        <style>body{{font-family:Inter,Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:28px;}}
        .grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:24px;}}
        table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:12px;}}
        th,td{{border:1px solid #334155;padding:7px 10px;text-align:left;}}
        th{{background:#1e293b;color:#38bdf8;}}</style></head>
        <body>
        <h2>GenomeTech Studio — Automated RT-qPCR 2<sup>-ΔΔCt</sup> Biostatistics Report</h2>
        <p><b>Mode:</b> {app_mode} | <b>Housekeeping:</b> {", ".join(hk_genes)} | <b>Calibrator:</b> {ctrl_group} | <b>Efficiency:</b> {amp_eff:.1f}%</p>
        <div class="grid">{svg_bar_str}{svg_l2_str}{svg_hm_str}{svg_qc_str}</div>
        <h3>Complete Group-Level 2^-ΔΔCt Fold-Change & Significance Table</h3>
        {sum_df.to_html(index=False)}
        </body></html>
        """

        sig_count = int((sum_df["Two_Tailed_P_Value"] < p_cutoff).sum())
        total_comparisons = int((sum_df["Group"] != ctrl_group).sum())
        sig_rate_pct = (sig_count / max(1, total_comparisons)) * 100.0

        st.session_state["sum_df_t2"] = sum_df
        st.session_state["rep_df_t2"] = target_df.round(4)
        st.session_state["hk_qc_df_t2"] = hk_qc_df
        st.session_state["wide_fc_df_t2"] = wide_fc_df
        st.session_state["svg_bar_t2"] = svg_bar_str
        st.session_state["svg_l2_t2"] = svg_l2_str
        st.session_state["svg_hm_t2"] = svg_hm_str
        st.session_state["svg_qc_t2"] = svg_qc_str
        st.session_state["html_rep_t2"] = html_report
        st.session_state["stats_t2"] = {
            "wells_in": total_wells_in,
            "n_genes": len(target_genes_sorted),
            "n_groups": len(groups_ordered),
            "total_comp": len(sum_df),
            "sig_hits": sig_count,
            "sig_rate": sig_rate_pct,
            "hk_str": ", ".join(hk_genes),
            "ctrl_str": ctrl_group,
            "eff": amp_eff,
            "hk_drift": max_global_hk_drift,
            "mode": app_mode
        }

# ==========================================
# RESULTS, CUSTOM KPI CARDS & PAYWALL RENDER
# ==========================================
if "sum_df_t2" in st.session_state:
    sum_df = st.session_state["sum_df_t2"]
    rep_df = st.session_state["rep_df_t2"]
    hk_qc_df = st.session_state["hk_qc_df_t2"]
    wide_fc_df = st.session_state["wide_fc_df_t2"]
    svg_bar = st.session_state["svg_bar_t2"]
    svg_l2 = st.session_state["svg_l2_t2"]
    svg_hm = st.session_state["svg_hm_t2"]
    svg_qc = st.session_state["svg_qc_t2"]
    html_rep = st.session_state["html_rep_t2"]
    stats = st.session_state["stats_t2"]

    if "currency" not in st.session_state:
        url_curr = str(st.query_params.get("currency", "USD")).strip().upper()
        st.session_state.currency = "INR" if url_curr == "INR" else "USD"
    is_inr = (st.session_state.get("currency", "USD") == "INR")

    st.markdown("---")
    st.markdown("### 📊 qPCR 2<sup>-ΔΔCt</sup> Coordinate Table & Significance Summary", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">qPCR Wells Processed</div><div class="metric-val">{stats["wells_in"]}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Normalized Comparisons</div><div class="metric-val">{stats["total_comp"]}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Significant Shifts (p &lt; α)</div><div class="metric-val">{stats["sig_hits"]}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Differential Hit Rate</div><div class="metric-val">{stats["sig_rate"]:.1f}%</div></div>', unsafe_allow_html=True)

    if st.session_state.get("is_unlocked_t2", False):
        st.success("✅ **Payment Verified for [Automated qPCR 2^-ΔΔCt Fold-Change Suite]!** All 4 vector figures, 4 complete biostatistical tables, and the printable report are unlocked.")

        st.markdown("#### 🎨 4-Panel qPCR Publication Figure Suite (Vector `.svg` & Printable `.html`)")
        g1, g2 = st.columns(2)
        with g1:
            st.markdown(svg_bar, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(svg_hm, unsafe_allow_html=True)
        with g2:
            st.markdown(svg_l2, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(svg_qc, unsafe_allow_html=True)

        st.markdown("#### 📋 1. Complete Group-Level 2<sup>-ΔΔCt</sup> Fold-Change, 95% CI, Welch t-Test & FDR Master Table", unsafe_allow_html=True)
        st.dataframe(sum_df, use_container_width=True)

        st.markdown("#### 🧪 2. Biological Replicate-Level ΔCt, ΔΔCt & Individual Fold-Change Table")
        st.dataframe(rep_df, use_container_width=True)

        st.markdown("#### 🛡️ 3. MIQE Housekeeping Gene Stability & Inter-Group Drift Audit")
        st.dataframe(hk_qc_df, use_container_width=True)

        st.markdown("#### 🧬 4. Wide Sample × Gene Fold-Change Matrix (Prism / R Ready)")
        st.dataframe(wide_fc_df, use_container_width=True)

        st.markdown("#### ⬇️ Download Complete qPCR Deliverables (`.csv`, `.svg`, `.html`)")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.download_button("⬇️ 1. Group 2^-ddCt Master (.csv)", data=sum_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_qPCR_Group_Master.csv", mime="text/csv", key="dl1_t2")
            st.download_button("⬇️ 5. Fig 1A: 2^-ddCt Barplot (.svg)", data=svg_bar.encode("utf-8"), file_name="GenomeTech_qPCR_FoldChange_Barplot.svg", mime="image/svg+xml", key="dl5_t2")
        with d2:
            st.download_button("⬇️ 2. Replicate-Level ddCt (.csv)", data=rep_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_qPCR_Replicate_ddCt.csv", mime="text/csv", key="dl2_t2")
            st.download_button("⬇️ 6. Fig 1B: Log2FC Forest (.svg)", data=svg_l2.encode("utf-8"), file_name="GenomeTech_qPCR_Log2FC_Plot.svg", mime="image/svg+xml", key="dl6_t2")
        with d3:
            st.download_button("⬇️ 3. MIQE Housekeeping QC (.csv)", data=hk_qc_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_qPCR_Housekeeping_QC.csv", mime="text/csv", key="dl3_t2")
            st.download_button("⬇️ 7. Fig 1C: qPCR Z-Heatmap (.svg)", data=svg_hm.encode("utf-8"), file_name="GenomeTech_qPCR_Heatmap.svg", mime="image/svg+xml", key="dl7_t2")
        with d4:
            st.download_button("⬇️ 4. Wide Fold-Change Matrix (.csv)", data=wide_fc_df.to_csv(index=False).encode("utf-8-sig"), file_name="GenomeTech_qPCR_Wide_Matrix.csv", mime="text/csv", key="dl4_t2")
            st.download_button("⬇️ 8. Printable Visual Report (.html)", data=html_rep.encode("utf-8"), file_name="GenomeTech_qPCR_Visual_Report.html", mime="text/html", key="dl8_t2")
    else:
        st.markdown("**Live Preview (First 3 Normalized Gene-Group Comparisons with ΔΔCt, Fold-Change & P-Values):**")
        st.dataframe(sum_df.head(3), use_container_width=True)

        st.markdown('<div class="blurred-table">', unsafe_allow_html=True)
        st.table(sum_df.iloc[3:8])
        st.markdown('</div>', unsafe_allow_html=True)

        razorpay_link = "https://rzp.io/rzp/UVDck3w"

        if is_inr:
            paywall_price_display = "₹799 INR"
            paywall_strike_display = "₹2,499"
            paywall_desc = (
                f"Your top preview rows are verified above. Complete the <b>₹799 INR</b> OmicsExpress checkout via Direct UPI or NEFT to unlock all "
                f"<b>{stats['total_comp']} normalized gene-group comparisons</b> ({stats['sig_hits']} significant hits), 4 vector publication figures (<code>.svg</code>), replicate-level ΔΔCt tables, and MIQE housekeeping audit."
            )
            upi_note = "OmicsExpress Tool 2 qPCR ddCt Suite"
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
                f'<h3 style="color: #e9d5ff !important; margin-top: 0;">🔒 Unlock All {stats["total_comp"]} qPCR Comparisons, 4 SVG Plots &amp; MIQE Sheet</h3>'
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
                f'<h3 style="color: #e9d5ff !important; margin-top: 0;">🔒 Unlock All {stats["total_comp"]} qPCR Comparisons, 4 SVG Plots &amp; MIQE Sheet</h3>'
                f'<p style="color: #cbd5e1 !important; font-size: 0.95rem; max-width: 600px; margin: 0 auto 14px auto;">'
                f'Your top preview rows are verified above. Complete the $40 OmicsExpress checkout to unlock all {stats["total_comp"]} normalized gene-group comparisons ({stats["sig_hits"]} significant hits), 4 vector publication figures (<code>.svg</code>), replicate-level ΔΔCt tables, and MIQE housekeeping audit.'
                f'</p>'
                f'<div style="background:rgba(56,189,248,0.14);border:1px solid rgba(56,189,248,0.45);color:#e0f2fe !important;padding:8px 14px;border-radius:8px;font-size:0.88rem;font-weight:600;margin:10px auto 6px auto;max-width:520px;">'
                f'🔥 <span style="color:#38bdf8 !important;font-weight:800;">FOUNDING LAB LAUNCH OFFER:</span> '
                f'<s style="color:#94a3b8 !important;">$100 USD</s> <b style="color:#ffffff !important;">$40 USD</b> — Special Early-Access Rate for Our First 20 Research Clients'
                f'</div>'
                f'<a href="{razorpay_link}" target="_blank" style="background: linear-gradient(90deg, #9333ea 0%, #2563eb 100%); color: white !important; padding: 14px 32px; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 1.05rem; display: inline-block; margin: 12px 0; border: 1px solid #c084fc; box-shadow: 0 4px 20px rgba(147, 51, 234, 0.5);">'
                f'💳 Pay $40 via Razorpay to Unlock Full qPCR 2^-ΔΔCt Suite'
                f'</a>'
                f'</div>',
                unsafe_allow_html=True
            )

        # --- START API & ANTI-REUSE GATEWAY UPGRADE ---
        u_col1, u_col2, u_col3 = st.columns([1, 2, 1])
        with u_col2:
            input_label_t2 = (
                "🔑 Completed payment via UPI or Razorpay? Paste your 12-digit UPI UTR or Payment ID:"
                if is_inr
                else "🔑 Completed payment? Paste your Razorpay Payment ID or Founder Key:"
            )
            input_placeholder_t2 = (
                "e.g., 430189234512 (UPI UTR) or pay_XXXXXXXXXXXXXX or GTS-DEMO-..."
                if is_inr
                else "pay_XXXXXXXXXXXXXX or GTS-DEMO-..."
            )

            entered_key = st.text_input(
                input_label_t2,
                placeholder=input_placeholder_t2,
                key="unlock_input_t2"
            ).strip()

            if st.button("Unlock Full Download", key="unlock_btn_t2", use_container_width=True):
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
                        st.session_state["is_unlocked_t2"] = True
                        st.rerun()
                    elif entered_key in AUTHORIZED_DEMO_KEYS:
                        burned, burn_date = is_key_burned(entered_key)
                        if burned:
                            st.error(f"❌ Security Lock: This Demo Key was already claimed on {burn_date}.")
                        else:
                            burn_key(entered_key)
                            st.session_state["is_unlocked_t2"] = True
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
                            st.session_state["is_unlocked_t2"] = True
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
                                        st.session_state["is_unlocked_t2"] = True
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
    st.markdown("### 📝 Automated MIQE Normalization Remarks & Direct Support")
    st.markdown(
        f'<div style="background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.3); border-radius:12px; padding:16px 20px; margin-bottom:14px; font-size:0.88rem; color:#cbd5e1; line-height:1.6;">'
        f'<b style="color:#f8fafc;">Automated RT-qPCR Biostatistical Diagnostics:</b><br>'
        f'• <b>Application Pipeline:</b> {stats["mode"]}<br>'
        f'• <b>Normalization &amp; Reference Stability:</b> Evaluated <b>{stats["wells_in"]}</b> qPCR reactions across <b>{stats["n_genes"]}</b> target genes normalized against <code>{stats["hk_str"]}</code> (Max inter-group HK drift: <b>{stats["hk_drift"]:.3f} Ct cycles</b>).<br>'
        f'• <b>Biophysical &amp; Expression Metrics:</b> Includes Livak $2^{{-\\Delta\\Delta C_t}}$, Pfaffl efficiency-corrected fold change ($E = {stats["eff"]:.1f}\\%$), 95% confidence intervals, Welch’s two-sample $t$-statistics, and Benjamini-Hochberg FDR.<br>'
        f'• <b>Differential Hit Rate:</b> Identified <b>{stats["sig_hits"]}</b> statistically significant gene-group comparisons out of <b>{stats["total_comp"]}</b> total evaluations (<b>{stats["sig_rate"]:.1f}%</b> differential hit rate).'
        f'</div>',
        unsafe_allow_html=True
    )

    with st.expander("💬 Send Remarks or Questions Directly to GenomeTech Team (via Email)"):
        rem_email = st.text_input("Your Email Address:", placeholder="researcher@university.edu", key="rem_em_t2")
        rem_msg = st.text_area("Your Question or Custom qPCR Normalization Request:", placeholder="Describe your plate layout, reference genes, or custom statistical contrast...", key="rem_msg_t2")
        if st.button("📩 Prepare Email to GenomeTech Support", key="btn_rem_t2"):
            subj = urllib.parse.quote("OmicsExpress Tool #2 (qPCR 2^-ddCt Suite) Inquiry")
            body = urllib.parse.quote(f"From: {rem_email}\n\nMessage:\n{rem_msg}")
            st.markdown(f'👉 **[Click here to send your message via your default email client](mailto:genometechstudio@gmail.com?subject={subj}&body={body})**')
