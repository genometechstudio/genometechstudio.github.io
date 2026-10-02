import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tier 1 Live Showcase | Variant Calling & Clinical Annotation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LIVE LINKS ---
MAIN_WEBSITE_URL = "https://genometechstudio.github.io"
CHECKOUT_TIER1_URL = "https://genometech-checkout.streamlit.app/?tier=1"

# --- BLUISH & REDDISH THEME + SINGLE CENTER MOVING TIER 1 LOGO ---
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
    '@keyframes floatCenterTier1 {'
    '  0% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '  50% { transform: translate(-50%, -50%) translateY(-22px) scale(1.06) rotate(5deg); opacity: 0.22; }'
    '  100% { transform: translate(-50%, -50%) translateY(0px) scale(1) rotate(0deg); opacity: 0.11; }'
    '}'
    '.center-tier1-logo {'
    '  position: fixed;'
    '  top: 52%;'
    '  left: 50%;'
    '  font-size: 13rem;'
    '  pointer-events: none;'
    '  z-index: 0;'
    '  user-select: none;'
    '  filter: drop-shadow(0 0 35px rgba(239, 68, 68, 0.55)) drop-shadow(0 0 60px rgba(59, 130, 246, 0.4));'
    '  animation: floatCenterTier1 10s ease-in-out infinite;'
    '}'
    '.t1-card {'
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
    '.t1-kpi {'
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
    '<div class="center-tier1-logo">🛡️</div>',
    unsafe_allow_html=True
)

# --- PRE-LOADED DEMO CLINICAL VARIANT DATA (NO UPLOAD NEEDED) ---
@st.cache_data
def get_tier1_demo_data():
    variants = [
        {"Gene": "BRCA1", "Chrom": "chr17", "Position": 43094464, "rsID": "rs80357906", "Ref>Alt": "G > A", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 184, "Quality_QUAL": 99.8, "Allele_Freq_AF": 0.48},
        {"Gene": "TP53", "Chrom": "chr17", "Position": 7674220, "rsID": "rs28934578", "Ref>Alt": "C > T", "Variant_Type": "SNP", "Consequence": "Stop_Gained", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 210, "Quality_QUAL": 99.9, "Allele_Freq_AF": 0.52},
        {"Gene": "EGFR", "Chrom": "chr7", "Position": 55191822, "rsID": "rs121434568", "Ref>Alt": "T > G", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 162, "Quality_QUAL": 98.7, "Allele_Freq_AF": 0.41},
        {"Gene": "BRCA2", "Chrom": "chr13", "Position": 32340301, "rsID": "rs80359550", "Ref>Alt": "CTT > C", "Variant_Type": "Indel", "Consequence": "Frameshift_Variant", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 145, "Quality_QUAL": 97.4, "Allele_Freq_AF": 0.49},
        {"Gene": "KRAS", "Chrom": "chr12", "Position": 25245350, "rsID": "rs121913529", "Ref>Alt": "C > A", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Likely Pathogenic", "Read_Depth_DP": 195, "Quality_QUAL": 99.2, "Allele_Freq_AF": 0.36},
        {"Gene": "PIK3CA", "Chrom": "chr3", "Position": 179234297, "rsID": "rs121913279", "Ref>Alt": "A > G", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Likely Pathogenic", "Read_Depth_DP": 172, "Quality_QUAL": 98.5, "Allele_Freq_AF": 0.44},
        {"Gene": "PTEN", "Chrom": "chr10", "Position": 87933147, "rsID": "rs121909224", "Ref>Alt": "G > T", "Variant_Type": "SNP", "Consequence": "Splice_Donor", "Clinical_Significance": "Likely Pathogenic", "Read_Depth_DP": 138, "Quality_QUAL": 96.9, "Allele_Freq_AF": 0.50},
        {"Gene": "ATM", "Chrom": "chr11", "Position": 108236086, "rsID": "rs587779872", "Ref>Alt": "C > G", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "VUS (Uncertain)", "Read_Depth_DP": 119, "Quality_QUAL": 94.1, "Allele_Freq_AF": 0.29},
        {"Gene": "ALK", "Chrom": "chr2", "Position": 29220829, "rsID": "rs373945110", "Ref>Alt": "G > A", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "VUS (Uncertain)", "Read_Depth_DP": 128, "Quality_QUAL": 95.3, "Allele_Freq_AF": 0.33},
        {"Gene": "APC", "Chrom": "chr5", "Position": 112839514, "rsID": "rs137854573", "Ref>Alt": "A > AT", "Variant_Type": "Indel", "Consequence": "Frameshift_Variant", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 156, "Quality_QUAL": 98.1, "Allele_Freq_AF": 0.47},
        {"Gene": "BRAF", "Chrom": "chr7", "Position": 140753336, "rsID": "rs113488022", "Ref>Alt": "A > T", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Pathogenic", "Read_Depth_DP": 224, "Quality_QUAL": 99.9, "Allele_Freq_AF": 0.51},
        {"Gene": "ERBB2", "Chrom": "chr17", "Position": 39724728, "rsID": "rs1050189", "Ref>Alt": "C > T", "Variant_Type": "SNP", "Consequence": "Synonymous_Variant", "Clinical_Significance": "Benign", "Read_Depth_DP": 190, "Quality_QUAL": 99.1, "Allele_Freq_AF": 0.98},
        {"Gene": "MLH1", "Chrom": "chr3", "Position": 37053568, "rsID": "rs63750217", "Ref>Alt": "G > A", "Variant_Type": "SNP", "Consequence": "Missense_Variant", "Clinical_Significance": "Likely Pathogenic", "Read_Depth_DP": 149, "Quality_QUAL": 97.8, "Allele_Freq_AF": 0.46},
        {"Gene": "MSH2", "Chrom": "chr2", "Position": 47414421, "rsID": "rs267607911", "Ref>Alt": "T > C", "Variant_Type": "SNP", "Consequence": "Intron_Variant", "Clinical_Significance": "Benign", "Read_Depth_DP": 167, "Quality_QUAL": 98.4, "Allele_Freq_AF": 0.95},
    ]
    return pd.DataFrame(variants)

df_variants = get_tier1_demo_data()

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
        f'<div style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.15em; color:#f87171; font-weight:800;">Tier 1 Live Deliverable Showcase • Pre-Loaded Clinical Cohort</div>'
        f'<div style="font-size:2rem; font-weight:900; color:#ffffff; letter-spacing:-0.02em;">Variant Calling & <span style="color:#ef4444;">Clinical Annotation</span></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with top_right:
    st.markdown(
        f'<div style="display:flex; justify-content:flex-end; align-items:center; gap:10px; padding-top:10px; flex-wrap:wrap;">'
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-back">← Back to Our Website</a>'
        f'<a href="{CHECKOUT_TIER1_URL}" target="_blank" rel="noopener noreferrer" class="nav-btn-order">Select Tier 1 Modules ($380) ➔</a>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(239, 68, 68, 0.3); margin: 0.85rem 0 1.2rem 0;'>", unsafe_allow_html=True)

# --- CONCISE OVERVIEW: WHAT WE DELIVER + FILES & LANGUAGES USED ---
st.markdown(
    '<div class="t1-card" style="background:linear-gradient(90deg, rgba(12,25,52,0.94), rgba(127,29,29,0.28));">'
    '<div style="font-size:1.1rem; font-weight:800; color:#f87171; margin-bottom:6px;">🔬 What You Receive in Tier 1 (Live Demo Dataset: Human Oncology Exome GRCh38)</div>'
    '<div style="font-size:0.9rem; color:#e2e8f0; line-height:1.55; margin-bottom:14px;">'
    'This live interactive dashboard demonstrates the exact outputs we generate for your sequencing project in <b>Tier 1</b>. '
    'From raw paired-end reads, our automated pipeline performs read trimming, reference genome alignment, high-confidence SNP/Indel discovery, and clinical pathogenicity mapping.'
    '</div>'
    '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:10px; font-size:0.83rem;">'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">📂 Input & QC Formats:</b><br><span style="color:#cbd5e1;">Raw <code>.fastq.gz</code> reads ➔ Clean QC <code>.html</code> & trimmed reads</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">🧬 Alignment & Variant Files:</b><br><span style="color:#cbd5e1;">Indexed <code>.bam</code> / <code>.bai</code> alignments & filtered <code>.vcf.gz</code> calls</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(239,68,68,0.3); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#fca5a5;">📊 Final Client Deliverables:</b><br><span style="color:#cbd5e1;">Annotated Clinical <code>.csv</code> table + high-res publication plots</span>'
    '</div>'
    '<div style="background:rgba(4,8,18,0.65); border:1px solid rgba(59,130,246,0.35); padding:10px 12px; border-radius:10px;">'
    '<b style="color:#93c5fd;">💻 Languages & Core Stack:</b><br><span style="color:#cbd5e1;"><code>Linux/Bash</code>, <code>Python</code> (Pandas), <code>R</code>, BWA-MEM & BCFtools</span>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# --- TOP-LEVEL DEMO COHORT KPI METRICS ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        '<div class="t1-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Clean Bases (Q30+)</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">96.8%</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Module 1 • FastQC & Trimming ($50)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        '<div class="t1-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">GRCh38 Mapped Reads</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">99.4%</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Module 2 • BWA-MEM Alignment ($150)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        '<div class="t1-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Mean Target Depth</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ffffff; margin:4px 0;">168x</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Module 3 • BCFtools Calling ($100)</div>'
        '</div>',
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        '<div class="t1-kpi">'
        '<div style="font-size:0.76rem; text-transform:uppercase; color:#93c5fd; font-weight:700;">Actionable Variants</div>'
        '<div style="font-size:1.95rem; font-weight:900; color:#ef4444; margin:4px 0;">14</div>'
        '<div style="font-size:0.78rem; color:#fca5a5;">Module 4 • CSV Annotation ($80)</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.write("")

# --- 4-MODULE DELIVERABLE TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Module 4: Clinical Variant CSV (Interactive)",
    "🧼 Module 1: FastQC & Trimming ($50)",
    "🎯 Module 2: BWA-MEM Alignment ($150)",
    "🧬 Module 3: BCFtools Variant Calling ($100)"
])

# =====================================================================
# TAB 1: INTERACTIVE CLINICAL ANNOTATION DELIVERABLE (MODULE 4)
# =====================================================================
with tab1:
    st.markdown(
        '<div class="t1-card">'
        '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:4px;">📋 Final Annotated Clinical Variant Table (Sample Deliverable)</div>'
        '<div style="font-size:0.86rem; color:#cbd5e1;">'
        'Explore our pre-loaded oncology panel results below. Use the interactive filters to inspect pathogenic mutations, read depth, and allele frequencies—exactly as delivered in your final annotated <code>.csv</code> report.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        selected_sig = st.multiselect(
            "Filter by Clinical Significance:",
            options=["Pathogenic", "Likely Pathogenic", "VUS (Uncertain)", "Benign"],
            default=["Pathogenic", "Likely Pathogenic", "VUS (Uncertain)", "Benign"]
        )
    with fcol2:
        selected_vtype = st.multiselect(
            "Filter by Variant Type:",
            options=["SNP", "Indel"],
            default=["SNP", "Indel"]
        )
    with fcol3:
        min_dp = st.slider("Minimum Read Depth (DP):", min_value=100, max_value=220, value=110, step=10)

    filtered_df = df_variants[
        (df_variants["Clinical_Significance"].isin(selected_sig)) &
        (df_variants["Variant_Type"].isin(selected_vtype)) &
        (df_variants["Read_Depth_DP"] >= min_dp)
    ]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    dl_col, info_col = st.columns([1.2, 2.8])
    with dl_col:
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Sample Annotated CSV",
            data=csv_bytes,
            file_name="GenomeTech_Tier1_Sample_Clinical_Variants.csv",
            mime="text/csv",
            use_container_width=True
        )
    with info_col:
        st.caption("💡 Constructed using Python (Pandas) & BCFtools annotation pipelines mapping dbSNP rsIDs, ClinVar clinical significance, and VEP consequence terms.")

# =====================================================================
# TAB 2: MODULE 1 — FASTQC & READ TRIMMING
# =====================================================================
with tab2:
    c_left, c_right = st.columns([1.1, 1.4], gap="large")
    with c_left:
        st.markdown(
            '<div class="t1-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧼 Module 1: FastQC & Adapter Trimming ($50)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Before alignment, raw paired-end <code>.fastq.gz</code> reads are screened for Phred base quality, adapter dimers, and GC bias.<br><br>'
            '• <b>Raw Input Reads:</b> 48,200,000 paired reads<br>'
            '• <b>Post-Trim Clean Reads:</b> 47,650,000 (98.8% retained)<br>'
            '• <b>Mean Phred Score:</b> Q36.4 across 150 bp read length<br>'
            '• <b>Deliverable Files:</b> MultiQC <code>.html</code> summary + cleaned <code>.fastq.gz</code>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c_right:
        st.markdown("##### 📈 Phred Base Quality Score Across Read Position (Pre vs. Post Trimming)")
        positions = [f"Pos {i}bp" for i in range(10, 151, 10)]
        qc_df = pd.DataFrame({
            "Post-Trim Clean Reads (Q-Score)": [38.2, 38.5, 38.4, 38.1, 37.9, 37.8, 37.5, 37.2, 36.9, 36.6, 36.2, 35.8, 35.4, 35.1, 34.8],
            "Raw Unfiltered Reads (Q-Score)": [36.0, 36.2, 35.8, 35.1, 34.2, 33.0, 31.8, 30.5, 29.1, 27.8, 26.2, 24.5, 22.8, 20.4, 18.9]
        }, index=positions)
        st.line_chart(qc_df, color=["#ef4444", "#3b82f6"])

# =====================================================================
# TAB 3: MODULE 2 — BWA-MEM REFERENCE ALIGNMENT
# =====================================================================
with tab3:
    a_left, a_right = st.columns([1.1, 1.4], gap="large")
    with a_left:
        st.markdown(
            '<div class="t1-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🎯 Module 2: BWA-MEM Reference Alignment ($150)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'High-quality reads are aligned to the human reference genome (<code>GRCh38</code>) with coordinate sorting and PCR duplicate marking.<br><br>'
            '• <b>Reference Build:</b> Human GRCh38.p14<br>'
            '• <b>Properly Paired Reads:</b> 98.9%<br>'
            '• <b>Target Exome Coverage (≥50x):</b> 97.6% of target regions<br>'
            '• <b>Deliverable Files:</b> Sorted & indexed <code>.bam</code>, <code>.bai</code>, and alignment flagstat report'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with a_right:
        st.markdown("##### 📊 Mean Sequencing Depth (x) Across Target Chromosomes")
        cov_df = pd.DataFrame({
            "Mean Coverage Depth (x)": [184, 167, 172, 156, 193, 138, 119, 195, 145, 202]
        }, index=["chr2", "chr3", "chr5", "chr7", "chr10", "chr11", "chr12", "chr13", "chr17", "chr19"])
        st.bar_chart(cov_df, color="#ef4444")

# =====================================================================
# TAB 4: MODULE 3 — BCFTOOLS VARIANT CALLING
# =====================================================================
with tab4:
    v_left, v_right = st.columns([1.1, 1.4], gap="large")
    with v_left:
        st.markdown(
            '<div class="t1-card">'
            '<div style="font-size:1.15rem; font-weight:800; color:#f87171; margin-bottom:6px;">🧬 Module 3: BCFtools Variant Calling ($100)</div>'
            '<div style="font-size:0.88rem; color:#e2e8f0; line-height:1.6;">'
            'Probabilistic genotype calling identifies Single Nucleotide Polymorphisms (SNPs) and short Indels, filtering out low-depth artifacts.<br><br>'
            '• <b>Transition / Transversion (Ti/Tv) Ratio:</b> 2.84 (Expected Exome: ~2.8)<br>'
            '• <b>Quality Threshold Applied:</b> QUAL &gt; 30, Read Depth DP &ge; 20<br>'
            '• <b>Deliverable Files:</b> Compressed & indexed <code>.vcf.gz</code> + variant stats summary'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with v_right:
        st.markdown("##### 🔬 Nucleotide Substitution Spectrum in Demo Cohort")
        sub_df = pd.DataFrame({
            "Variant Count": [420, 395, 115, 98, 84, 76]
        }, index=["C>T / G>A", "T>C / A>G", "C>A / G>T", "C>G / G>C", "T>A / A>T", "T>G / A>C"])
        st.bar_chart(sub_df, color="#3b82f6")