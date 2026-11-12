import streamlit as st
import os 

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="OmicsExpress Automated Suite | GenomeTech Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. GLOBAL SIDEBAR HIDING & COSMIC THEME CSS (APPLIES TO HUB & ALL 8 TOOLS)
# ==========================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .stApp {
        background: radial-gradient(circle at top right, #2e1065 0%, #1e1b4b 40%, #0f172a 80%, #090d16 100%);
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, p, span, label, li {
        color: #f1f5f9 !important;
    }

    .gts-navbar {
        background: linear-gradient(90deg, #1e1b4b 0%, #4c1d95 50%, #1e3a8a 100%);
        padding: 1.4rem 2.2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        border: 1px solid rgba(168, 85, 247, 0.45);
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
    }
    .gts-brand {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #ffffff !important;
        text-decoration: none;
        transition: opacity 0.2s ease;
        cursor: pointer;
    }
    .gts-brand:hover {
        opacity: 0.85;
    }
    .gts-sub {
        color: #38bdf8 !important;
        margin-left: 12px;
        font-size: 1rem;
        font-weight: 600;
    }
    .gts-badge {
        background: linear-gradient(135deg, #7c3aed, #2563eb);
        border: 1px solid #c084fc;
        color: #ffffff !important;
        padding: 7px 18px;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.5);
    }
    .top-nav-btn {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.4);
        color: #f8fafc !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        text-decoration: none !important;
        display: inline-block;
    }
    .top-nav-btn:hover {
        border-color: #38bdf8;
        background: rgba(51, 65, 85, 0.9);
    }

    .tool-card {
        background: rgba(30, 27, 75, 0.65);
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 0.8rem;
        min-height: 185px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .tool-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.35);
        border-color: rgba(168, 85, 247, 0.7);
    }

    .tool-tag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.45);
        color: #38bdf8 !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 8px;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #7c3aed 0%, #2563eb 100%) !important;
        color: white !important;
        border: 1px solid #a855f7 !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        margin-bottom: 1.4rem !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 22px rgba(168, 85, 247, 0.65) !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DUAL CURRENCY STATE INITIALIZATION (USD <-> INR)
# ==========================================
query_curr = str(st.query_params.get("currency", "USD")).strip().upper()
if "currency" not in st.session_state:
    st.session_state.currency = "INR" if query_curr == "INR" else "USD"

is_inr = (st.session_state.currency == "INR")
curr_param = "INR" if is_inr else "USD"

# ==========================================
# 4. DIRECT-EXECUTION ROUTER (WITH TOP BAR FOR TOOLS 1-8)
# ==========================================
TOOL_MAP = {
    "1": "pages/tool1_gene_translator.py",
    "2": "pages/tool2_primer_designing.py",
    "3": "pages/tool3_vcf_to_csv.py",
    "4": "pages/tool4_variant_susceptibility.py",
    "5": "pages/tool5_bulk_fasta_fetcher.py",
    "6": "pages/tool6_clinical_genomic_merger.py",
    "7": "pages/tool7_anova_posthoc.py",
    "8": "pages/tool8_kaplan_meier.py"
}

query_params = st.query_params
if "tool" in query_params:
    target_key = str(query_params["tool"]).strip().lower()
    if target_key in TOOL_MAP:
        target_file = TOOL_MAP[target_key]
        if os.path.exists(target_file):
            # Top navigation & currency bar across all 8 tools (Only Back to Website + Currency)
            t_nav_l, t_nav_r = st.columns([2.6, 1.4])
            with t_nav_l:
                st.markdown(
                    f'<div style="display:flex; gap:10px; align-items:center; padding-top:4px; margin-bottom:10px;">'
                    f'<a href="https://genometechstudio.github.io?currency={curr_param}" target="_self" class="top-nav-btn">← Back to Our Website</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with t_nav_r:
                top_curr = st.radio(
                    "Pricing Currency",
                    options=["USD", "INR"],
                    index=1 if is_inr else 0,
                    format_func=lambda x: "🌐 Global ($ USD)" if x == "USD" else "🇮🇳 India (₹ INR • Direct UPI)",
                    horizontal=True,
                    label_visibility="collapsed",
                    key="global_tool_top_curr"
                )
                if top_curr != st.session_state.currency:
                    st.session_state.currency = top_curr
                    st.query_params["currency"] = top_curr
                    st.rerun()

            with open(target_file, "r", encoding="utf-8") as f:
                code_content = f.read()
            exec(code_content, {"__name__": "__main__", "__file__": target_file})
            st.stop()

# ==========================================
# 5. MAIN OMICSEXPRESS HUB HEADER & TOP CURRENCY SWITCHER
# ==========================================
price_display = "₹799 INR" if is_inr else "$40 USD"
strike_display = "₹2,499" if is_inr else "$100"
badge_suffix = "0% Fee Direct UPI" if is_inr else "First 20 Clients"

hub_top_l, hub_top_r = st.columns([2.5, 1.5])
with hub_top_l:
    st.markdown(
        f'<div style="padding-top:4px; margin-bottom:8px;">'
        f'<a href="https://genometechstudio.github.io?currency={curr_param}" target="_self" class="top-nav-btn">← Back to Our Website</a>'
        f'</div>',
        unsafe_allow_html=True
    )
with hub_top_r:
    hub_curr = st.radio(
        "Select Pricing Mode:",
        options=["USD", "INR"],
        index=1 if is_inr else 0,
        format_func=lambda x: "🌐 Global ($ USD)" if x == "USD" else "🇮🇳 India (₹ INR • 0% Fee UPI)",
        horizontal=True,
        label_visibility="collapsed",
        key="omics_hub_top_curr_radio"
    )
    if hub_curr != st.session_state.currency:
        st.session_state.currency = hub_curr
        try:
            st.query_params["currency"] = hub_curr
        except Exception:
            pass
        st.rerun()

navbar_html = (
    '<div class="gts-navbar">'
    '<div>'
    f'<a href="https://genometechstudio.github.io?currency={curr_param}" class="gts-brand" style="text-decoration: none;">&#129516; GenomeTech Studio</a>'
    '<span class="gts-sub">| OmicsExpress Automated Bioinformatics Suite</span>'
    '</div>'
    f'<span class="gts-badge">&#128293; Founding Lab Offer: <s>{strike_display}</s> {price_display} ({badge_suffix})</span>'
    '</div>'
)
st.markdown(navbar_html, unsafe_allow_html=True)

# ==========================================
# 6. DASHBOARD 8-TOOL CARD GRID (UPDATED NAMES FOR TOOLS 2, 4 & 5)
# ==========================================
st.markdown("### 🚀 Select an Automated Micro-Tool Pipeline to Launch")
st.markdown(
    "All 8 tools include **live dataset previews**, **built-in demo datasets**, **cross-platform Windows & macOS Excel compatibility (`UTF-8-BOM`)**, "
    "and **instant self-serve unlock**."
)

TOOLS_META = [
    ("Tool #1 • Nomenclature & Annotation", "🧬 Universal Gene ID Translator",
     "Convert up to 50,000 Ensembl, Symbol, or Entrez IDs across model organisms with genomic coordinates, UniProt links & Excel date-corruption guard.",
     "1", "Launch Tool #1: Gene ID Translator"),
    ("Tool #2 • Wet-Lab RT-qPCR Biostatistics", "🧪 Automated qPCR 2^-ΔΔCt Fold-Change Suite",
     "Compute housekeeping ΔCt normalization, calibrator ΔΔCt shifts, Livak 2^-ΔΔCt & Pfaffl fold change, Welch t-test / FDR P-values, MIQE QC & 4 SVG plots.",
     "2", "Launch Tool #2: qPCR 2^-ΔΔCt Suite"),
    ("Tool #3 • NGS Variant Calling", "📄 VCF to Clinical CSV Converter",
     "Unpack complex multi-sample .vcf files into clean Excel tables with Genotype, Read Depth (DP), VAF %, SnpEff/VEP impact, and ClinVar calls.",
     "3", "Launch Tool #3: VCF to Clinical CSV"),
    ("Tool #4 • Functional Enrichment & ORA", "🕸️ GO & KEGG Pathway Bubble Plotter",
     "Run exact Hypergeometric Over-Representation Analysis (ORA) across KEGG, GO (BP/MF/CC) & Reactome with BH-FDR, GeneRatio bubble plots & network matrices.",
     "4", "Launch Tool #4: GO & KEGG Pathway Suite"),
    ("Tool #5 • Pharmacology & Cytotoxicity", "💊 IC50 / EC50 Dose-Response (4PL) Suite",
     "Fit exact 4-Parameter Logistic (4PL) sigmoidal Hill curves for MTT, CCK-8 & DPPH assays with IC50/IC90 95% CIs, R², Selectivity Index (SI) & 4 SVG plots.",
     "5", "Launch Tool #5: IC50 / EC50 4PL Suite"),
    ("Tool #6 • Translational Data Curation", "🔗 Clinical & Genomic Dataset Merger",
     "Harmonize mismatched patient chart IDs and RNA-seq sample barcodes, rescue tumor/normal specimen tags, and output DESeq2-synchronized matrices.",
     "6", "Launch Tool #6: Clinical & Genomic Merger"),
    ("Tool #7 • Biostatistics & Figures", "📊 Automated ANOVA, Post-Hoc & 4-Plot Suite",
     "Run One-Way ANOVA, Welch's, or Kruskal-Wallis with Tukey/Games-Howell/Dunn Post-Hoc tests, Shapiro-Wilk/Levene audits & 4 vector SVG figures.",
     "7", "Launch Tool #7: ANOVA & Post-Hoc Suite"),
    ("Tool #8 • Clinical Survival Oncology", "📈 Kaplan-Meier Survival & HR Suite",
     "Generate annotated survival curves with 95% CI ribbons, Number-at-Risk tables, Mantel-Cox Log-Rank P-values, RMST, and batch Hazard Ratio screens.",
     "8", "Launch Tool #8: Kaplan-Meier Plotter")
]

for row_idx in range(0, 8, 2):
    cols = st.columns(2)
    for col_idx in range(2):
        tag, title, desc, tool_id, btn_label = TOOLS_META[row_idx + col_idx]
        with cols[col_idx]:
            st.markdown(f"""
            <div class="tool-card">
                <span class="tool-tag">{tag}</span>
                <h4 style="margin: 4px 0 8px 0; color: #ffffff !important;">{title}</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1 !important; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(btn_label, key=f"btn_{row_idx + col_idx}"):
                st.query_params["tool"] = tool_id
                st.query_params["currency"] = curr_param
                st.rerun()
