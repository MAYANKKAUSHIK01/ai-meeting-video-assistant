"""
ui/styles.py — All custom CSS / font injection for the LENS Streamlit app.

Moving CSS out of app.py keeps the main file clean and makes the design
system easy to maintain independently.
"""

from __future__ import annotations

import streamlit as st

# ── Google Fonts link tag ─────────────────────────────────────────────────────
_FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" '
    'rel="stylesheet">'
)

# ── Main stylesheet ───────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ── Icon font safeguard — preserve Material Symbols on Streamlit controls ── */
.material-symbols-rounded,
[class*="material-symbols"],
[class*="material-icons"],
.stIcon, .stIcon *,
[data-testid*="Icon"], [data-testid*="icon"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"] *,
summary *, button svg, span:empty {
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
}

/* ── Base ── */
html, body, .stApp { background: #090E1A !important; color: #E8F4FD !important; }

h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, li, a, .stAlert,
[data-testid="stMarkdownContainer"] {
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Hide Streamlit chrome (toolbar, deploy button, header, footer) ── */
/* Handled by toolbarMode=minimal in .streamlit/config.toml — CSS is a fallback */
#MainMenu                          { display: none !important; }
header[data-testid="stHeader"]     { display: none !important; }
footer                             { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDeployButton"]     { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
.stDeployButton                    { display: none !important; }
/* Keep the top animated stripe visible despite header being hidden */
.stApp::before {
    display: block !important;
}

/* ── Keyframes ── */
@keyframes barSlide {
    0%   { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
@keyframes expandW { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pulse {
    0%, 100% { opacity: 1;    box-shadow: 0 0 0 3px rgba(124,111,255,0.28); }
    50%      { opacity: 0.4; box-shadow: 0 0 0 7px rgba(124,111,255,0.06); }
}
@keyframes glow {
    0%, 100% { text-shadow: 0 0 18px rgba(0,216,255,0.35); }
    50%      { text-shadow: 0 0 32px rgba(0,216,255,0.6); }
}

/* ── Animated top stripe ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #7C6FFF, #00D8FF, #A99BFF, #00D8FF, #7C6FFF);
    background-size: 300% 100%;
    animation: barSlide 4s linear infinite;
    z-index: 99999;
}

/* ── Layout ── */
.main .block-container {
    background: #090E1A !important;
    padding-top: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1526 !important;
    border-right: 1px solid rgba(124,111,255,0.15) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem !important; }
[data-testid="stSidebar"] label { font-family: 'Poppins', sans-serif !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(124,111,255,0.22) !important;
    border-radius: 10px !important;
    color: #E8F4FD !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
    color: rgba(184,212,238,0.3) !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: #7C6FFF !important;
    background: rgba(124,111,255,0.08) !important;
    box-shadow: 0 0 0 3px rgba(124,111,255,0.15) !important;
    outline: none !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(124,111,255,0.22) !important;
    border-radius: 10px !important;
    color: #E8F4FD !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #7C6FFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    padding: 0.65rem 1.4rem !important;
    transition: background 0.18s, transform 0.14s, box-shadow 0.18s !important;
    text-transform: uppercase !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #9C91FF !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(124,111,255,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(124,111,255,0.1) !important;
    color: #A99BFF !important;
    border: 1px solid rgba(124,111,255,0.25) !important;
    box-shadow: none !important;
    font-size: 0.88rem !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(124,111,255,0.18) !important;
    color: #E8F4FD !important;
}

/* ── Text ── */
.stMarkdown p, [data-testid="stMarkdownContainer"] p {
    color: #E8F4FD !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    line-height: 1.8 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0D1526 !important;
    border: 1px solid rgba(124,111,255,0.18) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(124,111,255,0.38) !important;
    box-shadow: 0 3px 18px rgba(124,111,255,0.1) !important;
}
[data-testid="stExpander"] summary {
    color: #7FAFD4 !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 1rem !important;
}

/* ── Alert / progress / spinner ── */
.stAlert {
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
    background: rgba(124,111,255,0.12) !important;
    border-color: rgba(124,111,255,0.3) !important;
    color: #E8F4FD !important;
}
.stProgress > div > div > div { background: #7C6FFF !important; }
.stSpinner > div { border-top-color: #7C6FFF !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,111,255,0.3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7C6FFF; }

hr { border: none !important; border-top: 1px solid rgba(124,111,255,0.15) !important; margin: 1.5rem 0 !important; }

/* ═══════════════════════════════
   CUSTOM COMPONENT CLASSES
   ═══════════════════════════════ */

.wordmark {
    font-family: 'Poppins', sans-serif !important;
    font-size: 2.6rem; font-weight: 800; letter-spacing: 0.14em;
    color: #00D8FF; line-height: 1; display: block;
    animation: fadeDown 0.6s ease both, glow 3s ease-in-out infinite;
}
.wm-sub {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.6rem; letter-spacing: 0.32em; text-transform: uppercase;
    color: rgba(0,216,255,0.45); margin-top: 0.35rem; display: block;
    font-weight: 500; animation: fadeDown 0.6s 0.1s ease both;
}
.wm-rule {
    height: 1px;
    background: linear-gradient(90deg, rgba(124,111,255,0.7), transparent);
    margin: 1rem 0 0.6rem; transform-origin: left;
    animation: expandW 0.8s 0.25s ease both;
}

.pipe-hdr {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.6rem; letter-spacing: 0.26em; text-transform: uppercase;
    color: rgba(184,212,238,0.38); padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(124,111,255,0.12); margin-bottom: 0.4rem; font-weight: 600;
}
.step-row {
    display: flex; align-items: center; gap: 0.55rem;
    padding: 0.42rem 0.55rem; border-radius: 8px;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem; font-weight: 500; color: rgba(184,212,238,0.35);
    margin-bottom: 1px; transition: background 0.25s, color 0.25s;
}
.step-row.active-row { background: rgba(124,111,255,0.14); color: #E8F4FD; }
.step-row.done-row   { color: #00D8FF; }
.step-row.failed-row { color: #FF6B8A; }
.step-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; transition: background 0.25s; }
.dot-active  { background: #7C6FFF; animation: pulse 1.5s ease-in-out infinite; }
.dot-done    { background: #00D8FF; }
.dot-pending { background: rgba(184,212,238,0.18); }
.dot-failed  { background: #FF6B8A; }

.hero-wrap {
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 1.2rem; padding-bottom: 1.4rem;
    border-bottom: 1px solid rgba(124,111,255,0.15); margin-bottom: 1.6rem;
    animation: fadeDown 0.55s ease both; flex-wrap: wrap;
}
.hero-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: clamp(2.6rem, 5vw, 4.6rem); font-weight: 800;
    line-height: 0.95; letter-spacing: -0.01em; color: #E8F4FD; margin: 0;
}
.hero-title span { color: #7C6FFF; }
.hero-meta {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.7rem; color: #7FAFD4; letter-spacing: 0.2em;
    text-transform: uppercase; line-height: 2.6;
    border-left: 2px solid #7C6FFF; padding-left: 0.85rem; font-weight: 500;
}

.tag {
    display: inline-block; font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 0.22rem 0.65rem; border-radius: 20px; margin-right: 0.35rem;
}
.tag-indigo { background: rgba(124,111,255,0.14); color: #A99BFF; border: 1px solid rgba(124,111,255,0.28); }
.tag-cyan   { background: rgba(0,216,255,0.1);    color: #00D8FF; border: 1px solid rgba(0,216,255,0.25); }
.tag-dim    { background: rgba(255,255,255,0.06);  color: #7FAFD4; border: 1px solid rgba(184,212,238,0.15); }

.title-card {
    background: #0D1526; border: 1px solid rgba(124,111,255,0.2);
    border-top: 2px solid #7C6FFF; border-radius: 14px;
    padding: 1.3rem 1.6rem 1.1rem; margin-bottom: 1.2rem;
    position: relative; animation: fadeUp 0.5s ease both;
}
.title-card::after {
    content: 'SESSION'; position: absolute; top: 1rem; right: 1.3rem;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.58rem; letter-spacing: 0.3em; color: rgba(124,111,255,0.4); font-weight: 600;
}
.tc-lbl {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem; letter-spacing: 0.24em; text-transform: uppercase;
    color: #7FAFD4; margin-bottom: 0.45rem; font-weight: 600;
}
.tc-val {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.8rem; font-weight: 700; color: #E8F4FD; line-height: 1.2;
}

.card {
    background: #0D1526; border: 1px solid rgba(124,111,255,0.18);
    border-top: 2px solid rgba(124,111,255,0.5); border-radius: 14px;
    padding: 1.15rem 1.25rem; margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.18s;
    animation: fadeUp 0.5s ease both;
}
.card:hover { border-color: rgba(124,111,255,0.4); box-shadow: 0 4px 22px rgba(124,111,255,0.12); transform: translateY(-2px); }
.card-label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem; letter-spacing: 0.24em; text-transform: uppercase;
    color: #7FAFD4; margin-bottom: 0.7rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;
}
.card-label::before { content: ''; display: inline-block; width: 12px; height: 2px; background: #7C6FFF; border-radius: 2px; }
.card-body { font-family: 'Nunito', sans-serif !important; font-size: 0.97rem; line-height: 1.8; color: #C8E0F4; }

.tx-box {
    background: #111C30; border: 1px solid rgba(124,111,255,0.15);
    border-radius: 8px; padding: 1rem;
    font-family: 'Nunito', sans-serif !important; font-size: 0.82rem;
    line-height: 1.85; max-height: 260px; overflow-y: auto;
    color: #7FAFD4; white-space: pre-wrap; word-break: break-word;
}

.notif {
    display: flex; align-items: center; gap: 0.6rem;
    background: rgba(124,111,255,0.1); border: 1px solid rgba(124,111,255,0.28);
    border-radius: 10px; padding: 0.7rem 1rem;
    font-family: 'Poppins', sans-serif !important; font-size: 0.8rem;
    font-weight: 500; color: #A99BFF; margin-bottom: 0.5rem;
    animation: fadeDown 0.4s ease both;
}
.notif-dot { width: 8px; height: 8px; border-radius: 50%; background: #7C6FFF; flex-shrink: 0; animation: pulse 1.5s ease-in-out infinite; }

.chat-section-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.8rem; font-weight: 700; letter-spacing: -0.01em;
    color: #E8F4FD; margin-bottom: 0.9rem;
    display: flex; align-items: center; gap: 0.8rem; animation: fadeUp 0.5s ease both;
}
.chat-section-title::after { content: ''; flex: 1; height: 1px; background: rgba(124,111,255,0.15); }

.chat-wrap {
    background: #0D1526; border: 1px solid rgba(124,111,255,0.18);
    border-radius: 14px; padding: 1rem 1.1rem;
    max-height: 400px; overflow-y: auto; margin-bottom: 0.75rem;
}
.msg { margin-bottom: 0.75rem; display: flex; flex-direction: column; animation: fadeUp 0.3s ease both; }
.msg-label { font-family: 'Poppins', sans-serif !important; font-size: 0.62rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.28rem; }
.user-label { color: #00D8FF; align-self: flex-end; }
.bot-label  { color: #A99BFF; align-self: flex-start; }
.msg-bubble { display: inline-block; padding: 0.65rem 1rem; font-family: 'Nunito', sans-serif !important; font-size: 0.95rem; line-height: 1.7; max-width: 86%; font-weight: 500; }
.user-bubble { background: rgba(0,216,255,0.09); border: 1px solid rgba(0,216,255,0.2); align-self: flex-end; color: #E8F4FD; border-radius: 14px 14px 4px 14px; }
.bot-bubble  { background: rgba(124,111,255,0.1); border: 1px solid rgba(124,111,255,0.2); align-self: flex-start; color: #E8F4FD; border-radius: 14px 14px 14px 4px; }

.await-card { background: #0D1526; border: 1px dashed rgba(124,111,255,0.3); border-radius: 14px; padding: 2.5rem 2rem; text-align: center; margin-bottom: 0.75rem; }
.await-label { font-family: 'Poppins', sans-serif !important; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.1em; color: rgba(124,111,255,0.4); margin-bottom: 0.45rem; }
.await-body  { font-family: 'Nunito', sans-serif !important; font-size: 0.95rem; color: #7FAFD4; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 2rem; text-align: center; animation: fadeIn 0.6s ease both; }
.empty-glyph { font-family: 'Poppins', sans-serif !important; font-size: 6rem; font-weight: 800; letter-spacing: 0.12em; color: rgba(124,111,255,0.25); line-height: 1; margin-bottom: 1.2rem; }
.empty-title { font-family: 'Poppins', sans-serif !important; font-size: 2rem; font-weight: 700; color: #7FAFD4; margin-bottom: 0.5rem; }
.empty-body  { font-family: 'Nunito', sans-serif !important; font-size: 1rem; color: #7FAFD4; max-width: 370px; line-height: 1.75; }

/* ── Custom High-Fidelity Slider ── */
[data-testid="stSlider"], .stSlider {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(124, 111, 255, 0.15) !important;
    border-radius: 12px !important;
    padding: 1.1rem 1.2rem 0.9rem 1.2rem !important;
    margin-bottom: 1.2rem !important;
    transition: border-color 0.22s, box-shadow 0.22s !important;
}
[data-testid="stSlider"]:hover, .stSlider:hover {
    border-color: rgba(124, 111, 255, 0.3) !important;
    box-shadow: 0 4px 18px rgba(124, 111, 255, 0.06) !important;
}
[data-testid="stSlider"] label, .stSlider label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #A99BFF !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 0.75rem !important;
    text-transform: uppercase !important;
}
/* Base track styling */
[data-testid="stSlider"] [data-baseweb="slider"] > div, .stSlider [data-baseweb="slider"] > div {
    background-color: rgba(255, 255, 255, 0.08) !important;
    height: 6px !important;
    border-radius: 4px !important;
}
/* Selected range track (glowing gradient) */
[data-testid="stSlider"] [data-baseweb="slider"] > div > div, .stSlider [data-baseweb="slider"] > div > div {
    background: linear-gradient(90deg, #7C6FFF, #00D8FF) !important;
    height: 6px !important;
    border-radius: 4px !important;
}
/* Thumb knob */
[data-testid="stSlider"] [role="slider"], .stSlider [role="slider"] {
    background-color: #090E1A !important;
    border: 2px solid #00D8FF !important;
    box-shadow: 0 0 12px rgba(0, 216, 255, 0.6) !important;
    width: 18px !important;
    height: 18px !important;
    /* Do NOT transition transform, as it causes terrible lag/stutter while dragging! Only transition glow. */
    transition: box-shadow 0.15s ease !important;
}
[data-testid="stSlider"] [role="slider"]:hover, .stSlider [role="slider"]:hover {
    box-shadow: 0 0 20px rgba(0, 216, 255, 0.95) !important;
}
/* Value and label nodes */
[data-testid="stSlider"] div[data-baseweb="slider"] ~ div, .stSlider div[data-baseweb="slider"] ~ div {
    color: #E8F4FD !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
}

/* ── Hide "Press Enter to apply" helpers globally ── */
[data-testid="InputInstructions"], .stTextInput small {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}

@media (max-width: 768px) {
    .main .block-container { padding-left: 0.85rem !important; padding-right: 0.85rem !important; }
    .hero-title { font-size: 2.2rem !important; }
    .hero-meta  { font-size: 0.62rem !important; line-height: 2.2 !important; }
    .tc-val     { font-size: 1.4rem !important; }
    .card       { padding: 0.9rem 1rem !important; }
    .card-body  { font-size: 0.88rem !important; }
    .msg-bubble { max-width: 95% !important; font-size: 0.88rem !important; }
    .wordmark   { font-size: 2rem !important; }
    .chat-section-title { font-size: 1.4rem !important; }
    .empty-glyph { font-size: 3.5rem !important; }
    .empty-title { font-size: 1.5rem !important; }
    .await-card  { padding: 1.5rem 1rem !important; }
}
</style>
"""


def inject_styles() -> None:
    """Inject Google Fonts link and all custom CSS into the Streamlit page."""
    st.markdown(_FONT_LINK, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)
