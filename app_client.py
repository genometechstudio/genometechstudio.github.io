import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import time
import io
import re
import os
import razorpay

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Client Portal | GenomeTech Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SECURITY: ANTI-REUSE DATABASE & AUTHORIZED DEMO KEYS ---
DB_FILE = "used_keys.json"

# ONLY these specific demo keys will work. Add new ones here before giving them to clients.
AUTHORIZED_DEMO_KEYS = [
    "GTS-DEMO-ALFA",
    "GTS-DEMO-BETA",
    "GTS-DEMO-GAMMA"
]

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

# --- LIVE GOOGLE SHEET, APPS SCRIPT & WEBSITE ENDPOINTS ---
SHEET_ID = "1un359_bf30-82K3C74hH7sX-uSH-jpx1yB12N7cB3v0"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsQkADNSxfsePaLn1b4RPN018cIyO8bHnfRtmIYGAawnRtgjBGhWhM35GMRhNrVvfcf3wZE7indbHl/pub?output=csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz-pKMSgW-i32k9XAYEPaybbE5V4MV9Pm2boob3PFW10JwqahSPZjlFD1nIoS31KtLt/exec"
MASTER_BYPASS_CODE = "GENOMETECH_MASTER_2026!"
MAIN_WEBSITE_URL = "https://genometechstudio.github.io"

# --- PROFESSIONAL DARK SLATE & EMERALD GREEN THEME + FLOATING STICKERS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 15% 20%, #06281e 0%, #041524 45%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(2, 6, 23, 0.92) !important;
        border-right: 1px solid rgba(16, 185, 129, 0.25);
    }
    @keyframes floatSlow {
        0% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0.14; }
        50% { transform: translateY(-22px) translateX(10px) rotate(8deg); opacity: 0.28; }
        100% { transform: translateY(0px) translateX(0px) rotate(0deg); opacity: 0.14; }
    }
    .bg-sticker {
        position: fixed;
        pointer-events: none;
        z-index: 0;
        user-select: none;
        filter: drop-shadow(0 0 12px rgba(16, 185, 129, 0.35));
    }
    .st-1 { top: 12%; left: 4%; font-size: 3.8rem; animation: floatSlow 9s ease-in-out infinite; }
    .st-2 { bottom: 14%; right: 6%; font-size: 4.5rem; animation: floatSlow 12s ease-in-out infinite reverse; }
    .st-3 { top: 45%; left: 48%; font-size: 3.2rem; animation: floatSlow 11s ease-in-out infinite 2s; }
    .st-4 { top: 18%; right: 18%; font-size: 3rem; animation: floatSlow 10s ease-in-out infinite 1s; }
    .st-5 { bottom: 22%; left: 12%; font-size: 3.4rem; animation: floatSlow 13s ease-in-out infinite 3s; }
    .portal-card {
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(16, 185, 129, 0.28);
        padding: 1.6rem;
        border-radius: 16px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
        margin-bottom: 1.25rem;
        position: relative;
        z-index: 1;
    }
    .back-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.14);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.45);
        padding: 8px 18px;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 700;
        text-decoration: none !important;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .back-btn:hover {
        background: rgba(16, 185, 129, 0.28);
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.35);
    }
    .gts-brand {
        text-decoration: none;
        transition: opacity 0.2s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .gts-brand:hover {
        opacity: 0.85;
    }
    @keyframes liquidFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes dnaSwim {
        0% { transform: translateX(-15px) translateY(0px) rotate(0deg); }
        50% { transform: translateX(15px) translateY(-2px) rotate(12deg); }
        100% { transform: translateX(-15px) translateY(0px) rotate(0deg); }
    }
    .liquid-track {
        width: 100%;
        height: 36px;
        background: #091326;
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 999px;
        overflow: hidden;
        position: relative;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.7);
    }
    .liquid-fill {
        height: 100%;
        background: linear-gradient(270deg, #047857, #10b981, #34d399, #059669);
        background-size: 300% 300%;
        animation: liquidFlow 4s ease infinite;
        border-radius: 999px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-around;
        overflow: hidden;
        transition: width 0.6s ease;
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.55);
    }
    .dna-inside {
        display: flex;
        align-items: center;
        justify-content: space-around;
        width: 100%;
        font-size: 1.05rem;
        animation: dnaSwim 3.5s ease-in-out infinite;
        opacity: 0.9;
        pointer-events: none;
        white-space: nowrap;
    }
    .liquid-percent-label {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        font-weight: 800;
        font-size: 0.9rem;
        color: #ffffff;
        text-shadow: 0 1px 4px rgba(0,0,0,0.9);
        z-index: 3;
    }
    .locked-preview-box {
        position: relative;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(16, 185, 129, 0.4);
        margin: 1rem 0;
        background: #091326;
    }
    .locked-preview-img {
        width: 100%;
        height: 230px;
        object-fit: cover;
        filter: blur(7px) brightness(0.65);
        transform: scale(1.04);
    }
    .locked-preview-overlay {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(180deg, rgba(2,6,23,0.2) 0%, rgba(2,6,23,0.88) 85%);
        padding: 1.2rem;
        text-align: center;
    }
    .pay-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background: linear-gradient(90deg, #059669, #10b981);
        color: #020617 !important;
        font-weight: 800;
        padding: 12px 20px;
        border-radius: 12px;
        text-decoration: none !important;
        margin: 10px 0;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
        transition: all 0.2s ease;
        box-sizing: border-box;
    }
    .pay-btn:hover {
        background: linear-gradient(90deg, #10b981, #34d399);
        transform: translateY(-1px);
    }
    .download-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background: linear-gradient(90deg, #0ea5e9, #10b981);
        color: #020617 !important;
        font-weight: 800;
        padding: 14px 22px;
        border-radius: 12px;
        text-decoration: none !important;
        margin: 12px 0;
        box-shadow: 0 6px 25px rgba(14, 165, 233, 0.4);
        box-sizing: border-box;
    }
    </style>
    <div class="bg-sticker st-1">🧬</div>
    <div class="bg-sticker st-2">🔬</div>
    <div class="bg-sticker st-3">🧪</div>
    <div class="bg-sticker st-4">🦠</div>
    <div class="bg-sticker st-5">📊</div>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_tier_logo(tier_text):
    t = str(tier_text).lower()
    if "tier 1" in t or "qc" in t or "assembly" in t:
        return "🛡️", "#38bdf8"
    elif "tier 2" in t or "variant" in t or "wgs" in t:
        return "🧬", "#818cf8"
    elif "tier 3" in t or "rna" in t or "transcript" in t:
        return "📈", "#c084fc"
    elif "tier 4" in t or "single-cell" in t or "seurat" in t:
        return "🔬", "#34d399"
    elif "tier 5" in t or "microbiome" in t or "16s" in t:
        return "🦠", "#fbbf24"
    elif "express" in t:
        return "⚡", "#f472b6"
    return "🧬", "#10b981"

def has_master_code(val):
    return MASTER_BYPASS_CODE.lower() in str(val).strip().lower()

def format_direct_download_link(raw_url):
    url = str(raw_url).strip()
    if not url or has_master_code(url) or url.lower() == "nan":
        return "data:text/csv;charset=utf-8,Gene_ID,Log2FC,P_Value,Cluster%0AGENE_001,2.45,0.0001,Cluster_1%0AGENE_002,-1.89,0.0004,Cluster_2%0AGENE_003,3.12,0.00001,Cluster_1"
    drive_match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    if "dropbox.com" in url:
        if "dl=0" in url:
            return url.replace("dl=0", "dl=1")
        elif "dl=1" not in url:
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}dl=1"
    return url

LOCAL_CACHE_FILE = "_sheet_backup.csv"

def load_live_sheet_df():
    ts = int(time.time() * 1000)
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    urls_to_try = [
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&_cb={ts}",
        f"{SHEET_CSV_URL}&_cb={ts}"
    ]

    for url in urls_to_try:
        for attempt in range(2):
            try:
                r = requests.get(url, headers=headers, timeout=8)
                if r.status_code == 200 and "Client Email" in r.text:
                    df = pd.read_csv(io.StringIO(r.text), dtype=str, keep_default_na=False)
                    df.columns = [str(c).strip() for c in df.columns]
                    try:
                        df.to_csv(LOCAL_CACHE_FILE, index=False)
                    except Exception:
                        pass
                    return df
            except Exception:
                time.sleep(0.5)

    if os.path.exists(LOCAL_CACHE_FILE):
        st.toast("⚠️ Offline/DNS hiccup detected — using last synced Sheet snapshot.", icon="📡")
        df = pd.read_csv(LOCAL_CACHE_FILE, dtype=str, keep_default_na=False)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    st.toast("⚠️ Internet/DNS offline — using local test mode.", icon="🛠️")
    return pd.DataFrame([{
        "Timestamp": "2026-09-29",
        "Client Email": "test@genometech.com",
        "Client ID": "GT-101",
        "Project ID": "GT-101",
        "Tier Selected": "Tier 4: Single-Cell Profiling",
        "Modules Chosen": "Seurat Clustering & Marker Identification",
        "Total Price": "500",
        "Advance Paid (30%)": "Paid",
        "Status": "Complete",
        "Progress Percent": "100",
        "Initial Deliverables Link": MASTER_BYPASS_CODE,
        "Remaining Payment (70%) Link": "",
        "70% Payment Status": "Paid",
        "Final Deliverables Link": MASTER_BYPASS_CODE,
        "Redo Request Text": "",
        "Client Feedback": "",
        "Redo File Link": ""
    }])

def get_col_val(row, possible_names, default=""):
    for name in possible_names:
        for col in row.index:
            if col.strip().lower() == name.lower():
                val = str(row[col]).strip()
                if val and val.lower() != "nan":
                    return val
    return default

def post_single_payload_to_gas(payload):
    try:
        r = requests.post(
            APPS_SCRIPT_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "text/plain;charset=utf-8"},
            allow_redirects=False,
            timeout=12
        )
        if r.status_code in [301, 302, 303, 307, 308] and "Location" in r.headers:
            r_out = requests.get(r.headers["Location"], timeout=10)
            try:
                return r_out.json()
            except Exception:
                return {"raw": r_out.text}
        elif r.status_code == 200:
            try:
                return r.json()
            except Exception:
                return {"raw": r.text}
    except Exception as e:
        return {"error": str(e)}
    return {}

def sync_update_to_sheet(active_row, action_type, text_value):
    col_b_email = str(active_row.iloc[1]) if len(active_row) > 1 else get_col_val(active_row, ["Client Email"], "")
    col_c_cid = str(active_row.iloc[2]) if len(active_row) > 2 else get_col_val(active_row, ["Client ID"], "")
    col_d_pid = str(active_row.iloc[3]) if len(active_row) > 3 else get_col_val(active_row, ["Project ID"], "")

    pid_candidates = []
    for cand in [col_d_pid, col_d_pid.strip(), col_c_cid, col_c_cid.strip(), ""]:
        if cand not in pid_candidates:
            pid_candidates.append(cand)
        if isinstance(cand, str) and cand.isdigit():
            int_cand = int(cand)
            if int_cand not in pid_candidates:
                pid_candidates.append(int_cand)

    email_candidates = []
    for ec in [col_b_email, col_b_email.strip(), col_b_email.strip().lower()]:
        if ec not in email_candidates:
            email_candidates.append(ec)

    last_resp = {}
    for em in email_candidates:
        for pid in pid_candidates:
            payload = {
                "clientEmail": em,
                "projectID": pid,
                "action": action_type,
                "redoText": text_value,
                "feedbackText": text_value
            }
            res = post_single_payload_to_gas(payload)
            last_resp = res
            if isinstance(res, dict) and res.get("status") == "success":
                return True, f"✅ Synced to Google Sheet (Matched Email='{em}', ProjectID='{pid}')"

    return False, f"⚠️ Apps Script returned: {last_resp}. Make sure Column B ('Client Email') and Column D ('Project ID') are filled on this row in Sheet1!"

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "client_email" not in st.session_state:
    st.session_state.client_email = ""
if "client_id" not in st.session_state:
    st.session_state.client_id = ""
if "unlocked_projects" not in st.session_state:
    st.session_state.unlocked_projects = set()
if "redo_submitted" not in st.session_state:
    st.session_state.redo_submitted = {}
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = {}
if "last_sheet_sync_msg" not in st.session_state:
    st.session_state.last_sheet_sync_msg = ""
if "checkout_unlocked" not in st.session_state:
    st.session_state.checkout_unlocked = False

# --- 64-PIECE (8x8) GENOMIC PICTURE PUZZLE COMPONENT ---
def render_64_piece_puzzle(client_key):
    puzzle_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            user-select: none;
        }}
        .game-wrapper {{
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 16px;
            padding: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .game-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .game-title {{
            font-size: 0.95rem;
            font-weight: 800;
            color: #34d399;
        }}
        .score-pill {{
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 999px;
        }}
        .preview-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(2, 6, 23, 0.65);
            border: 1px solid #1e293b;
            padding: 8px;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        .preview-thumb {{
            width: 68px;
            height: 68px;
            border-radius: 8px;
            border: 1px solid #10b981;
            object-fit: cover;
            flex-shrink: 0;
        }}
        .preview-info {{
            font-size: 0.74rem;
            color: #cbd5e1;
            line-height: 1.35;
        }}
        .section-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #94a3b8;
            margin: 6px 0 4px 0;
            font-weight: 700;
        }}
        .board-grid {{
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 1px;
            width: 280px;
            height: 280px;
            margin: 0 auto 10px auto;
            background: #0f172a;
            border: 2px solid #10b981;
            border-radius: 8px;
            overflow: hidden;
        }}
        .tray-grid {{
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 2px;
            width: 280px;
            height: 280px;
            margin: 0 auto;
            background: #020617;
            border: 1px dashed #475569;
            border-radius: 8px;
            padding: 2px;
            box-sizing: border-box;
        }}
        .slot, .tray-cell {{
            width: 100%;
            height: 100%;
            background-color: #091326;
            position: relative;
            cursor: pointer;
            box-sizing: border-box;
        }}
        .slot.selected, .tray-cell.selected {{
            outline: 2px solid #38bdf8;
            z-index: 5;
        }}
        .slot.correct {{
            box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.5);
        }}
        .btn-row {{
            display: flex;
            gap: 6px;
            margin-top: 10px;
        }}
        .g-btn {{
            flex: 1;
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 7px 8px;
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .g-btn:hover {{
            background: #334155;
            border-color: #10b981;
        }}
        .g-btn.primary {{
            background: linear-gradient(90deg, #059669, #10b981);
            color: #020617;
            border: none;
        }}
        .win-banner {{
            display: none;
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid #10b981;
            color: #34d399;
            text-align: center;
            padding: 8px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-top: 8px;
        }}
    </style>
    </head>
    <body>
    <div class="game-wrapper">
        <div class="game-header">
            <span class="game-title">🧩 64-Piece Genomic Art Puzzle</span>
            <span class="score-pill" id="progressText">0 / 64 Placed</span>
        </div>
        <div class="preview-row">
            <img id="previewImg" class="preview-thumb" src="" alt="Preview">
            <div class="preview-info">
                <b id="picTitle" style="color:#34d399;">Loading...</b><br>
                Click any piece in the <b>Pieces Box</b> below, then click its spot in the <b>8×8 Target Box</b>. Your progress stays saved across refreshes!
            </div>
        </div>
        <div class="section-label">Target Assembly Box (8×8 = 64 Pieces)</div>
        <div class="board-grid" id="boardGrid"></div>
        <div class="section-label">Scrambled Pieces Box (Click to Pick & Place)</div>
        <div class="tray-grid" id="trayGrid"></div>
        <div class="win-banner" id="winBanner">
            🎉 Masterpiece Complete! All 64 genomic fragments assembled!
        </div>
        <div class="btn-row">
            <button class="g-btn" onclick="placeHintPiece()">💡 Place 5 Pieces</button>
            <button class="g-btn primary" onclick="nextPicture()">Next Picture ➔</button>
        </div>
    </div>
    <script>
    const STORAGE_KEY = "gt_puzzle64_state_" + "{client_key}";
    const IMAGES = [
        {{ title: "DNA Double Helix Structure", url: "https://images.unsplash.com/photo-1530497610245-94d3c16cda28?w=600&auto=format&fit=crop&q=80" }},
        {{ title: "Single-Cell Fluorescence Map", url: "https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=600&auto=format&fit=crop&q=80" }},
        {{ title: "Genomic Sequencing Matrix", url: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80" }},
        {{ title: "Microbiome Colony Architecture", url: "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=600&auto=format&fit=crop&q=80" }}
    ];
    let state = null;
    let selectedSource = null;

    function initNewState(imgIndex) {{
        const pieces = [];
        for (let i = 0; i < 64; i++) pieces.push(i);
        for (let i = pieces.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [pieces[i], pieces[j]] = [pieces[j], pieces[i]];
        }}
        state = {{
            imgIndex: imgIndex % IMAGES.length,
            board: Array(64).fill(null),
            tray: pieces
        }};
        saveState();
    }}

    function loadState() {{
        try {{
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {{
                const parsed = JSON.parse(raw);
                if (parsed && Array.isArray(parsed.board) && parsed.board.length === 64 && Array.isArray(parsed.tray)) {{
                    state = parsed;
                    return;
                }}
            }}
        }} catch (e) {{}}
        initNewState(0);
    }}

    function saveState() {{
        try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch (e) {{}}
    }}

    function applyPieceStyle(el, pieceId, imgUrl) {{
        if (pieceId === null || pieceId === undefined) {{
            el.style.backgroundImage = "none";
            return;
        }}
        const row = Math.floor(pieceId / 8);
        const col = pieceId % 8;
        const posX = (col / 7) * 100;
        const posY = (row / 7) * 100;
        el.style.backgroundImage = `url('${{imgUrl}}')`;
        el.style.backgroundSize = "800% 800%";
        el.style.backgroundPosition = `${{posX}}% ${{posY}}%`;
    }}

    function render() {{
        const imgObj = IMAGES[state.imgIndex % IMAGES.length];
        document.getElementById("previewImg").src = imgObj.url;
        document.getElementById("picTitle").innerText = imgObj.title;
        const boardEl = document.getElementById("boardGrid");
        const trayEl = document.getElementById("trayGrid");
        boardEl.innerHTML = "";
        trayEl.innerHTML = "";
        let correctCount = 0;

        for (let i = 0; i < 64; i++) {{
            const pieceId = state.board[i];
            if (pieceId === i) correctCount++;
            const slot = document.createElement("div");
            slot.className = "slot" + (pieceId === i ? " correct" : "");
            if (selectedSource && selectedSource.zone === "board" && selectedSource.index === i) slot.classList.add("selected");
            applyPieceStyle(slot, pieceId, imgObj.url);
            slot.onclick = () => handleCellClick("board", i);
            boardEl.appendChild(slot);
        }}

        for (let i = 0; i < 64; i++) {{
            const pieceId = state.tray[i];
            const cell = document.createElement("div");
            cell.className = "tray-cell";
            if (selectedSource && selectedSource.zone === "tray" && selectedSource.index === i) cell.classList.add("selected");
            applyPieceStyle(cell, pieceId, imgObj.url);
            cell.onclick = () => handleCellClick("tray", i);
            trayEl.appendChild(cell);
        }}

        document.getElementById("progressText").innerText = `${{correctCount}} / 64 Correct`;
        document.getElementById("winBanner").style.display = (correctCount === 64) ? "block" : "none";
    }}

    function handleCellClick(zone, index) {{
        const clickedVal = state[zone][index];
        if (!selectedSource) {{
            if (clickedVal === null) return;
            selectedSource = {{ zone, index }};
            render();
            return;
        }}
        const srcZone = selectedSource.zone;
        const srcIdx = selectedSource.index;
        const temp = state[srcZone][srcIdx];
        state[srcZone][srcIdx] = state[zone][index];
        state[zone][index] = temp;
        selectedSource = null;
        saveState();
        render();
    }}

    function placeHintPiece() {{
        let placed = 0;
        for (let targetIdx = 0; targetIdx < 64 && placed < 5; targetIdx++) {{
            if (state.board[targetIdx] !== targetIdx) {{
                let foundZone = null;
                let foundIdx = -1;
                for (let j = 0; j < 64; j++) {{
                    if (state.tray[j] === targetIdx) {{ foundZone = "tray"; foundIdx = j; break; }}
                    if (state.board[j] === targetIdx) {{ foundZone = "board"; foundIdx = j; break; }}
                }}
                if (foundZone !== null) {{
                    const displaced = state.board[targetIdx];
                    state.board[targetIdx] = targetIdx;
                    state[foundZone][foundIdx] = displaced;
                    placed++;
                }}
            }}
        }}
        selectedSource = null;
        saveState();
        render();
    }}

    function nextPicture() {{
        selectedSource = null;
        initNewState(state.imgIndex + 1);
        render();
    }}

    loadState();
    render();
    </script>
    </body>
    </html>
    """
    components.html(puzzle_html, height=760, scrolling=False)

# --- TOP HEADER BAR ---
head_col1, head_col2 = st.columns([3.6, 1.4])
with head_col1:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom: 1.5rem;">'
        f'<a href="{MAIN_WEBSITE_URL}" class="gts-brand">'
        f'<svg style="width: 32px; height: 32px; color: #34d399;" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>'
        f'</svg>'
        f'</a>'
        f'<div>'
        f'<a href="{MAIN_WEBSITE_URL}" class="gts-brand" style="font-size:1.55rem; font-weight:800; color:#f8fafc; letter-spacing:-0.02em;">GenomeTech <span style="color:#ffffff;">Studio</span></a>'
        f'<span style="font-size:1rem; color:#34d399; font-weight:600; margin-left:8px;">| Client Login Portal</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with head_col2:
    st.markdown(
        f'<div style="text-align:right; padding-top:4px;">'
        f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="back-btn">← Back to Our Website</a>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(16, 185, 129, 0.2); margin: 0.75rem 0 1.5rem 0;'>", unsafe_allow_html=True)

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    
    with st.sidebar:
        st.markdown("### 🔑 Master Access")
        master_key = st.text_input("Enter Key:", type="password", key="master_key_input")
        if st.button("Unlock Portal"):
            if master_key == "GTS-MASTER-UNLIMITED":
                st.session_state.checkout_unlocked = True
                st.success("Master Key Accepted.")
                st.rerun()
            elif master_key in AUTHORIZED_DEMO_KEYS:
                burned, burn_date = is_key_burned(master_key)
                if burned:
                    st.error(f"❌ Security Lock: This Demo Key was already claimed on {burn_date}.")
                else:
                    burn_key(master_key)
                    st.session_state.checkout_unlocked = True
                    st.success("Demo Key Accepted.")
                    st.rerun()
            else:
                st.error("Invalid Key or Unauthorized Demo Code.")

    _, login_col, _ = st.columns([1, 1.4, 1])
    with login_col:
        st.markdown(
            '<div class="portal-card" style="text-align:center;">'
            '<div style="font-size:2.6rem; margin-bottom:0.3rem;">🧬</div>'
            '<h2 style="color:#34d399; margin:0 0 0.5rem 0; font-weight:800;">Client Greenroom Portal</h2>'
            '<p style="color:#94a3b8; font-size:0.92rem; margin-bottom:0.5rem;">'
            'Enter your registered Email and Client ID (or Project ID) to enter your live bioinformatics workspace.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )

        with st.form("client_login_form"):
            email_in = st.text_input("Registered Client Email", placeholder="researcher@university.edu")
            id_in = st.text_input("Client ID / Project ID", placeholder="e.g., GT-101 or Project ID")
            login_btn = st.form_submit_button("Enter Greenroom ➔", use_container_width=True)

            if login_btn:
                if not email_in.strip() or not id_in.strip():
                    st.warning("Please enter both your Email and Client ID.")
                else:
                    try:
                        df = load_live_sheet_df()
                        email_clean = email_in.strip().lower()
                        id_clean = id_in.strip().lower()

                        email_series = df["Client Email"].astype(str).str.strip().str.lower() if "Client Email" in df.columns else pd.Series([], dtype=str)
                        cid_series = df["Client ID"].astype(str).str.strip().str.lower() if "Client ID" in df.columns else pd.Series([], dtype=str)
                        pid_series = df["Project ID"].astype(str).str.strip().str.lower() if "Project ID" in df.columns else pd.Series([], dtype=str)

                        matches = df[(email_series == email_clean) & ((cid_series == id_clean) | (pid_series == id_clean))]

                        if not matches.empty:
                            st.session_state.logged_in = True
                            st.session_state.client_email = email_clean
                            st.session_state.client_id = id_clean
                            st.rerun()
                        else:
                            st.error("No matching record found in the live sheet. Please verify your Client Email and Client ID in the Google Sheet.")
                    except Exception as e:
                        st.error(f"Could not read live Google Sheet: {e}")

# --- GREENROOM DASHBOARD ---
else:
    if "sheet_df" not in st.session_state or st.session_state.sheet_df is None:
        try:
            st.session_state.sheet_df = load_live_sheet_df()
        except Exception as e:
            st.error(f"Error syncing live Google Sheet: {e}")
            st.stop()
    df_live = st.session_state.sheet_df

    email_clean = st.session_state.client_email
    id_clean = st.session_state.client_id

    email_series = df_live["Client Email"].astype(str).str.strip().str.lower()
    cid_series = df_live["Client ID"].astype(str).str.strip().str.lower() if "Client ID" in df_live.columns else pd.Series([""] * len(df_live))
    pid_series = df_live["Project ID"].astype(str).str.strip().str.lower() if "Project ID" in df_live.columns else pd.Series([""] * len(df_live))

    client_all_rows = df_live[(email_series == email_clean) | (cid_series == id_clean)]
    exact_rows = df_live[(email_series == email_clean) & ((cid_series == id_clean) | (pid_series == id_clean))]
    active_row = exact_rows.iloc[-1] if not exact_rows.empty else client_all_rows.iloc[-1]

    # Extract live columns from Sheet
    client_id_val = get_col_val(active_row, ["Client ID"], st.session_state.client_id.upper())
    project_id_val = get_col_val(active_row, ["Project ID"], client_id_val)
    tier_val = get_col_val(active_row, ["Tier Selected", "Tier"], "Custom Bioinformatics Pipeline")
    modules_val = get_col_val(active_row, ["Modules Chosen", "Module"], "Standard Omics Execution")
    status_val = get_col_val(active_row, ["Status"], "In Progress")
    advance_status = get_col_val(active_row, ["Advance Paid (30%)"], "Paid")
    
    # Calculate Expected 70% Amount Base on Sheet Data
    try:
        total_usd = float(re.sub(r'[^\d.]', '', str(get_col_val(active_row, ["Total Price"], "0"))))
    except ValueError:
        total_usd = 0.0
    expected_70_cents = int((total_usd * 0.70) * 100)
    if expected_70_cents <= 0:
        expected_70_cents = 100  # Fallback to prevent free unauthorized unlocks if sheet is blank

    raw_progress = get_col_val(active_row, ["Progress Percent", "Progress"], "0")
    try:
        progress_val = int(float(str(raw_progress).replace("%", "").strip()))
    except Exception:
        progress_val = 0

    initial_link = get_col_val(active_row, ["Initial Deliverables Link", "Deliverable Link"], "")
    
    # Dynamically pull the 70% payment link from the Google Sheet column
    payment_70_link = get_col_val(active_row, ["Remaining Payment (70%) Link"], "")

    payment_70_status = get_col_val(active_row, ["70% Payment Status"], "")
    final_link = get_col_val(active_row, ["Final Deliverables Link"], "")
    redo_req_existing = get_col_val(active_row, ["Redo Request Text"], "")
    feedback_existing = get_col_val(active_row, ["Client Feedback"], "")
    redo_file_link = get_col_val(active_row, ["Redo File Link", "Redo Deliverable Link", "Redo Deliverables Link"], "")

    # --- MASTER CODE IN SHEET COLUMNS DETECTION ---
    master_in_initial = has_master_code(initial_link)
    master_in_final = has_master_code(final_link) or has_master_code(payment_70_status)
    master_in_redo = has_master_code(redo_file_link)

    if master_in_initial or master_in_final or master_in_redo or bool(initial_link or final_link or redo_file_link):
        progress_val = 100
    progress_val = max(0, min(100, progress_val))

    # --- SIDEBAR: PREVIOUS PROJECT HISTORY & REFRESH ---
    with st.sidebar:
        st.markdown(
            f'<a href="{MAIN_WEBSITE_URL}" target="_blank" rel="noopener noreferrer" class="back-btn" style="width:100%; box-sizing:border-box; margin-bottom:1rem;">← Back to Our Website</a>',
            unsafe_allow_html=True
        )
        st.markdown("### 👤 Client Greenroom")
        st.caption(f"**Email:** {st.session_state.client_email}\n\n**Client ID:** `{client_id_val}`\n\n**Project ID:** `{project_id_val}`")

        if st.button("🔄 Refresh Live Sheet Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.sheet_df = load_live_sheet_df()
            st.rerun()

        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.sheet_df = None
            st.rerun()

        st.markdown("---")
        st.markdown("### 📜 Previous Project History")
        if not client_all_rows.empty:
            for idx, h_row in client_all_rows.iloc[::-1].iterrows():
                h_pid = get_col_val(h_row, ["Project ID"], get_col_val(h_row, ["Client ID"], "GT-PROJ"))
                h_tier = get_col_val(h_row, ["Tier Selected"], "Bioinformatics")
                h_stat = get_col_val(h_row, ["Status"], "Active")
                h_prog = get_col_val(h_row, ["Progress Percent"], "0")
                h_time = get_col_val(h_row, ["Timestamp"], "")
                st.markdown(
                    f'<div style="background:rgba(15,23,42,0.85); border:1px solid rgba(16,185,129,0.25); padding:10px 12px; border-radius:10px; margin-bottom:8px; font-size:0.83rem;">'
                    f'<div style="display:flex; justify-content:space-between; font-weight:700; color:#34d399;"><span>{h_pid}</span><span>{h_prog}%</span></div>'
                    f'<div style="color:#e2e8f0; margin-top:2px;">{h_tier}</div>'
                    f'<div style="color:#94a3b8; font-size:0.75rem; margin-top:4px;">Status: <b style="color:#6ee7b7;">{h_stat}</b> {("• " + h_time) if h_time else ""}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # --- MAIN 2-COLUMN WORKSPACE ---
    mid_col, right_col = st.columns([1.35, 1], gap="large")

    with mid_col:
        tier_icon, tier_color = get_tier_logo(tier_val)

        # 1. PROGRESS BAR CARD
        progress_bar_html = (
            f'<div class="portal-card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px;">'
            f'<div style="display:flex; align-items:center; gap:12px;">'
            f'<div style="width:46px; height:46px; border-radius:12px; background:rgba(16,185,129,0.15); border:1px solid {tier_color}; display:flex; align-items:center; justify-content:center; font-size:1.5rem;">{tier_icon}</div>'
            f'<div>'
            f'<div style="font-size:0.78rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em;">Project ID: <b style="color:#34d399; font-size:0.92rem;">{project_id_val}</b></div>'
            f'<div style="font-size:1.08rem; font-weight:800; color:#f8fafc;">{tier_val}</div>'
            f'<div style="font-size:0.84rem; color:#6ee7b7;">Module Running: <b>{modules_val}</b></div>'
            f'</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<span style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4); color:#34d399; padding:4px 12px; border-radius:999px; font-size:0.78rem; font-weight:700;">30% Advance: {advance_status}</span>'
            f'</div>'
            f'</div>'
            f'<div class="liquid-track">'
            f'<div class="liquid-fill" style="width: {max(progress_val, 8)}%;">'
            f'<div class="dna-inside"><span>🧬</span><span>🧬</span><span>🧬</span><span>🧬</span><span>🧬</span><span>🧬</span></div>'
            f'</div>'
            f'<div class="liquid-percent-label">{progress_val}%</div>'
            f'</div>'
            f'<div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.8rem; color:#94a3b8;">'
            f'<span>Pipeline Status: <b style="color:#e2e8f0;">{status_val}</b></span>'
            f'<span>Real-Time Sheet Sync Active</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(progress_bar_html, unsafe_allow_html=True)

        if st.session_state.last_sheet_sync_msg:
            st.caption(st.session_state.last_sheet_sync_msg)
            
        if st.session_state.checkout_unlocked:
            st.info("🔓 Portal Bypass Enabled. Downloads will not require payment verification.")

        # 2. STEP LOGIC controlled by Sheet Columns + Master Code
        is_ready_for_preview = (progress_val >= 100) or bool(initial_link or final_link or redo_file_link)

        if not is_ready_for_preview:
            st.markdown(
                '<div class="portal-card" style="text-align:center; padding:1.4rem;">'
                '<div style="color:#34d399; font-weight:700; font-size:0.98rem; margin-bottom:4px;">⚙️ Genomic Pipeline Executing on High-Performance Cluster</div>'
                '<div style="color:#94a3b8; font-size:0.86rem;">Once your pipeline reaches <b>100%</b> and your link is uploaded to the sheet, your result preview and unlock controls will appear right here. Click <b>🔄 Refresh Live Sheet Data</b> in the sidebar anytime to check live updates!</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            sheet_marks_paid = str(payment_70_status).strip().lower() in ["paid", "unlocked", "complete", "completed", "yes", "true"]
            is_unlocked = (
                (project_id_val in st.session_state.unlocked_projects)
                or sheet_marks_paid
                or bool(final_link)
                or bool(redo_file_link)
                or master_in_final
                or master_in_redo
                or st.session_state.checkout_unlocked
            )

            preview_img_url = (
                initial_link
                if (initial_link.startswith("http") and any(ext in initial_link.lower() for ext in [".png", ".jpg", ".jpeg", ".webp"]))
                else "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=80"
            )

            if not is_unlocked:
                if payment_70_link.startswith("http"):
                    pay_button_html = f'<a href="{payment_70_link}" target="_blank" rel="noopener noreferrer" class="pay-btn">💳 Pay Remaining 70% Balance Now (${(expected_70_cents/100):.2f}) ↗</a>'
                else:
                    pay_button_html = '<div style="background:rgba(251,191,36,0.15); border:1px solid #fbbf24; color:#fde68a; padding:12px; border-radius:10px; text-align:center; font-weight:700; margin:10px 0;">⚠️ Your 70% balance payment link is being generated by our team. Please check back shortly!</div>'

                locked_card_html = (
                    f'<div class="portal-card">'
                    f'<div class="locked-preview-box">'
                    f'<img src="{preview_img_url}" class="locked-preview-img" alt="Encrypted Preview">'
                    f'<div class="locked-preview-overlay">'
                    f'<span style="background:rgba(16,185,129,0.25); border:1px solid #10b981; color:#6ee7b7; padding:4px 12px; border-radius:999px; font-size:0.78rem; font-weight:700; margin-bottom:8px;">🔒 100% COMPLETE — PREVIEW LOCKED</span>'
                    f'<div style="color:#ffffff; font-weight:800; font-size:1.05rem; max-width:480px;">Your file is complete! To unlock full resolution files, please pay the remaining 70% balance below and copy your Payment ID to unlock.</div>'
                    f'</div>'
                    f'</div>'
                    f'{pay_button_html}'
                    f'<div style="font-size:0.8rem; color:#94a3b8; text-align:center; margin-bottom:8px;">After completing payment, copy your <b>Payment ID</b> and paste it in the box below to immediately unlock your deliverable files.</div>'
                    f'</div>'
                )
                st.markdown(locked_card_html, unsafe_allow_html=True)

                with st.form("unlock_deliverable_form"):
                    unlock_code_in = st.text_input(
                        "Paste Payment ID to Unlock Deliverable Files",
                        placeholder="e.g., pay_Pxyz123456789 or GTS-DEMO-..."
                    )
                    unlock_submit = st.form_submit_button("🔓 Verify & Unlock Full Files", use_container_width=True)

                    if unlock_submit:
                        entered_key = unlock_code_in.strip()
                        if not entered_key:
                            st.warning("Please enter a key.")
                        # 1. INFINITE MASTER KEY CHECK
                        elif entered_key == "GTS-MASTER-UNLIMITED" or has_master_code(entered_key):
                            st.session_state.unlocked_projects.add(project_id_val)
                            st.rerun()

                        # 2. AUTHORIZED DEMO KEY CHECK (One-Time Use)
                        elif entered_key in AUTHORIZED_DEMO_KEYS:
                            burned, burn_date = is_key_burned(entered_key)
                            if burned:
                                st.error(f"❌ Security Lock: This Demo Key was already claimed on {burn_date}.")
                            else:
                                burn_key(entered_key)
                                st.session_state.unlocked_projects.add(project_id_val)
                                st.rerun()

                        # 3. RAZORPAY API VERIFICATION (Amount-Checked & One-Time Use)
                        elif entered_key.startswith("pay_") and len(entered_key) >= 14:
                            burned, burn_date = is_key_burned(entered_key)
                            if burned:
                                st.error(f"❌ Security Lock: This Receipt ID was already claimed on {burn_date}. Keys cannot be shared.")
                            else:
                                try:
                                    # Authenticate with Razorpay Servers
                                    client = razorpay.Client(auth=(st.secrets["razorpay"]["key_id"], st.secrets["razorpay"]["key_secret"]))
                                    payment = client.payment.fetch(entered_key)
                                    
                                    # Verify the transaction was successful
                                    if payment["status"] in ["captured", "authorized"]:
                                        # Verify exact amount matches expected 70% calculation (allowing $1 variance)
                                        if payment["amount"] >= (expected_70_cents - 100) and payment["currency"] == "USD":
                                            burn_key(entered_key)
                                            st.session_state.unlocked_projects.add(project_id_val)
                                            st.rerun()
                                        else:
                                            st.error(f"❌ Invalid Payment Amount. Expected roughly ${(expected_70_cents/100):.2f} USD, but found {payment['amount']/100:.2f} {payment['currency']}.")
                                    else:
                                        st.error(f"❌ Payment Status: {payment['status'].upper()}. This transaction is not complete.")
                                        
                                except Exception as e:
                                    st.error("❌ Invalid Payment ID. The bank API could not verify this transaction.")
                                    
                        else:
                            st.error("❌ Invalid Key Format or Unauthorized Demo Key.")

            else:
                raw_deliverable = final_link if final_link else initial_link
                direct_dl_url = format_direct_download_link(raw_deliverable)

                unlocked_card_html = (
                    f'<div class="portal-card">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">'
                    f'<span style="color:#34d399; font-weight:800; font-size:1.05rem;">✅ Full Deliverable Package Unlocked</span>'
                    f'<span style="font-size:0.75rem; color:#94a3b8;">Universal Device Compatible</span>'
                    f'</div>'
                    f'<img src="{preview_img_url}" style="width:100%; height:200px; object-fit:cover; border-radius:10px; border:1px solid #10b981; margin-bottom:12px;" alt="Unlocked Preview">'
                    f'<a href="{direct_dl_url}" target="_blank" rel="noopener noreferrer" download="GenomeTech_{project_id_val}_Deliverables.csv" class="download-btn">📥 Download Full Project Deliverables ({project_id_val})</a>'
                    f'</div>'
                )
                st.markdown(unlocked_card_html, unsafe_allow_html=True)

                # --- STEP C: REDO OPTION & REMARKS WORKFLOW ---
                redo_state_key = f"redo_done_{project_id_val}"
                feedback_state_key = f"feedback_done_{project_id_val}"
                sync_msg_key = f"sync_msg_{project_id_val}"

                def push_to_sheet_now(action_name, text_val):
                    """Sends exact Column B (Client Email) and Column D (Project ID) to Google Apps Script."""
                    raw_email = str(active_row.iloc[1]).strip() if len(active_row) > 1 else st.session_state.client_email
                    raw_cid = str(active_row.iloc[2]).strip() if len(active_row) > 2 else client_id_val
                    raw_pid = str(active_row.iloc[3]).strip() if len(active_row) > 3 else project_id_val

                    pid_list = [raw_pid]
                    if raw_pid.isdigit():
                        pid_list.append(int(raw_pid))
                    if raw_cid and raw_cid not in pid_list:
                        pid_list.append(raw_cid)
                        if raw_cid.isdigit():
                            pid_list.append(int(raw_cid))

                    for pid_candidate in pid_list:
                        payload = {
                            "clientEmail": raw_email,
                            "projectID": pid_candidate,
                            "action": action_name,
                            "redoText": text_val,
                            "feedbackText": text_val
                        }
                        try:
                            resp = requests.post(
                                APPS_SCRIPT_URL,
                                data=json.dumps(payload),
                                headers={"Content-Type": "text/plain;charset=utf-8"},
                                allow_redirects=True,
                                timeout=10
                            )
                            if "success" in resp.text.lower():
                                return True, "✅ Saved to Google Sheet!"
                        except Exception:
                            pass
                    return False, "⚠️ Saved in portal (Check that Column B 'Client Email' & Column D 'Project ID' are filled in Sheet1)."

                has_redo_file_ready = (
                    bool(redo_file_link)
                    or master_in_redo
                    or (status_val.strip().lower() in ["redo complete", "redo completed", "revised"])
                )
                redo_saved_text = st.session_state.get(redo_state_key, "") or redo_req_existing
                feedback_saved_text = st.session_state.get(feedback_state_key, "") or feedback_existing

                if st.session_state.get(sync_msg_key):
                    st.caption(st.session_state[sync_msg_key])

                if has_redo_file_ready:
                    redo_dl_url = format_direct_download_link(redo_file_link if redo_file_link else final_link)
                    st.markdown(
                        f'<div class="portal-card">'
                        f'<div style="color:#34d399; font-weight:800; font-size:1.02rem; margin-bottom:6px;">🎉 Your Revised Redo File is Ready!</div>'
                        f'<a href="{redo_dl_url}" target="_blank" rel="noopener noreferrer" download="GenomeTech_{project_id_val}_Revised.csv" class="download-btn">📥 Download Revised Deliverable File ({project_id_val})</a>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    if st.session_state.get(feedback_state_key) or bool(feedback_existing):
                        st.markdown(
                            '<div class="portal-card" style="background:rgba(16,185,129,0.15); border:1px solid #10b981; text-align:center;">'
                            '<h4 style="color:#34d399; margin:0;">✨ Thanks for choosing GenomeTech Studio! We will wait for your next visit! ✨</h4>'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown('<div class="portal-card">', unsafe_allow_html=True)
                        st.markdown("#### 💬 Final Remarks, Reviews & Ideas")
                        final_remarks = st.text_area(
                            "Share your remarks, reviews, and ideas to make us better:",
                            key=f"final_rem_input_{project_id_val}"
                        )
                        if st.button("Submit Final Remarks ➔", key=f"btn_final_rem_{project_id_val}", use_container_width=True):
                            if final_remarks.strip():
                                ok, msg = push_to_sheet_now("client_feedback", final_remarks.strip())
                                st.session_state[sync_msg_key] = msg
                                st.session_state[feedback_state_key] = final_remarks.strip()
                                st.rerun()
                            else:
                                st.warning("Please enter your remarks before submitting.")
                        st.markdown('</div>', unsafe_allow_html=True)

                elif bool(redo_saved_text) and not has_redo_file_ready:
                    st.markdown(
                        f'<div class="portal-card" style="border-color:#fbbf24;">'
                        f'<div style="color:#fbbf24; font-weight:800; font-size:1.05rem; margin-bottom:6px;">⏳ Work in progress, please wait...</div>'
                        f'<div style="color:#cbd5e1; font-size:0.88rem; margin-bottom:8px;">Your one-time revision request has been submitted:</div>'
                        f'<div style="background:rgba(2,6,23,0.6); border:1px solid rgba(251,191,36,0.3); padding:10px; border-radius:8px; font-size:0.84rem; color:#fde68a; margin-bottom:8px;">{redo_saved_text}</div>'
                        f'<div style="color:#94a3b8; font-size:0.82rem;">Once we finish redoing your file and paste the link (or Master Code) in the <b>Redo File Link</b> column in the sheet, click <b>🔄 Refresh Live Sheet Data</b> in the sidebar to download it!</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                elif bool(feedback_saved_text):
                    st.markdown(
                        '<div class="portal-card" style="background:rgba(16,185,129,0.15); border:1px solid #10b981; text-align:center;">'
                        '<h4 style="color:#34d399; margin:0;">✨ Thanks for choosing GenomeTech Studio! We will wait for your next visit! ✨</h4>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                else:
                    st.markdown('<div class="portal-card">', unsafe_allow_html=True)
                    st.markdown("#### 🔄 Do you need a Redo / Revision on this deliverable file?")
                    redo_choice = st.radio(
                        "Select an option:",
                        ("No", "Yes"),
                        key=f"redo_radio_choice_{project_id_val}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )

                    if redo_choice == "No":
                        st.markdown("**Remarks, Reviews, Ideas & Future Service Requests**")
                        remarks_txt = st.text_area(
                            "Remarks, reviews, and ideas to make us better:",
                            placeholder="Share your experience with our pipeline speed and report quality...",
                            key=f"no_redo_remarks_{project_id_val}"
                        )
                        service_req_txt = st.text_input(
                            "Any new service request or future pipeline needs?",
                            placeholder="e.g., Need spatial transcriptomics or custom R volcano plots...",
                            key=f"no_redo_service_{project_id_val}"
                        )
                        if st.button("Submit Review & Service Request ➔", key=f"submit_no_btn_{project_id_val}", use_container_width=True):
                            if remarks_txt.strip() or service_req_txt.strip():
                                combined_feedback = f"Redo: No | Remarks & Ideas: {remarks_txt.strip()} | Service Request: {service_req_txt.strip()}"
                                ok, msg = push_to_sheet_now("client_feedback", combined_feedback)
                                st.session_state[sync_msg_key] = msg
                                st.session_state[feedback_state_key] = combined_feedback
                                st.rerun()
                            else:
                                st.warning("Please fill in your remarks or service request before submitting.")
                    else:
                        st.info("⚠️ **One-Time Offer:** This revision is strictly for **math, threshold, or parameter value changes only** (not a whole code rewrite).")
                        redo_details = st.text_area(
                            "Mention the exact math, threshold, or value changes you need:",
                            placeholder="e.g., Change p-value cutoff from 0.05 to 0.01 and log2FC threshold to 1.5...",
                            key=f"yes_redo_details_{project_id_val}"
                        )
                        if st.button("Submit One-Time Redo Request ➔", key=f"submit_yes_btn_{project_id_val}", use_container_width=True):
                            if redo_details.strip():
                                redo_payload_text = f"Redo: Yes | Value Changes Requested: {redo_details.strip()}"
                                ok, msg = push_to_sheet_now("redo_request", redo_payload_text)
                                st.session_state[sync_msg_key] = msg
                                st.session_state[redo_state_key] = redo_payload_text
                                st.rerun()
                            else:
                                st.warning("Please describe the value changes you need.")
                    st.markdown('</div>', unsafe_allow_html=True)

    # --- RIGHT COLUMN: 64-PIECE GENOMIC PICTURE PUZZLE CORNER ---
    with right_col:
        render_64_piece_puzzle(client_id_val)