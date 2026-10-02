import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tier 4 Live Showcase | Single-Cell RNA Profiling",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LIVE LINKS ---
MAIN_WEBSITE_URL = "https://genometechstudio.github.io"
CHECKOUT_TIER4_URL = "https://genometech-checkout.streamlit.app/?tier=4"

# --- BLUISH & REDDISH THEME + SINGLE CENTER MOVING TIER 4 LOGO ---
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
    '@keyframes floatCenterTier4 {'
    '  0% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '  50% { transform: translate(-50%, -50%) translateY(-22px) scale(1.06) rotate(5deg); opacity: 0.22; }'
    '  100% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '}'
    '.center-tier4-logo {'
    '  position: fixed;'
    '  top: 52%;'
    '  left: 50%;'
    '  font-size: 13rem;'
    '  pointer-events: none;'
    '  z-index: 0;'
    '  user-select: none;'
    '  filter: drop-shadow(0 0 35px rgba(239, 68, 68, 0.55)) drop-shadow(0 0 60px rgba(59, 130, 246, 0.4));'
    '  animation: floatCenterTier4 10s ease-in-out infinite;'
    '}'
    '.t4-card {'
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
    '.t4-kpi {'
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
    '<div class="center-tier4-logo">🧪</div>',
    unsafe_allow_html=True
)

# --- PRE-LOADED DEMO SINGLE-CELL CLUSTER DATA (NO UPLOAD NEEDED) ---
@st.cache_data
def get_tier4_demo_data():
    cells = [
        {"Cell_ID": "AAACCTGAGCT42", "Cluster_ID": 0, "Cell_Type": "CD4+ Naive T Cells", "UMAP_1": -12.4, "UMAP_2": 8.1, "n_Genes": 1840, "Total_UMI": 4210, "Percent_MT": 3.2, "Marker_Gene": "IL7R"},
        {"Cell_ID": "AAACGGGCAT19", "Cluster_ID": 1, "Cell_Type": "CD14+ Monocytes", "UMAP_1": 14.2, "UMAP_2": -6.5, "n_Genes": 2450, "Total_UMI": 6890, "Percent_MT": 4.1, "Marker_Gene": "CD14"},
        {"Cell_ID": "AAAGATGCTT84", "Cluster_ID": 2, "Cell_Type": "CD8+ Cytotoxic T", "UMAP_1": -8.1, "UMAP_2": 15.6, "n_Genes": 1920, "Total_UMI": 4810, "Percent_MT": 2.8, "Marker_Gene": "CD8A"},
        {"Cell_ID": "AAACCCAGTC03", "Cluster_ID": 3, "Cell_Type": "B Cells (CD19+)", "UMAP_1": 6.5, "UMAP_2": 18.2, "n_Genes": 1650, "Total_UMI": 3940, "Percent_MT": 2.1, "Marker_Gene": "CD79A"},
        {"Cell_ID": "AAAGCGTACC22", "Cluster_ID": 4, "Cell_Type": "NK Cells", "UMAP_1": -15.8, "UMAP_2": 2.4, "n_Genes": 1710, "Total_UMI": 4120, "Percent_MT": 3.6, "Marker_Gene": "NKG7"},
        {"Cell_ID": "AAAGTAGCGA11", "Cluster_ID": 5, "Cell_Type": "Dendritic Cells", "UMAP_1": 18.5, "UMAP_2": -1.2, "n_Genes": 2890, "Total_UMI": 7450, "Percent_MT": 4.8, "Marker_Gene": "FCER1A"},
        {"Cell_ID": "AACAACCGTG56", "Cluster_ID": 0, "Cell_Type": "CD4+ Naive T Cells", "UMAP_1": -11.9, "UMAP_2": 7.5, "n_Genes": 1790, "Total_UMI": 4050, "Percent_MT": 3.4, "Marker_Gene": "IL7R"},
        {"Cell_ID": "AACCGGTTAC89", "Cluster_ID": 1, "Cell_Type": "CD14+ Monocytes", "UMAP_1": 13.8, "UMAP_2": -5.9, "n_Genes": 2390, "Total_UMI": 6710, "Percent_MT": 3.9, "Marker_Gene": "CD14"},
        {"Cell_ID": "AACCTTGGAA33", "Cluster_ID": 2, "Cell_Type": "CD8+ Cytotoxic T", "UMAP_1": -7.6, "UMAP_2": 14.8, "n_Genes": 1880, "Total_UMI": 4720, "Percent_MT": 2.9, "Marker_Gene": "CD8A"},
        {"Cell_ID": "AAGGCCTTAA77", "Cluster_ID": 3, "Cell_Type": "B Cells (CD19+)", "UMAP_1": 7.1, "UMAP_2": 17.5, "n_Genes": 1610, "Total_UMI": 3820, "Percent_MT": 2.3, "Marker_Gene": "CD79A"},
        {"Cell_ID": "AATTCGGCAT44", "Cluster_ID": 4, "Cell_Type": "NK Cells", "UMAP_1": -16.2, "UMAP_2": 3.1, "n_Genes": 1750, "Total_UMI": 4250, "Percent_MT": 3.5, "Marker_Gene": "NKG7"},
        {"Cell_ID": "ACCCGTTAGC99", "Cluster_ID": 5, "Cell_Type": "Dendritic Cells", "UMAP_1": 17.9, "UMAP_2": -0.8, "n_Genes": 2940, "Total_UMI": 7620, "Percent_MT": 4.5, "Marker_Gene": "FCER1A"},
        {"Cell_ID": "ACTGACTGAT21", "Cluster_ID": 0, "Cell_Type": "CD4+ Naive T Cells", "UMAP_1": -13.1, "UMAP_2": 8.9, "n_Genes": 1860, "Total_UMI": 4320, "Percent_MT": 3.1, "Marker_Gene": "IL7R"},
        {"Cell_ID": "AGCTAGCTAG15", "Cluster_ID": 1, "Cell_Type": "CD14+ Monocytes", "UMAP_1": 14.9, "UMAP_2": -7.1, "n_Genes": 2510, "Total_UMI": 7020, "Percent_MT": 4.2, "Marker_Gene": "CD14"},
        {"Cell_ID": "ATCGATCGAT88", "Cluster_ID": 2, "Cell_Type": "CD8+ Cytotoxic T", "UMAP_1": -8.5, "UMAP_2": 16.1, "n_Genes": 1950, "Total_UMI": 4910, "Percent_MT": 2.7, "Marker_Gene": "CD8A"},
    ]
    return pd.DataFrame(cells)

df_cells = get_tier4_demo_data()

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
        f'<div style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.15em; color:#f87171; font-weight:800;">Tier 4 Live Deliverable Showcase • Pre-Loaded Single-Cell Cohort</div>'
        f'<div style="font-size:2rem; font-weight:900; color:#ffffff; letter-spacing:-0.02em;">Single-Cell RNA <span style="color:#ef4444;">Profiling & UMAP</span></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with top_right:
    st.markdown(
        f'<div style="display:flex; justify-content:flex-end; align-items:center; gap:10px; padding-top:10px; flex-wrap:wrap;">'
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-back">← Back to Our Website</a>'
        f'<a href="{CHECKOUT_TIER4_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-order">Select Tier 4 Modules ($450) ➔</a>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(239, 68, 68, 0.3); margin: 0.85rem 0 1.2rem 0;'>", unsafe_allow_html=True)

# --- CONCISE OVERVIEW: WHAT WE DELIVER + FILES & LANGUAGES USED ---
st.markdown(
    '<div class="t4-card" style="background:linear-gradient(90deg, rgba(12,25,52,0.94), rgba(127,29,29,0.28));">'
    '<div style="font-size:1.1rem; font-weight:800; color:#f87171; margin-bottom:6px;">🔬 What You Receive in Tier 4 (Live Demo Dataset: 10x Genomics Single-Cell PBMCs)</div>'
    '<div style="font-size:0.9rem; color:#e2e8f0; line-height:1.55; margin-bottom:14px;">'
    'This live interactive dashboard demonstrates the exact output generated in our <b>Tier 4 Single-Cell Profiling Bundle ($450)</b>. '
    'Starting from raw 10x Genomics reads, we perform matrix processing, quality filtering, Seurat graph-based clustering, cell type ID mapping, and 2D UMAP projections.'
    '</div>'
    '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:10px; font-size:0.83rem;">'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">📂 Matrix Processing:</b><br><span style="color:#cbd5e1;">Bcl/Fastq ➔ Filtered count matrix <code>.h5</code> & barcodes</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">🧬 Seurat Clustering:</b><br><span style="color:#cbd5e1;">PCA reduction, SNN graph & Leiden cluster markers</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">🗺️ Cell Maps & UMAP:</b><br><span style="color:#cbd5e1;">Annotated Cell Type Metadata <code>.csv</code> + UMAP plots</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">💻 Languages & Stack:</b><br><span style="color:#cbd5e1;"><code>Python</code> (Scanpy), <code>R</code> (Seurat v5), & Cell Ranger</span>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# --- TOP-LEVEL DEMO COHORT KPI METRICS ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        '<div class="t4-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Processed Cells</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">8,450</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Matrix Processing ($150)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        '<div class="t4-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Seurat Clusters</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">6 Groups</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Seurat Clustering ($120)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        '<div class="t4-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Cell Type Maps</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">Annotated</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Cell Type ID Maps ($100)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        '<div class="t4-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">UMAP Projections</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ef4444; margin:4px 0;">2D Space</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">UMAP Projections ($80)</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.write("")

# --- 4-MODULE DELIVERABLE TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Cell Type ID Maps & Metadata (Interactive)",
    "🧼 Matrix Processing ($150)",
    "🧬 Seurat Clustering ($120)",
    "🗺️ UMAP Projections ($80)"
])

# =====================================================================
# TAB 1: INTERACTIVE CELL METADATA & ANNOTATION (MODULE 3)
# =====================================================================
with tab1:
    st.markdown(
        '<div class="t4-card">'
        '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:4px;">📋 Cell Type ID Maps Deliverable (Sample Metadata)</div>'
        '<div style="font-size:0.86rem; color:#cbd5e1;">'
        'Explore our pre-loaded single-cell PBMC profiling table below. Use the interactive filters to inspect specific cell types, gene counts, and mitochondrial fractions—exactly as delivered in your final <code>.csv</code> metadata report.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        selected_types = st.multiselect(
            "Filter by Cell Type:",
            options=df_cells["Cell_Type"].unique().tolist(),
            default=df_cells["Cell_Type"].unique().tolist()
        )
    with fcol2:
        min_genes = st.slider("Minimum Detected Genes (n_Genes):", min_value=1500, max_value=2500, value=1600, step=100)
    with fcol3:
        max_mt = st.slider("Maximum Mitochondrial % (MT):", min_value=2.0, max_value=6.0, value=5.0, step=0.5)

    filtered_cells = df_cells[
        (df_cells["Cell_Type"].isin(selected_types)) &
        (df_cells["n_Genes"] >= min_genes) &
        (df_cells["Percent_MT"] <= max_mt)
    ]

    st.dataframe(filtered_cells, use_container_width=True, hide_index=True)

    dl_col, info_col = st.columns([1.2, 2.8])
    with dl_col:
        csv_bytes = filtered_cells.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Sample Cell Metadata CSV",
            data=csv_bytes,
            file_name="GenomeTech_Tier4_Cell_Type_ID_Maps.csv",
            mime="text/csv",
            use_container_width=True
        )
    with info_col:
        st.caption("💡 Processed using Scanpy (Python) & Seurat v5 (R) integrating automated cell-type scoring against reference PBMC atlases.")

# =====================================================================
# TAB 2: MODULE 1 — MATRIX PROCESSING
# =====================================================================
with tab2:
    c_left, c_right = st.columns([1.1, 1.4], gap="large")
    with c_left:
        st.markdown(
            '<div class="t4-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧼 Module 1: Matrix Processing ($150)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Raw sequencing data is converted into filtered expression count matrices, removing empty droplets and low-quality artifacts.<br><br>'
            '• <b>Raw Droplets Detected:</b> 9,820 cells<br>'
            '• <b>Passing QC Cells:</b> 8,450 high-quality single cells retained<br>'
            '• <b>Mitochondrial Threshold:</b> &lt; 5.0% total UMI counts<br>'
            '• <b>Deliverable Files:</b> Filtered count matrix <code>.h5</code> & QC summary report'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c_right:
        st.markdown("##### 📈 Cell Gene Count vs. Mitochondrial % Distribution")
        qc_df = pd.DataFrame({
            "Passed QC Cells": [2100, 2450, 1920, 1980],
            "Filtered Out (Dying/Doublet)": [350, 420, 310, 290]
        }, index=["Batch 1", "Batch 2", "Batch 3", "Batch 4"])
        st.bar_chart(qc_df, color=["#3b82f6", "#ef4444"])

# =====================================================================
# TAB 3: MODULE 2 — SEURAT CLUSTERING
# =====================================================================
with tab3:
    u_left, u_right = st.columns([1.1, 1.4], gap="large")
    with u_left:
        st.markdown(
            '<div class="t4-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧬 Module 2: Seurat Clustering ($120)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'High-dimensional gene expression space is reduced via PCA, followed by K-nearest neighbor graph construction and Seurat/Leiden community detection.<br><br>'
            '• <b>Principal Components Used:</b> Top 30 PCs<br>'
            '• <b>Cluster Resolution:</b> 0.6 (yielding 6 major immune lineages)<br>'
            '• <b>Deliverable Files:</b> Seurat R object (<code>.rds</code>) with cluster assignments and marker lists'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with u_right:
        st.markdown("##### 🔬 Marker Gene Expression Across Seurat Clusters")
        marker_summary = pd.DataFrame({
            "Mean Expression Score": [4.8, 5.2, 4.5, 4.1, 4.9, 5.6]
        }, index=["IL7R (CD4 T)", "CD14 (Monocyte)", "CD8A (CD8 T)", "CD79A (B Cell)", "NKG7 (NK Cell)", "FCER1A (DC)"])
        st.bar_chart(marker_summary, color="#ef4444")

# =====================================================================
# TAB 4: MODULE 4 — UMAP PROJECTIONS
# =====================================================================
with tab4:
    m_left, m_right = st.columns([1.1, 1.4], gap="large")
    with m_left:
        st.markdown(
            '<div class="t4-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🗺️ Module 4: UMAP Projections ($80)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Non-linear dimensionality reduction projects single-cell transcriptomes into intuitive 2D UMAP scatter visualizations.<br><br>'
            '• <b>Embedding Method:</b> Uniform Manifold Approximation and Projection (UMAP)<br>'
            '• <b>Visualization Output:</b> High-resolution vector plots colored by cluster and cell type<br>'
            '• <b>Deliverable Files:</b> 2D UMAP coordinate CSV & publication-ready PDF/PNG figures'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with m_right:
        st.markdown("##### 📉 2D UMAP Spatial Distribution of Major Immune Clusters")
        st.scatter_chart(
            df_cells,
            x="UMAP_1",
            y="UMAP_2",
            color="Cell_Type",
            size="n_Genes",
            height=340
        )