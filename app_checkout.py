import streamlit as st
import requests
import json
import os
import urllib.parse 
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GenoStack Services | Checkout Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🇮🇳 INDIA DIRECT PAYMENT CONFIG (SAFE FOR PUBLIC GITHUB)
# Remember to copy those 6 lines into app_checkout's Streamlit Secrets too!
# ==========================================
INDIA_UPI_ID = st.secrets.get("INDIA_UPI_ID", "BHARATPE2A0G0R8H8A59248@unitype")
INDIA_PAYEE_NAME = st.secrets.get("INDIA_PAYEE_NAME", "GenomeTech Studio")
INDIA_BANK_HOLDER = st.secrets.get("INDIA_BANK_HOLDER", "GenomeTech Studio")
INDIA_BANK_ACC = st.secrets.get("INDIA_BANK_ACC", "Available on Proforma Invoice")
INDIA_BANK_IFSC = st.secrets.get("INDIA_BANK_IFSC", "Available on Proforma Invoice")
INDIA_BANK_NAME = st.secrets.get("INDIA_BANK_NAME", "Available on Proforma Invoice")

# --- DUAL CURRENCY STATE INITIALIZATION (USD <-> INR) ---
query_curr = st.query_params.get("currency", "USD").upper()
if "currency" not in st.session_state:
    st.session_state.currency = "INR" if query_curr == "INR" else "USD"

# --- SECURITY: MASTER KEY & ANTI-REUSE GATEWAY ---
if "checkout_unlocked" not in st.session_state:
    st.session_state["checkout_unlocked"] = False

DB_FILE = "used_keys.json"

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

# --- YOUR LIVE ENDPOINTS ---
SHEET_ID = "1un359_bf30-82K3C74hH7sX-uSH-jpx1yB12N7cB3v0"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-pKMSgW-i32k9XAYEPaybbE5V4MV9Pm2boob3PFW10JwqahSPZjlFD1nIoS31KtLt/exec"
MAIN_WEBSITE_URL = "https://genometechstudio.github.io"

# --- TIER 1, 2, 4, 5 CONFIGURATION (SYNCED WITH INDEX.HTML & BUILDER.HTML FOR USD + INR) ---
TIER_CATALOG = {
    "Tier 1": {
        "name": "Tier 1: Variant Calling & Clinical Annotation",
        "logo": "🛡️",
        "mrp_usd": 500,
        "full_price": 380,
        "advance_30": 114,
        "mrp_inr": 16000,
        "full_price_inr": 11999,
        "advance_30_inr": 3600,
        "payment_link": "https://rzp.io/rzp/r0bsnBPe",
        "services": [
            {"name": "FastQC & Trimming", "price": 70, "price_inr": 2499},
            {"name": "BWA-MEM Alignment", "price": 190, "price_inr": 5999},
            {"name": "BCFtools Variant Calling", "price": 130, "price_inr": 4499},
            {"name": "CSV Clinical Annotation", "price": 110, "price_inr": 3003},
        ]
    },
    "Tier 2": {
        "name": "Tier 2: RNA-Seq Transcriptomics Suite",
        "logo": "🧬",
        "mrp_usd": 550,
        "full_price": 410,
        "advance_30": 123,
        "mrp_inr": 18000,
        "full_price_inr": 12999,
        "advance_30_inr": 3900,
        "payment_link": "https://rzp.io/rzp/ppWhefM",
        "services": [
            {"name": "STAR Alignment", "price": 190, "price_inr": 5999},
            {"name": "FeatureCounts Quant", "price": 110, "price_inr": 3499},
            {"name": "DESeq2 Differential Math", "price": 160, "price_inr": 4999},
            {"name": "Volcano & Heatmap Visualization", "price": 90, "price_inr": 3503},
        ]
    },
    "Tier 4": {
        "name": "Tier 4: Single-Cell RNA-Seq Profiling",
        "logo": "🔬",
        "mrp_usd": 600,
        "full_price": 450,
        "advance_30": 135,
        "mrp_inr": 20000,
        "full_price_inr": 14999,
        "advance_30_inr": 4500,
        "payment_link": "https://rzp.io/rzp/33zosVfX",
        "services": [
            {"name": "Matrix Processing", "price": 190, "price_inr": 6499},
            {"name": "Seurat Clustering", "price": 160, "price_inr": 5499},
            {"name": "Cell Type ID Maps", "price": 140, "price_inr": 4499},
            {"name": "UMAP Projections", "price": 110, "price_inr": 3503},
        ]
    },
    "Tier 5": {
        "name": "Tier 5: Microbiome 16S rRNA Profiling",
        "logo": "🦠",
        "mrp_usd": 550,
        "full_price": 400,
        "advance_30": 120,
        "mrp_inr": 17500,
        "full_price_inr": 12499,
        "advance_30_inr": 3750,
        "payment_link": "https://rzp.io/rzp/3BGvCKo1",
        "services": [
            {"name": "QIIME2 Execution", "price": 190, "price_inr": 5999},
            {"name": "Taxonomic Classification", "price": 140, "price_inr": 4499},
            {"name": "Alpha/Beta Diversity", "price": 120, "price_inr": 3999},
            {"name": "Abundance Charts", "price": 100, "price_inr": 3003},
        ]
    }
}

# --- BLUISH & YELLOWISH THEME + FLOATING TIER LOGOS IN BACKGROUND ---
st.markdown(
    '<style>'
    '.stApp {'
    '  background: radial-gradient(circle at 80% 15%, #163a70 0%, #0a1931 52%, #040b18 100%);'
    '  color: #f8fafc;'
    '  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'
    '}'
    'section[data-testid="stSidebar"] {'
    '  background-color: rgba(4, 11, 24, 0.95) !important;'
    '  border-right: 1px solid rgba(250, 204, 21, 0.3);'
    '}'
    '@keyframes floatTierLogo {'
    '  0% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0.14; }'
    '  50% { transform: translateY(-22px) translateX(10px) rotate(8deg); opacity: 0.28; }'
    '  100% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0.14; }'
    '}'
    '.bg-tier-sticker {'
    '  position: fixed;'
    '  pointer-events: none;'
    '  z-index: 0;'
    '  user-select: none;'
    '  filter: drop-shadow(0 0 16px rgba(250, 204, 21, 0.45));'
    '}'
    '.bts-1 { top: 12%; left: 4%; font-size: 4.2rem; animation: floatTierLogo 9s ease-in-out infinite; }'
    '.bts-2 { bottom: 12%; right: 5%; font-size: 4.6rem; animation: floatTierLogo 12s ease-in-out infinite reverse; }'
    '.bts-3 { top: 45%; left: 48%; font-size: 3.6rem; animation: floatTierLogo 11s ease-in-out infinite 1.5s; }'
    '.bts-4 { top: 16%; right: 15%; font-size: 3.8rem; animation: floatTierLogo 10s ease-in-out infinite 0.7s; }'
    '.bts-5 { bottom: 20%; left: 10%; font-size: 3.9rem; animation: floatTierLogo 13s ease-in-out infinite 2.2s; }'
    '.geno-card {'
    '  background: rgba(11, 27, 54, 0.86);'
    '  backdrop-filter: blur(14px);'
    '  border: 1px solid rgba(250, 204, 21, 0.38);'
    '  padding: 1.5rem;'
    '  border-radius: 16px;'
    '  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.5);'
    '  margin-bottom: 1.2rem;'
    '  position: relative;'
    '  z-index: 1;'
    '}'
    '.back-web-btn {'
    '  display: inline-flex;'
    '  align-items: center;'
    '  justify-content: center;'
    '  gap: 8px;'
    '  background: rgba(250, 204, 21, 0.15);'
    '  color: #facc15 !important;'
    '  border: 1px solid rgba(250, 204, 21, 0.55);'
    '  padding: 9px 18px;'
    '  border-radius: 999px;'
    '  font-size: 0.88rem;'
    '  font-weight: 800;'
    '  text-decoration: none !important;'
    '  transition: all 0.2s ease;'
    '}'
    '.back-web-btn:hover {'
    '  background: #facc15;'
    '  color: #040b18 !important;'
    '  box-shadow: 0 0 18px rgba(250, 204, 21, 0.5);'
    '}'
    '.direct-pay-btn {'
    '  display: block;'
    '  width: 100%;'
    '  text-align: center;'
    '  background: linear-gradient(90deg, #eab308, #facc15, #fde047);'
    '  color: #040b18 !important;'
    '  font-weight: 900;'
    '  font-size: 1rem;'
    '  padding: 14px 22px;'
    '  border-radius: 12px;'
    '  text-decoration: none !important;'
    '  margin-top: 12px;'
    '  box-shadow: 0 8px 25px rgba(250, 204, 21, 0.4);'
    '  box-sizing: border-box;'
    '}'
    '.direct-pay-btn:hover {'
    '  background: linear-gradient(90deg, #facc15, #fef08a);'
    '  box-shadow: 0 10px 30px rgba(250, 204, 21, 0.65);'
    '}'
    'div.stButton > button {'
    '  background: linear-gradient(90deg, #eab308, #facc15) !important;'
    '  color: #040b18 !important;'
    '  font-weight: 800 !important;'
    '  border: none !important;'
    '  border-radius: 10px !important;'
    '  padding: 0.7rem 1.2rem !important;'
    '  box-shadow: 0 4px 15px rgba(250, 204, 21, 0.3) !important;'
    '}'
    'div.stButton > button:hover {'
    '  background: linear-gradient(90deg, #facc15, #fde047) !important;'
    '  color: #040b18 !important;'
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
    '<div class="bg-tier-sticker bts-1">🛡️️</div>'
    '<div class="bg-tier-sticker bts-2">🧬</div>'
    '<div class="bg-tier-sticker bts-3">🔬</div>'
    '<div class="bg-tier-sticker bts-4">🦠</div>'
    '<div class="bg-tier-sticker bts-5">⚡</div>',
    unsafe_allow_html=True
)

# --- SEND ORDER DATA TO GOOGLE SHEET (DUAL CURRENCY USD / INR) ---
def save_checkout_to_sheet(email_val, tier_val, modules_val, total_price_val, option_label, curr_code="USD", utr_ref=""):
    """
    Sends Timestamp, Client Email, Tier Selected, Modules Chosen, and Total Price
    (prefixed with ₹ for INR or $ for USD so app_client.py auto-detects currency!)
    to your Google Sheet via Apps Script.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symbol = "₹" if curr_code == "INR" else "$"

    if utr_ref:
        advance_status_str = f"Paid 30% ({curr_code} Ref: {utr_ref})"
    elif "Option B" in option_label:
        advance_status_str = f"Pending 30% ({curr_code})"
    else:
        advance_status_str = f"Direct Link / QR Opened ({curr_code})"

    payload = {
        "action": "new_custom_intake",
        "timestamp": now_str,
        "clientEmail": email_val.strip(),
        "clientID": "",
        "projectID": "",
        "tierSelected": tier_val,
        "modulesChosen": modules_val,
        "totalPrice": f"{symbol}{total_price_val}",
        "currency": curr_code,
        "advancePaid": advance_status_str,
        "status": "New Order",
        "progressPercent": "0"
    }
    try:
        r = requests.post(
            APPS_SCRIPT_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain;charset=utf-8"},
            allow_redirects=True,
            timeout=12
        )
        if "success" in r.text.lower():
            return True, now_str
        return False, now_str
    except Exception:
        return False, now_str

# --- DETECT TIER & CURRENCY FROM URL (?tier=1&currency=INR) ---
query_params = st.query_params if hasattr(st, "query_params") else {}
url_tier = str(query_params.get("tier", "1")).strip()
tier_keys = ["Tier 1", "Tier 2", "Tier 4", "Tier 5"]
default_idx = 0
for i, k in enumerate(tier_keys):
    if url_tier == k.replace("Tier ", "") or url_tier.lower() == k.lower():
        default_idx = i
        break

# Sync currency from URL if present, and provide a live switcher
url_curr = str(query_params.get("currency", "")).strip().upper()
if url_curr in ["USD", "INR"] and "currency_initialized_from_url" not in st.session_state:
    st.session_state.currency = url_curr
    st.session_state.currency_initialized_from_url = True

with st.sidebar:
    st.markdown("### 🌍 Region & Currency")
    chosen_curr = st.radio(
        "Select Pricing & Checkout Mode:",
        options=["USD", "INR"],
        index=1 if st.session_state.get("currency", "USD") == "INR" else 0,
        format_func=lambda x: "🌐 Global ($ USD)" if x == "USD" else "🇮🇳 India (₹ INR • Direct UPI / NEFT)",
    )
    if chosen_curr != st.session_state.get("currency", "USD"):
        st.session_state.currency = chosen_curr
        try:
            st.query_params["currency"] = chosen_curr
        except Exception:
            pass
        st.rerun()

is_inr = (st.session_state.get("currency", "USD") == "INR")
curr_symbol = "₹" if is_inr else "$"

# --- SIDEBAR BACK BUTTON ---
with st.sidebar:
    st.markdown(
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="back-web-btn" style="width:100%; box-sizing:border-box; margin-bottom:1rem;">← Back to Our Website</a>',
        unsafe_allow_html=True
    )
    st.markdown("### 🧬 GenoStack Services")
    st.caption("Select your desired bioinformatics tier and package option to begin your project.")
    
    st.markdown("---")
    st.markdown("### 🔑 Master Access")
    master_key = st.text_input("Enter Key:", type="password", key="master_key_input")
    if st.button("Unlock Portal"):
        if master_key == "GTS-MASTER-UNLIMITED":
            st.session_state["checkout_unlocked"] = True
            st.success("Master Key Accepted.")
            st.rerun()
        elif master_key.startswith("GTS-DEMO-"):
            burned, burn_date = is_key_burned(master_key)
            if burned:
                st.error(f"❌ Security Lock: This Demo Key was already claimed on {burn_date}.")
            else:
                burn_key(master_key)
                st.session_state["checkout_unlocked"] = True
                st.success("Demo Key Accepted.")
                st.rerun()
        else:
            st.error("Invalid Key.")

# --- TOP HEADER: GENOSTACK SERVICES + BACK TO WEBSITE ON SIDE ---
head_col1, head_col2 = st.columns([3.6, 1.4])
with head_col1:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:14px; margin-bottom: 1.8rem;">'
        f'<a href="{MAIN_WEBSITE_URL}" class="gts-brand">'
        f'<svg style="width: 54px; height: 54px; color: #34d399;" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>'
        f'</svg>'
        f'</a>'
        f'<div>'
        f'<div style="font-size:0.78rem; text-transform:uppercase; letter-spacing:0.15em; color:#facc15; font-weight:800;">GenomeTech Studio • Bioinformatics Portal</div>'
        f'<div style="font-size:2.1rem; font-weight:900; color:#ffffff; letter-spacing:-0.02em;">Geno<span style="color:#facc15;">Stack</span> Services</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with head_col2:
    st.markdown(
        f'<div style="text-align:right; padding-top:10px;">'
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="back-web-btn">← Back to Our Website</a>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(250, 204, 21, 0.28); margin: 0.85rem 0 1.3rem 0;'>", unsafe_allow_html=True)

if st.session_state["checkout_unlocked"]:
    st.info("🔓 You are currently logged in with bypass access. Orders will not require payment links.")

# --- TIER SELECTOR BAR + INLINE CURRENCY TOGGLE ---
sel_col1, sel_col2 = st.columns([2.6, 1.4])
with sel_col1:
    st.markdown("##### 🎯 Choose Your GenoStack Pipeline Tier")
    selected_tier_key = st.radio(
        "Select Tier:",
        tier_keys,
        index=default_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
with sel_col2:
    st.markdown("##### 🌍 Billing Currency")
    top_curr = st.radio(
        "Billing Currency:",
        options=["USD", "INR"],
        index=1 if st.session_state.get("currency", "USD") == "INR" else 0,
        format_func=lambda x: "🌐 Global ($ USD)" if x == "USD" else "🇮🇳 India (₹ INR • Direct UPI)",
        horizontal=True,
        label_visibility="collapsed",
        key="main_curr_radio"
    )
    if top_curr != st.session_state.get("currency", "USD"):
        st.session_state.currency = top_curr
        try:
            st.query_params["currency"] = top_curr
        except Exception:
            pass
        st.rerun()

is_inr = (st.session_state.get("currency", "USD") == "INR")
curr_symbol = "₹" if is_inr else "$"
active_tier = TIER_CATALOG[selected_tier_key]

# Active Tier Dynamic Prices (USD vs INR)
active_full_price = active_tier["full_price_inr"] if is_inr else active_tier["full_price"]
active_mrp_price = active_tier["mrp_inr"] if is_inr else active_tier["mrp_usd"]
active_advance_30 = active_tier["advance_30_inr"] if is_inr else active_tier["advance_30"]

if is_inr:
    bundle_badge_text = f"Full Tier Bundle: <s style='opacity:0.65; font-weight:500;'>₹{active_mrp_price:,}</s> ₹{active_full_price:,} INR (0% GST)"
else:
    bundle_badge_text = f"Full Tier Bundle: <s style='opacity:0.65; font-weight:500;'>${active_mrp_price}</s> ${active_full_price} USD"

# --- ACTIVE TIER BANNER ---
st.markdown(
    f'<div class="geno-card" style="padding:1.1rem 1.5rem; background:linear-gradient(90deg, rgba(15,37,71,0.95), rgba(250,204,21,0.16));">'
    f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">'
    f'<div style="display:flex; align-items:center; gap:12px;">'
    f'<div style="width:46px; height:46px; border-radius:12px; background:rgba(250,204,21,0.18); border:1px solid #facc15; display:flex; align-items:center; justify-content:center; font-size:1.6rem;">{active_tier["logo"]}</div>'
    f'<div>'
    f'<div style="font-size:1.2rem; font-weight:800; color:#facc15;">{active_tier["name"]}</div>'
    f'<div style="font-size:0.84rem; color:#cbd5e1;">Select <b>Option A (Full Bundle Price)</b> or <b>Option B (Custom Bundle for {selected_tier_key} Services)</b> on the right.</div>'
    f'</div>'
    f'</div>'
    f'<span style="background:rgba(250,204,21,0.2); border:1px solid #facc15; color:#fde047; padding:5px 14px; border-radius:999px; font-size:0.84rem; font-weight:800;">{bundle_badge_text}</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# --- MAIN 2-COLUMN SPLIT: LEFT (CLIENT DETAILS) | RIGHT (OPTION A & OPTION B) ---
left_col, right_col = st.columns([1, 1.35], gap="large")

with left_col:
    st.markdown(
        '<div class="geno-card">'
        '<div style="font-size:1.18rem; font-weight:800; color:#facc15; margin-bottom:8px;">✉️ Client Details</div>'
        '<div style="font-size:0.9rem; color:#e2e8f0; line-height:1.55;">'
        'Please share your email address below to begin your project. Once your selection is confirmed, we will send your dedicated <b>Client Login ID</b> and secure <b>File Drop-off Box link</b> straight to your inbox.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    client_email = st.text_input(
        "Your Email Address *",
        placeholder="researcher@university.edu",
        key="checkout_client_email"
    )
    client_notes = st.text_input(
        "Your Name / Institution (Optional)",
        placeholder="e.g., Dr. Sharma — Genomics Lab",
        key="checkout_client_notes"
    )

with right_col:
    st.markdown(
        f'<div class="geno-card" style="padding:1.2rem 1.5rem;">'
        f'<div style="font-size:1.12rem; font-weight:800; color:#facc15; margin-bottom:4px;">⚡ Select Your {selected_tier_key} Package Mode</div>'
        f'<div style="font-size:0.84rem; color:#cbd5e1;">Choose <b>Option A</b> for the full bundle fixed price, or <b>Option B</b> to customize from the 4 {selected_tier_key} services.</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    opt_a_price_label = f"₹{active_full_price:,} INR" if is_inr else f"${active_full_price} USD"

    option_choice = st.radio(
        "Package Option:",
        (
            f"Option A: Full Bundle Price for {selected_tier_key} ({opt_a_price_label})",
            f"Option B: Custom Bundle for {selected_tier_key} Services"
        ),
        key=f"opt_radio_{selected_tier_key}_{'INR' if is_inr else 'USD'}",
        horizontal=True,
        label_visibility="collapsed"
    )

    # =========================================================================
    # OPTION A: FULL BUNDLE FIXED PRICE FOR SELECTED TIER (USD & INR)
    # =========================================================================
    if option_choice.startswith("Option A"):
        current_modules_str = "Full Bundle (" + ", ".join([s["name"] for s in active_tier["services"]]) + ")"
        current_total_price = active_full_price
        current_advance_30 = active_advance_30
        curr_code_str = "INR" if is_inr else "USD"

        services_list_html = "".join([
            f'<div style="display:flex; justify-content:space-between; align-items:center; padding:9px 12px; background:rgba(4,11,24,0.65); border:1px solid rgba(250,204,21,0.22); border-radius:8px; margin-bottom:6px; font-size:0.88rem;">'
            f'<span>✅ {s["name"]}</span>'
            f'<span style="color:#fde047; font-weight:700;">Included ({"₹" + format(s["price_inr"], ",") if is_inr else "$" + str(s["price"])})</span>'
            f'</div>'
            for s in active_tier["services"]
        ])

        if is_inr:
            full_price_display_html = f'₹{current_total_price:,} <span style="font-size:0.85rem; color:#cbd5e1;">INR</span>'
            advance_sub_html = f'30% Direct UPI / NEFT Advance: <b>₹{current_advance_30:,} INR (0% GST)</b>'
            bottom_hint_html = 'Click below to generate your <b>0%-Fee Direct UPI QR Code &amp; NEFT Grant Details</b>. Once payment is completed, we will email you your <b>Client ID</b> and <b>File Drop-off Box link</b>!'
            btn_opt_a_label = f"Select {selected_tier_key} Full Bundle & Generate UPI QR / NEFT (₹{current_advance_30:,}) ➔"
        else:
            full_price_display_html = f'${current_total_price} <span style="font-size:0.85rem; color:#cbd5e1;">USD</span>'
            advance_sub_html = f'30% Direct Payment Link: <b>${current_advance_30} USD</b>'
            bottom_hint_html = 'Click below to unlock your <b>Direct Payment Link</b>. Once payment is completed, we will email you your <b>Client ID</b> and <b>File Drop-off Box link</b>!'
            btn_opt_a_label = f"Select {selected_tier_key} Full Bundle & Open Direct Payment Link ➔"

        st.markdown(
            f'<div class="geno-card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(250,204,21,0.25); padding-bottom:12px; margin-bottom:12px;">'
            f'<div>'
            f'<span style="font-size:0.75rem; text-transform:uppercase; color:#facc15; font-weight:800;">Option A • Full Tier Package</span>'
            f'<div style="font-size:1.28rem; font-weight:900; color:#ffffff;">{selected_tier_key} Full Bundle</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:0.75rem; color:#94a3b8;">Full Bundle Fixed Price</div>'
            f'<div style="font-size:1.85rem; font-weight:900; color:#facc15;">{full_price_display_html}</div>'
            f'<div style="font-size:0.76rem; color:#fde047;">{advance_sub_html}</div>'
            f'</div>'
            f'</div>'
            f'<div style="margin-bottom:12px;">{services_list_html}</div>'
            f'<div style="font-size:0.82rem; color:#cbd5e1; background:rgba(250,204,21,0.1); border:1px solid rgba(250,204,21,0.3); padding:10px 12px; border-radius:10px;">'
            f'{bottom_hint_html}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        opt_a_state_key = f"optA_done_{selected_tier_key}_{curr_code_str}"

        if st.button(btn_opt_a_label, key=f"btn_optA_{selected_tier_key}_{curr_code_str}", use_container_width=True):
            if not client_email.strip() or "@" not in client_email:
                st.warning("⚠️ Please enter a valid Email Address on the left first.")
            else:
                ok, ts_saved = save_checkout_to_sheet(
                    email_val=client_email,
                    tier_val=selected_tier_key,
                    modules_val=current_modules_str,
                    total_price_val=current_total_price,
                    option_label="Option A - Full Bundle",
                    curr_code=curr_code_str
                )
                st.session_state[opt_a_state_key] = {
                    "email": client_email.strip(),
                    "ts": ts_saved,
                    "price": current_total_price,
                    "advance": current_advance_30,
                    "curr": curr_code_str,
                    "link": active_tier["payment_link"]
                }

        if st.session_state.get(opt_a_state_key):
            info_a = st.session_state[opt_a_state_key]
            if is_inr:
                upi_note = f"GTS {selected_tier_key} 30Pct Advance"
                upi_uri = (
                    f"upi://pay?pa={urllib.parse.quote(INDIA_UPI_ID)}"
                    f"&pn={urllib.parse.quote(INDIA_PAYEE_NAME)}"
                    f"&am={info_a['advance']}"
                    f"&cu=INR"
                    f"&tn={urllib.parse.quote(upi_note)}"
                )
                qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&margin=10&data={urllib.parse.quote(upi_uri)}"

                st.markdown(
                    f'<div class="geno-card" style="border:2px solid #10b981; background:rgba(15,37,71,0.96); text-align:center;">'
                    f'<div style="font-size:1.12rem; font-weight:900; color:#34d399; margin-bottom:6px;">✅ {selected_tier_key} Full Bundle Reserved!</div>'
                    f'<div style="font-size:0.88rem; color:#ffffff; line-height:1.5; margin-bottom:12px;">'
                    f'Scan the 0%-Fee UPI QR below to pay your <b>30% Advance (₹{info_a["advance"]:,} INR)</b>. '
                    f'Once paid, enter your 12-digit UPI UTR below (or we will email your <b>Client ID</b> and <b>File Drop-off Box link</b> to <b>{info_a["email"]}</b>).'
                    f'</div>'
                    f'<img src="{qr_img_url}" alt="UPI QR Code" style="width:190px; height:190px; border-radius:12px; border:3px solid #10b981; padding:6px; background:#ffffff; margin:0 auto 10px auto; display:block;">'
                    f'<div style="color:#e2e8f0; font-size:0.84rem; font-family:monospace; background:rgba(255,255,255,0.06); display:inline-block; padding:5px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.12); margin-bottom:6px;">'
                    f'Merchant UPI ID: <b>{INDIA_UPI_ID}</b>'
                    f'</div>'
                    f'<div style="color:#94a3b8; font-size:0.76rem;">Works with Google Pay, PhonePe, Paytm &amp; BHIM • 0% Gateway Fee • 0% GST</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                with st.expander("🏦 Paying via University Grant / Direct NEFT / IMPS? View Bank Details"):
                    st.markdown(f"""
                    * **Beneficiary Name:** `{INDIA_BANK_HOLDER}`
                    * **Bank Name:** `{INDIA_BANK_NAME}`
                    * **Account Number:** `{INDIA_BANK_ACC}`
                    * **IFSC Code:** `{INDIA_BANK_IFSC}`
                    * **Total Bundle Value:** `₹{info_a['price']:,} INR`
                    * **30% Advance Due Now:** `₹{info_a['advance']:,} INR` *(0% GST — Exempt under ₹20L threshold)*
                    """)

                utr_input_a = st.text_input(
                    "Paid via UPI / NEFT? Paste your 12-digit UTR / Reference No. to confirm instantly:",
                    placeholder="e.g., 430189234512",
                    key=f"utr_optA_{selected_tier_key}"
                )
                if st.button("✅ Submit Payment UTR & Confirm Project", key=f"utr_btn_optA_{selected_tier_key}", use_container_width=True):
                    if len(utr_input_a.strip()) >= 8:
                        save_checkout_to_sheet(
                            email_val=info_a["email"],
                            tier_val=selected_tier_key,
                            modules_val=current_modules_str,
                            total_price_val=info_a["price"],
                            option_label="Option A - Full Bundle",
                            curr_code="INR",
                            utr_ref=utr_input_a.strip()
                        )
                        st.success(f"🎉 UTR ({utr_input_a.strip()}) recorded! Your Client ID and File Drop-off Box link will arrive at {info_a['email']} shortly.")
                    else:
                        st.warning("⚠️ Please enter a valid 12-digit UPI UTR or NEFT reference number.")
            else:
                st.markdown(
                    f'<div class="geno-card" style="border:2px solid #facc15; background:rgba(15,37,71,0.96);">'
                    f'<div style="font-size:1.12rem; font-weight:900; color:#facc15; margin-bottom:6px;">✅ {selected_tier_key} Full Bundle Selected!</div>'
                    f'<div style="font-size:0.9rem; color:#ffffff; line-height:1.5; margin-bottom:10px;">'
                    f'Please complete your direct payment using the fixed payment link below. '
                    f'Once paid, we will email your <b>Client ID</b> and <b>File Drop-off Box link</b> to <b>{info_a["email"]}</b>.'
                    f'</div>'
                    f'<a href="{info_a["link"]}" target="_blank" rel="noopener noreferrer" class="direct-pay-btn">'
                    f'💳 Proceed to Fixed Direct Payment Link (${info_a["advance"]} USD — 30% Advance) ↗'
                    f'</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # =========================================================================
    # OPTION B: CUSTOM BUNDLE (SELECT WHICH OF THE 4 SERVICES + TOTAL + BUY) — USD & INR
    # =========================================================================
    else:
        curr_code_str = "INR" if is_inr else "USD"

        st.markdown(
            f'<div class="geno-card">'
            f'<span style="font-size:0.75rem; text-transform:uppercase; color:#facc15; font-weight:800;">Option B • Custom Service Selector</span>'
            f'<div style="font-size:1.25rem; font-weight:900; color:#ffffff; margin-bottom:4px;">Select Your {selected_tier_key} Services (Pick from the 4 Modules)</div>'
            f'<div style="font-size:0.84rem; color:#cbd5e1;">Tick the specific services you want below. The total price updates live as you select.</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        picked_modules = []
        custom_total_price = 0

        for idx, srv in enumerate(active_tier["services"]):
            srv_price_val = srv["price_inr"] if is_inr else srv["price"]
            price_label_str = f"₹{srv_price_val:,} INR" if is_inr else f"${srv_price_val} USD"

            is_checked = st.checkbox(
                f"{srv['name']}  —  {price_label_str}",
                key=f"custom_srv_{selected_tier_key}_{curr_code_str}_{idx}"
            )
            if is_checked:
                picked_modules.append(srv["name"])
                custom_total_price += srv_price_val

        current_modules_str = ", ".join(picked_modules) if picked_modules else "None selected yet"
        currency_unit_label = "INR" if is_inr else "USD"
        custom_advance_30 = round(custom_total_price * 0.30) if is_inr else round(custom_total_price * 0.30, 2)

        # Live Total Price Bar
        st.markdown(
            f'<div class="geno-card" style="background:rgba(4,11,24,0.9); border:1px solid #facc15;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<div>'
            f'<div style="font-size:0.82rem; color:#94a3b8;">Selected Services ({len(picked_modules)} of 4 chosen)</div>'
            f'<div style="font-size:0.86rem; color:#fde047; font-weight:700;">{current_modules_str}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:0.75rem; color:#94a3b8;">Total Price</div>'
            f'<div style="font-size:2rem; font-weight:900; color:#facc15;">{"₹" + format(custom_total_price, ",") if is_inr else "$" + str(custom_total_price)} <span style="font-size:0.85rem; color:#cbd5e1;">{currency_unit_label}</span></div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        opt_b_state_key = f"optB_done_{selected_tier_key}_{curr_code_str}"

        if st.button("🛒 Buy Selected Custom Services ➔", key=f"btn_optB_{selected_tier_key}_{curr_code_str}", use_container_width=True):
            if not client_email.strip() or "@" not in client_email:
                st.warning("⚠️ Please enter a valid Email Address on the left first.")
            elif len(picked_modules) == 0:
                st.warning("⚠️ Please select at least 1 of the 4 services above.")
            else:
                ok, ts_saved = save_checkout_to_sheet(
                    email_val=client_email,
                    tier_val=selected_tier_key,
                    modules_val=current_modules_str,
                    total_price_val=custom_total_price,
                    option_label="Option B - Custom Bundle",
                    curr_code=curr_code_str
                )
                st.session_state[opt_b_state_key] = {
                    "email": client_email.strip(),
                    "modules": current_modules_str,
                    "total": custom_total_price,
                    "advance": custom_advance_30,
                    "curr": curr_code_str,
                    "ts": ts_saved
                }

        if st.session_state.get(opt_b_state_key):
            info_b = st.session_state[opt_b_state_key]
            if is_inr:
                upi_note = f"GTS Custom {selected_tier_key}"
                upi_uri = (
                    f"upi://pay?pa={urllib.parse.quote(INDIA_UPI_ID)}"
                    f"&pn={urllib.parse.quote(INDIA_PAYEE_NAME)}"
                    f"&am={info_b['advance']}"
                    f"&cu=INR"
                    f"&tn={urllib.parse.quote(upi_note)}"
                )
                qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&margin=10&data={urllib.parse.quote(upi_uri)}"

                st.markdown(
                    f'<div class="geno-card" style="border:2px solid #10b981; background:rgba(15,37,71,0.96); text-align:center;">'
                    f'<div style="font-size:1.12rem; font-weight:900; color:#34d399; margin-bottom:6px;">✨ Custom {selected_tier_key} Package Reserved!</div>'
                    f'<div style="font-size:0.88rem; color:#ffffff; line-height:1.5; margin-bottom:12px;">'
                    f'Scan the 0%-Fee UPI QR below to pay your <b>30% Advance (₹{info_b["advance"]:,} INR)</b>. '
                    f'Once paid, enter your 12-digit UPI UTR below (or we will email your <b>Client ID</b> and <b>File Drop-off Box link</b> to <b>{info_b["email"]}</b>).'
                    f'</div>'
                    f'<img src="{qr_img_url}" alt="UPI QR Code" style="width:190px; height:190px; border-radius:12px; border:3px solid #10b981; padding:6px; background:#ffffff; margin:0 auto 10px auto; display:block;">'
                    f'<div style="color:#e2e8f0; font-size:0.84rem; font-family:monospace; background:rgba(255,255,255,0.06); display:inline-block; padding:5px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.12); margin-bottom:6px;">'
                    f'Merchant UPI ID: <b>{INDIA_UPI_ID}</b>'
                    f'</div>'
                    f'<div style="color:#94a3b8; font-size:0.76rem;">Works with Google Pay, PhonePe, Paytm &amp; BHIM • 0% Gateway Fee • 0% GST</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                with st.expander("🏦 Paying via University Grant / Direct NEFT / IMPS? View Bank Details"):
                    st.markdown(f"""
                    * **Beneficiary Name:** `{INDIA_BANK_HOLDER}`
                    * **Bank Name:** `{INDIA_BANK_NAME}`
                    * **Account Number:** `{INDIA_BANK_ACC}`
                    * **IFSC Code:** `{INDIA_BANK_IFSC}`
                    * **Custom Total Value:** `₹{info_b['total']:,} INR`
                    * **30% Advance Due Now:** `₹{info_b['advance']:,} INR` *(0% GST — Exempt under ₹20L threshold)*
                    """)

                utr_input_b = st.text_input(
                    "Paid via UPI / NEFT? Paste your 12-digit UTR / Reference No. to confirm instantly:",
                    placeholder="e.g., 430189234512",
                    key=f"utr_optB_{selected_tier_key}"
                )
                if st.button("✅ Submit Payment UTR & Confirm Custom Project", key=f"utr_btn_optB_{selected_tier_key}", use_container_width=True):
                    if len(utr_input_b.strip()) >= 8:
                        save_checkout_to_sheet(
                            email_val=info_b["email"],
                            tier_val=selected_tier_key,
                            modules_val=info_b["modules"],
                            total_price_val=info_b["total"],
                            option_label="Option B - Custom Bundle",
                            curr_code="INR",
                            utr_ref=utr_input_b.strip()
                        )
                        st.success(f"🎉 UTR ({utr_input_b.strip()}) recorded! Your Client ID and File Drop-off Box link will arrive at {info_b['email']} shortly.")
                    else:
                        st.warning("⚠️ Please enter a valid 12-digit UPI UTR or NEFT reference number.")
            else:
                st.markdown(
                    f'<div class="geno-card" style="border:2px solid #facc15; background:rgba(15,37,71,0.96);">'
                    f'<div style="font-size:1.2rem; font-weight:900; color:#facc15; margin-bottom:8px;">✨ Thank you for selecting custom services!</div>'
                    f'<div style="font-size:0.95rem; color:#ffffff; line-height:1.55;">'
                    f'Thank you for selecting custom services, we will get in touch with you shortly with your <b>30% advance payment link</b> at <b>{info_b["email"]}</b>.<br><br>'
                    f'After your payment confirmation message, we will email you your <b>Client ID</b> and <b>File Drop-off Box link</b>!'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
