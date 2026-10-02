import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tier 5 Live Showcase | Microbiome (16S rRNA Profiling)",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LIVE LINKS ---
MAIN_WEBSITE_URL = "https://genometechstudio.github.io"
CHECKOUT_TIER5_URL = "https://genometech-checkout.streamlit.app/?tier=5"

# --- BLUISH & REDDISH THEME + SINGLE CENTER MOVING TIER 5 LOGO ---
st.markdown(
    '<style>'
    '.stApp {'
    '  background: radial-gradient(circle at 50% 35%, #172a54 0%, #091326 55%, #040812 100%);'
    '  color: #f8fafc;'
    '  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'
    '}'
    'section[data-testid="stSidebar"] {'
    '  background-color: rgba(5, 10, 22, 0.96) !important;'
    '  border-right: 1px solid rgba(239, 68, 68, 0.35);'
    '}'
    '@keyframes floatCenterTier5 {'
    '  0% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '  50% { transform: translate(-50%, -50%) translateY(-22px) scale(1.06) rotate(5deg); opacity: 0.22; }'
    '  100% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '}'
    '.center-tier5-logo {'
    '  position: fixed;'
    '  top: 52%;'
    '  left: 50%;'
    '  font-size: 13rem;'
    '  pointer-events: none;'
    '  z-index: 0;'
    '  user-select: none;'
    '  filter: drop-shadow(0 0 35px rgba(239, 68, 68, 0.55)) drop-shadow(0 0 60px rgba(59, 130, 246, 0.4));'
    '  animation: floatCenterTier5 10s ease-in-out infinite;'
    '}'
    '.t5-card {'
    '  background: rgba(11, 24, 48, 0.84);'
    '  backdrop-filter: blur(14px);'
    '  border: 1px solid rgba(239, 68, 68, 0.38);'
    '  padding: 1.4rem 1.6rem;'
    '  border-radius: 16px;'
    '  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.5);'
    '  margin-bottom: 1.1rem;'
    '  position: relative;'
    '  z-index: 1;'
    '}'
    '.t5-kpi {'
    '  background: linear-gradient(135deg, rgba(15, 32, 66, 0.92), rgba(127, 29, 29, 0.28));'
    '  border: 1px solid rgba(244, 63, 94, 0.45);'
    '  padding: 1.15rem;'
    '  border-radius: 14px;'
    '  text-align: center;'
    '  position: relative;'
    '  z-index: 1;'
    '}'
    '.nav-btn-back {'
    '  display: inline-flex;'
    '  align-items: center;'
    '  justify-content: center;'
    '  gap: 8px;'
    '  background: rgba(239, 68, 68, 0.15);'
    '  color: #fca5a5 !important;'
    '  border: 1px solid rgba(239, 68, 68, 0.55);'
    '  padding: 9px 18px;'
    '  border-radius: 999px;'
    '  font-size: 0.86rem;'
    '  font-weight: 800;'
    '  text-decoration: none !important;'
    '  transition: all 0.2s ease;'
    '}'
    '.nav-btn-back:hover {'
    '  background: #ef4444;'
    '  color: #ffffff !important;'
    '  box-shadow: 0 0 18px rgba(239, 68, 68, 0.55);'
    '}'
    '.nav-btn-order {'
    '  display: inline-flex;'
    '  align-items: center;'
    '  justify-content: center;'
    '  gap: 8px;'
    '  background: linear-gradient(90deg, #dc2626, #f43f5e);'
    '  color: #ffffff !important;'
    '  padding: 9px 18px;'
    '  border-radius: 999px;'
    '  font-size: 0.86rem;'
    '  font-weight: 800;'
    '  text-decoration: none !important;'
    '  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);'
    '}'
    'div.stDownloadButton > button {'
    '  background: linear-gradient(90deg, #dc2626, #ef4444) !important;'
    '  color: #ffffff !important;'
    '  font-weight: 800 !important;'
    '  border: none !important;'
    '  border-radius: 10px !important;'
    '  padding: 0.65rem 1.2rem !important;'
    '}'
    '.gts-brand {'
    '  text-decoration: none;'
    '  transition: opacity 0.2s ease;'
    '  cursor: pointer;'
    '  display: flex;'
    '  align-items: center;'
    '  gap: 8px;'
    '}'
    '.gts-brand:hover {'
    '  opacity: 0.85;'
    '}'
    '</style>'
    '<div class="center-tier5-logo">🦠</div>',
    unsafe_allow_html=True
)

# --- PRE-LOADED DEMO MICROBIOME 16S DATA (NO UPLOAD NEEDED) ---
@st.cache_data
def get_tier5_demo_data():
    taxa = [
        {"OTU_ID": "OTU_001", "Phylum": "Firmicutes", "Family": "Lactobacillaceae", "Genus": "Lactobacillus", "Control_Abundance_pct": 24.5, "Dysbiosis_Abundance_pct": 6.2, "Significance_p": 0.00012},
        {"OTU_ID": "OTU_002", "Phylum": "Bacteroidetes", "Family": "Bacteroidaceae", "Genus": "Bacteroides", "Control_Abundance_pct": 38.2, "Dysbiosis_Abundance_pct": 18.5, "Significance_p": 0.00140},
        {"OTU_ID": "OTU_003", "Phylum": "Firmicutes", "Family": "Ruminococcaceae", "Genus": "Faecalibacterium", "Control_Abundance_pct": 19.8, "Dysbiosis_Abundance_pct": 4.1, "Significance_p": 0.00005},
        {"OTU_ID": "OTU_004", "Phylum": "Proteobacteria", "Family": "Enterobacteriaceae", "Genus": "Escherichia-Shigella", "Control_Abundance_pct": 2.1, "Dysbiosis_Abundance_pct": 28.4, "Significance_p": 0.00001},
        {"OTU_ID": "OTU_005", "Phylum": "Actinobacteria", "Family": "Bifidobacteriaceae", "Genus": "Bifidobacterium", "Control_Abundance_pct": 9.4, "Dysbiosis_Abundance_pct": 3.0, "Significance_p": 0.00820},
        {"OTU_ID": "OTU_006", "Phylum": "Verrucomicrobia", "Family": "Akkermansiaceae", "Genus": "Akkermansia", "Control_Abundance_pct": 4.5, "Dysbiosis_Abundance_pct": 1.2, "Significance_p": 0.01500},
        {"OTU_ID": "OTU_007", "Phylum": "Proteobacteria", "Family": "Desulfovibrionaceae", "Genus": "Desulfovibrio", "Control_Abundance_pct": 1.2, "Dysbiosis_Abundance_pct": 14.6, "Significance_p": 0.00045},
        {"OTU_ID": "OTU_008", "Phylum": "Firmicutes", "Family": "Streptococcaceae", "Genus": "Streptococcus", "Control_Abundance_pct": 0.3, "Dysbiosis_Abundance_pct": 15.8, "Significance_p": 0.00008},
        {"OTU_ID": "OTU_009", "Phylum": "Bacteroidetes", "Family": "Prevotellaceae", "Genus": "Prevotella", "Control_Abundance_pct": 0.0, "Dysbiosis_Abundance_pct": 8.3, "Significance_p": 0.00210},
    ]
    return pd.DataFrame(taxa)

df_taxa = get_tier5_demo_data()

# --- TOP HEADER BAR ---
top_left, top_right = st.columns([3.2, 1.8])
with top_left:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:14px; margin-bottom: 1.5rem;">'
        f'<a href="{MAIN_WEBSITE_URL}" class="gts-brand">'
        f'<svg style="width: 56px; height: 56px; color: #34d399;" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>'
        f'</svg>'
        f'</a>'
        f'<div>'
        f'<div style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.15em; color:#f87171; font-weight:800;">Tier 5 Live Deliverable Showcase • Pre-Loaded 16S rRNA Amplicon Cohort</div>'
        f'<div style="font-size:2rem; font-weight:900; color:#ffffff; letter-spacing:-0.02em;">Microbiome & <span style="color:#ef4444;">16S rRNA Profiling</span></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with top_right:
    st.markdown(
        f'<div style="display:flex; justify-content:flex-end; align-items:center; gap:10px; padding-top:10px; flex-wrap:wrap;">'
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-back">← Back to Our Website</a>'
        f'<a href="{CHECKOUT_TIER5_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-order">Select Tier 5 Modules ($400) ➔</a>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(239, 68, 68, 0.3); margin: 0.85rem 0 1.2rem 0;'>", unsafe_allow_html=True)

# --- CONCISE OVERVIEW: WHAT WE DELIVER + FILES & LANGUAGES USED ---
st.markdown(
    '<div class="t5-card" style="background:linear-gradient(90deg, rgba(12,25,52,0.94), rgba(127,29,29,0.28));">'
    '<div style="font-size:1.1rem; font-weight:800; color:#f87171; margin-bottom:6px;">🔬 What You Receive in Tier 5 (Live Demo Dataset: Gut Microbiome Dysbiosis Cohort)</div>'
    '<div style="font-size:0.9rem; color:#e2e8f0; line-height:1.55; margin-bottom:14px;">'
    'This live interactive dashboard demonstrates the exact output generated in our <b>Tier 5 Microbiome 16S rRNA Profiling Bundle ($400)</b>. '
    'Starting from raw amplicon FASTQ reads, we execute QIIME2 DADA2 denoising, taxonomic classification against Silva/Greengenes, alpha & beta diversity metrics, and differential abundance stacked bar plots.'
    '</div>'
    '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:10px; font-size:0.83rem;">'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">📂 QIIME2 Execution:</b><br><span style="color:#cbd5e1;">Demux fastq ➔ DADA2 ASVs ➔ Feature table <code>.qza</code> artifacts</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">🧬 Taxonomic Class.:</b><br><span style="color:#cbd5e1;">Naive Bayes classifier ➔ Phylum to Genus <code>.tsv</code> mapping</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">📊 Diversity & Abundance:</b><br><span style="color:#cbd5e1;">Shannon/Chao1 metrics, Bray-Curtis PCoA & stacked bar charts</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">💻 Languages & Stack:</b><br><span style="color:#cbd5e1;"><code>QIIME2</code>, <code>Python</code> (Pandas / Seaborn), & <code>R</code></span>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# --- TOP-LEVEL DEMO COHORT KPI METRICS ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        '<div class="t5-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Denoised Reads</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">97.4%</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">QIIME2 Execution ($150)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        '<div class="t5-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Classified Genera</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">340+</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Taxonomic Class. ($100)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        '<div class="t5-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Alpha Diversity</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">p &lt; 0.01</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Alpha/Beta Diversity ($80)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        '<div class="t5-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Dysbiosis Ratio</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ef4444; margin:4px 0;">4.8x</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Abundance Charts ($70)</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.write("")

# --- 4-MODULE DELIVERABLE TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Taxonomic Class. & Abundance Table (Interactive)",
    "🧼 QIIME2 Execution ($150)",
    "🧬 Alpha/Beta Diversity ($80)",
    "📊 Abundance Charts ($70)"
])

# =====================================================================
# TAB 1: INTERACTIVE TAXONOMIC CLASSIFICATION TABLE (MODULE 2)
# =====================================================================
with tab1:
    st.markdown(
        '<div class="t5-card">'
        '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:4px;">📋 Taxonomic Classification & Relative Abundance Table</div>'
        '<div style="font-size:0.86rem; color:#cbd5e1;">'
        'Explore our pre-loaded 16S microbiome profiling results below. Use the interactive filters to inspect specific phyla or genera across healthy control vs. dysbiosis samples—exactly as delivered in your final <code>.tsv/.csv</code> report.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        selected_phyla = st.multiselect(
            "Filter by Phylum:",
            options=df_taxa["Phylum"].unique().tolist(),
            default=df_taxa["Phylum"].unique().tolist()
        )
    with fcol2:
        max_p = st.slider("Maximum p-value (Significance threshold):", min_value=0.00001, max_value=0.02, value=0.01, step=0.001)

    filtered_taxa = df_taxa[
        (df_taxa["Phylum"].isin(selected_phyla)) &
        (df_taxa["Significance_p"] <= max_p)
    ]

    st.dataframe(filtered_taxa, use_container_width=True, hide_index=True)

    dl_col, info_col = st.columns([1.2, 2.8])
    with dl_col:
        csv_bytes = filtered_taxa.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Sample Taxonomic CSV",
            data=csv_bytes,
            file_name="GenomeTech_Tier5_Taxonomic_Classification.csv",
            mime="text/csv",
            use_container_width=True
        )
    with info_col:
        st.caption("💡 Generated using QIIME2 feature classifiers mapped against Greengenes2 / Silva 138 reference databases with Mann-Whitney FDR statistics.")

# =====================================================================
# TAB 2: MODULE 1 — QIIME2 EXECUTION
# =====================================================================
with tab2:
    c_left, c_right = st.columns([1.1, 1.4], gap="large")
    with c_left:
        st.markdown(
            '<div class="t5-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧼 Module 1: QIIME2 Execution ($150)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Raw amplicon sequences are imported, quality-filtered, and denoised into Amplicon Sequence Variants (ASVs) using DADA2.<br><br>'
            '• <b>Raw Reads Processed:</b> 1,240,000 paired-end reads<br>'
            '• <b>Dada2 Non-Chimeric ASVs:</b> 1,207,500 reads retained (97.4%)<br>'
            '• <b>Truncation Parameters:</b> Forward 240bp, Reverse 200bp<br>'
            '• <b>Deliverable Files:</b> QIIME2 artifact tables (`.qza`), representative sequences, and interactive denoising summary'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c_right:
        st.markdown("##### 📈 DADA2 Quality Filtering & Retention per Sample")
        q2_df = pd.DataFrame({
            "Retained Denoised Reads": [310000, 295000, 302000, 300500],
            "Filtered Chimera / Low-Q": [8500, 9200, 7800, 8100]
        }, index=["Sample Group A", "Sample Group B", "Sample Group C", "Sample Group D"])
        st.bar_chart(q2_df, color=["#3b82f6", "#ef4444"])

# =====================================================================
# TAB 3: MODULE 3 — ALPHA & BETA DIVERSITY
# =====================================================================
with tab3:
    u_left, u_right = st.columns([1.1, 1.4], gap="large")
    with u_left:
        st.markdown(
            '<div class="t5-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧬 Module 3: Alpha & Beta Diversity ($80)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Measures microbial richness within samples (Alpha diversity) and compositional dissimilarity between groups (Beta diversity).<br><br>'
            '• <b>Alpha Metrics:</b> Shannon Index & Chao1 richness (p &lt; 0.01 significant loss in dysbiosis)<br>'
            '• <b>Beta Metrics:</b> Bray-Curtis dissimilarity & Unifrac distances with PERMANOVA test<br>'
            '• <b>Deliverable Files:</b> Diversity vector `.qza` tables and emperor PCoA plots'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with u_right:
        st.markdown("##### 🔬 Alpha Diversity (Shannon Index) Comparison")
        div_df = pd.DataFrame({
            "Shannon Index (Richness & Evenness)": [6.4, 6.2, 6.5, 3.8, 4.1, 3.6]
        }, index=["Control_1", "Control_2", "Control_3", "Dysbiosis_1", "Dysbiosis_2", "Dysbiosis_3"])
        st.bar_chart(div_df, color="#ef4444")

# =====================================================================
# TAB 4: MODULE 4 — ABUNDANCE CHARTS
# =====================================================================
with tab4:
    m_left, m_right = st.columns([1.1, 1.4], gap="large")
    with m_left:
        st.markdown(
            '<div class="t5-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">📊 Module 4: Abundance Charts ($70)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Visualizes relative abundance profiles across taxonomic ranks, highlighting shifts in dominant phyla and pathogenic overgrowth.<br><br>'
            '• <b>Visualization Type:</b> Stacked bar plots & differential boxplots<br>'
            '• <b>Key Finding:</b> Firmicutes/Bacteroidetes ratio imbalance and Enterobacteriaceae spike in dysbiosis<br>'
            '• <b>Deliverable Files:</b> High-resolution SVG/PNG abundance charts & taxa summary reports'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with m_right:
        st.markdown("##### 📉 Phylum-Level Relative Abundance (%) Across Cohorts")
        abund_df = pd.DataFrame({
            "Firmicutes": [62.5, 24.5],
            "Bacteroidetes": [31.2, 32.1],
            "Proteobacteria": [3.4, 38.6],
            "Others / Actinobacteria": [2.9, 4.8]
        }, index=["Healthy Control Cohort", "Gut Dysbiosis Cohort"])
        st.bar_chart(abund_df, color=["#ef4444", "#3b82f6", "#10b981", "#f59e0b"])