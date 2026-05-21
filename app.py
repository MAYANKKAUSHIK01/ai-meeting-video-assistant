import os, warnings
# Suppress noisy transformers / HuggingFace advisory warnings before any imports
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

st.set_page_config(
    page_title="LENS — Meeting Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown('<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">', unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* ── ICON FONT SAFEGUARD ── */
/* Force Streamlit's icon elements to retain the Material Symbols font */
.material-symbols-rounded,
[class*="material-symbols"],
[class*="material-icons"],
.stIcon,
.stIcon *,
[data-testid*="Icon"],
[data-testid*="icon"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"] *,
summary *,
button svg,
span:empty {
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
}

/* ── Global overrides ── */
html, body, .stApp { 
    background: #090E1A !important; 
    color: #E8F4FD !important;
}

/* Apply custom font ONLY to actual text elements, strictly avoiding Streamlit UI controls */
h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown p, li, a, .stAlert,
[data-testid="stMarkdownContainer"] {
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Palette ── */
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
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes expandW {
    from { transform: scaleX(0); }
    to   { transform: scaleX(1); }
}
@keyframes pulse {
    0%, 100% { opacity: 1;    box-shadow: 0 0 0 3px rgba(124,111,255,0.28); }
    50%      { opacity: 0.4; box-shadow: 0 0 0 7px rgba(124,111,255,0.06); }
}
@keyframes glow {
    0%, 100% { text-shadow: 0 0 18px rgba(0,216,255,0.35); }
    50%      { text-shadow: 0 0 32px rgba(0,216,255,0.6); }
}

/* ── Global overrides ── */
html, body { background: #090E1A !important; }
.stApp     { background: #090E1A !important; }

.main .block-container {
    background: #090E1A !important;
    padding-top: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* animated top stripe */
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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1526 !important;
    border-right: 1px solid rgba(124,111,255,0.15) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem !important; }
/* Target only actual text inputs/labels — NOT generic div/span which host icons */
[data-testid="stSidebar"] label {
    font-family: 'Poppins', sans-serif !important;
}
.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(124,111,255,0.22) !important;
    border-radius: 10px !important;
    color: #E8F4FD !important;
    -webkit-text-fill-color: #E8F4FD !important; /* Force visibility on WebKit browsers */
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
}
.stTextInput input::placeholder {
    color: rgba(184,212,238,0.3) !important;
}
.stTextInput input:focus {
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
[data-testid="stSidebar"] [data-baseweb="select"] span:not([class*="material"]) { 
    color: #E8F4FD !important; 
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
    transform: none !important;
    box-shadow: none !important;
}

/* ── Main text ── */
.stMarkdown p, [data-testid="stMarkdownContainer"] p {
    color: #E8F4FD !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
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
[data-testid="stExpander"] summary:hover { color: #E8F4FD !important; }

/* ── Alert ── */
.stAlert {
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.9rem !important;
    background: rgba(124,111,255,0.12) !important;
    border-color: rgba(124,111,255,0.3) !important;
    color: #E8F4FD !important;
}

/* ── Progress & spinner ── */
.stProgress > div > div > div { background: #7C6FFF !important; }
.stSpinner > div { border-top-color: #7C6FFF !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,111,255,0.3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7C6FFF; }

hr { border: none !important; border-top: 1px solid rgba(124,111,255,0.15) !important; margin: 1.5rem 0 !important; }

/* ════════════════════════════════
   CUSTOM COMPONENT CLASSES
   ════════════════════════════════ */

.wordmark {
    font-family: 'Poppins', sans-serif !important;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    color: #00D8FF;
    line-height: 1;
    display: block;
    animation: fadeDown 0.6s ease both, glow 3s ease-in-out infinite;
}
.wm-sub {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.6rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: rgba(0,216,255,0.45);
    margin-top: 0.35rem;
    display: block;
    font-weight: 500;
    animation: fadeDown 0.6s 0.1s ease both;
}
.wm-rule {
    height: 1px;
    background: linear-gradient(90deg, rgba(124,111,255,0.7), transparent);
    margin: 1rem 0 0.6rem;
    transform-origin: left;
    animation: expandW 0.8s 0.25s ease both;
}

.pipe-hdr {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.6rem;
    letter-spacing: 0.26em;
    text-transform: uppercase;
    color: rgba(184,212,238,0.38);
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(124,111,255,0.12);
    margin-bottom: 0.4rem;
    font-weight: 600;
}
.step-row {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.42rem 0.55rem;
    border-radius: 8px;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem;
    font-weight: 500;
    color: rgba(184,212,238,0.35);
    margin-bottom: 1px;
    transition: background 0.25s, color 0.25s;
}
.step-row.active-row { background: rgba(124,111,255,0.14); color: #E8F4FD; }
.step-row.done-row   { color: #00D8FF; }
.step-row.failed-row { color: #FF6B8A; }
.step-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    transition: background 0.25s;
}
.dot-active  { background: #7C6FFF; animation: pulse 1.5s ease-in-out infinite; }
.dot-done    { background: #00D8FF; }
.dot-pending { background: rgba(184,212,238,0.18); }
.dot-failed  { background: #FF6B8A; }

.hero-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1.2rem;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid rgba(124,111,255,0.15);
    margin-bottom: 1.6rem;
    animation: fadeDown 0.55s ease both;
    flex-wrap: wrap;
}
.hero-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: clamp(2.6rem, 5vw, 4.6rem);
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: -0.01em;
    color: #E8F4FD;
    margin: 0;
}
.hero-title span { color: #7C6FFF; }
.hero-meta {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.7rem;
    color: #7FAFD4;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    line-height: 2.6;
    border-left: 2px solid #7C6FFF;
    padding-left: 0.85rem;
    font-weight: 500;
}

.tag {
    display: inline-block;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.22rem 0.65rem;
    border-radius: 20px;
    margin-right: 0.35rem;
}
.tag-indigo { background: rgba(124,111,255,0.14); color: #A99BFF; border: 1px solid rgba(124,111,255,0.28); }
.tag-cyan   { background: rgba(0,216,255,0.1);    color: #00D8FF; border: 1px solid rgba(0,216,255,0.25); }
.tag-dim    { background: rgba(255,255,255,0.06);  color: #7FAFD4; border: 1px solid rgba(184,212,238,0.15); }

.title-card {
    background: #0D1526;
    border: 1px solid rgba(124,111,255,0.2);
    border-top: 2px solid #7C6FFF;
    border-radius: 14px;
    padding: 1.3rem 1.6rem 1.1rem;
    margin-bottom: 1.2rem;
    position: relative;
    animation: fadeUp 0.5s ease both;
}
.title-card::after {
    content: 'SESSION';
    position: absolute;
    top: 1rem; right: 1.3rem;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.58rem;
    letter-spacing: 0.3em;
    color: rgba(124,111,255,0.4);
    font-weight: 600;
}
.tc-lbl {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: #7FAFD4;
    margin-bottom: 0.45rem;
    font-weight: 600;
}
.tc-val {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.8rem;
    font-weight: 700;
    color: #E8F4FD;
    line-height: 1.2;
}

.card {
    background: #0D1526;
    border: 1px solid rgba(124,111,255,0.18);
    border-top: 2px solid rgba(124,111,255,0.5);
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.18s;
    animation: fadeUp 0.5s ease both;
}
.card:hover {
    border-color: rgba(124,111,255,0.4);
    box-shadow: 0 4px 22px rgba(124,111,255,0.12);
    transform: translateY(-2px);
}
.card-label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: #7FAFD4;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
}
.card-label::before {
    content: '';
    display: inline-block;
    width: 12px; height: 2px;
    background: #7C6FFF;
    border-radius: 2px;
}
.card-body {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.97rem;
    line-height: 1.8;
    color: #C8E0F4;
    font-weight: 400;
}

.tx-box {
    background: #111C30;
    border: 1px solid rgba(124,111,255,0.15);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem;
    line-height: 1.85;
    max-height: 260px;
    overflow-y: auto;
    color: #7FAFD4;
    white-space: pre-wrap;
    word-break: break-word;
}

.notif {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: rgba(124,111,255,0.1);
    border: 1px solid rgba(124,111,255,0.28);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.8rem;
    font-weight: 500;
    color: #A99BFF;
    margin-bottom: 0.5rem;
    animation: fadeDown 0.4s ease both;
}
.notif-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #7C6FFF;
    flex-shrink: 0;
    animation: pulse 1.5s ease-in-out infinite;
}

.chat-section-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #E8F4FD;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    animation: fadeUp 0.5s ease both;
}
.chat-section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(124,111,255,0.15);
}

.chat-wrap {
    background: #0D1526;
    border: 1px solid rgba(124,111,255,0.18);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 0.75rem;
}
.msg {
    margin-bottom: 0.75rem;
    display: flex;
    flex-direction: column;
    animation: fadeUp 0.3s ease both;
}
.msg-label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.28rem;
}
.user-label { color: #00D8FF;  align-self: flex-end; }
.bot-label  { color: #A99BFF; align-self: flex-start; }
.msg-bubble {
    display: inline-block;
    padding: 0.65rem 1rem;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem;
    line-height: 1.7;
    max-width: 86%;
    font-weight: 500;
}
.user-bubble {
    background: rgba(0,216,255,0.09);
    border: 1px solid rgba(0,216,255,0.2);
    align-self: flex-end;
    color: #E8F4FD;
    border-radius: 14px 14px 4px 14px;
}
.bot-bubble {
    background: rgba(124,111,255,0.1);
    border: 1px solid rgba(124,111,255,0.2);
    align-self: flex-start;
    color: #E8F4FD;
    border-radius: 14px 14px 14px 4px;
}

.await-card {
    background: #0D1526;
    border: 1px dashed rgba(124,111,255,0.3);
    border-radius: 14px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 0.75rem;
}
.await-label {
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: rgba(124,111,255,0.4);
    margin-bottom: 0.45rem;
}
.await-body {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem;
    color: #7FAFD4;
    font-weight: 400;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
    animation: fadeIn 0.6s ease both;
}
.empty-glyph {
    font-family: 'Poppins', sans-serif !important;
    font-size: 6rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    color: rgba(124,111,255,0.25);
    line-height: 1;
    margin-bottom: 1.2rem;
}
.empty-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 2rem;
    font-weight: 700;
    color: #7FAFD4;
    margin-bottom: 0.5rem;
}
.empty-body {
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem;
    color: #7FAFD4;
    max-width: 370px;
    line-height: 1.75;
    font-weight: 400;
}

/* ── Hide only unwanted Streamlit chrome — do NOT touch the header element ── */
/* Hiding the header breaks the sidebar toggle button inside it.              */
#MainMenu                        { display: none !important; }
footer                           { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stDeployButton"]   { display: none !important; }
.stDeployButton                  { display: none !important; }

/* Style the header bar to match the dark theme instead of hiding it */
header[data-testid="stHeader"] {
    background: #090E1A !important;
    border-bottom: 1px solid rgba(124, 111, 255, 0.1) !important;
    box-shadow: none !important;
}

/* Style the sidebar toggle button to match the brand theme */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(124, 111, 255, 0.3) !important;
    border-radius: 8px !important;
    color: #A99BFF !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: #A99BFF !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: rgba(124, 111, 255, 0.15) !important;
    border-color: #7C6FFF !important;
}

/* Keep the top animated stripe visible */
.stApp::before {
    display: block !important;
}


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
    .main .block-container {
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }
    .hero-title { font-size: 2.2rem !important; }
    .hero-meta  { font-size: 0.62rem !important; line-height: 2.2 !important; }
    .tc-val     { font-size: 1.4rem !important; }
    .card       { padding: 0.9rem 1rem !important; }
    .card-body  { font-size: 0.88rem !important; }
    .msg-bubble { max-width: 95% !important; font-size: 0.88rem !important; }
    .wordmark   { font-size: 2rem !important; }
    .chat-section-title { font-size: 1.4rem !important; }
    .empty-glyph  { font-size: 3.5rem !important; }
    .empty-title  { font-size: 1.5rem !important; }
    .await-card   { padding: 1.5rem 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ──────────────────────────────────────────────────────────────────
STEPS_META = [
    ("audio",      "01", "Audio Processing"),
    ("transcript", "02", "Transcription"),
    ("title",      "03", "Title Generation"),
    ("summary",    "04", "Summarisation"),
    ("extract",    "05", "Extraction"),
    ("rag",        "06", "RAG Engine"),
]

def step_css(steps, key):
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active",  "active-row"
    if s == "done":    return "dot-done",     "done-row"
    if s == "failed":  return "dot-failed",   "failed-row"
    return "dot-pending", ""

def draw_status(placeholder):
    html = '<div class="pipe-hdr">— Pipeline Status</div>'
    for key, num, label in STEPS_META:
        dot_cls, row_cls = step_css(st.session_state.pipeline_steps, key)
        html += (
            f'<div class="step-row {row_cls}">'
            f'<div class="step-dot {dot_cls}"></div>'
            f'<span style="color:rgba(184,212,238,0.28);font-size:.7rem;margin-right:2px">{num}</span>'
            f'{label}</div>'
        )
    placeholder.markdown(html, unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 .2rem">
        <span class="wordmark">LENS</span>
        <span class="wm-sub">Meeting Intelligence System</span>
        <div class="wm-rule"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<span class="tag tag-dim">Input</span>', unsafe_allow_html=True)

    source = st.text_input(
        "Source",
        placeholder="https://youtube.com/… or /path/to/file.mp4",
        label_visibility="visible",
    )
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    
    # Model size selector for Local Whisper
    model_size = "base"
    if language == "english":
        model_size = st.selectbox(
            "Whisper Model Size",
            ["tiny", "base", "small", "medium"],
            index=1,  # Default to base (blazingly fast on CPU)
            format_func=lambda x: {
                "tiny": "⚡⚡⚡ tiny (fastest)",
                "base": "⚡ base (balanced)",
                "small": "🐢 small (accurate)",
                "medium": "🐢🐢 medium (heavy)",
            }[x],
            help="Smaller models are much faster on CPU but slightly less accurate."
        )
    else:
        st.info("Hinglish uses Sarvam AI's high-speed GPU API.")
        
    # Dynamic chunk size selector
    chunk_minutes = st.slider(
        "Audio Chunk Size (minutes)",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        help="Slices the audio into smaller parts. 10 minutes is optimal for typical meetings."
    )
        
    run_btn = st.button("⚡  Run Analysis", use_container_width=True)

    sidebar_placeholder = st.empty()
    if st.session_state.pipeline_done:
        draw_status(sidebar_placeholder)

    st.markdown("""
    <div style="margin-top:2rem;font-family:'Poppins',sans-serif;font-size:.58rem;
                letter-spacing:.22em;color:rgba(124,111,255,0.22);
                text-align:center;text-transform:uppercase;font-weight:500">
        Lens v1.0 · AI-powered
    </div>""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">Meeting<br><span>Intelligence</span></div>
    <div class="hero-meta">Transcribe<br>Summarise<br>Interrogate</div>
</div>
""", unsafe_allow_html=True)

# ─── Pipeline run ─────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Source is required — enter a YouTube URL or file path.")
    else:
        st.session_state.update({
            "pipeline_done": False,
            "result": None,
            "chat_history": [],
            "pipeline_steps": {k: "pending" for k, *_ in STEPS_META},
        })
        draw_status(sidebar_placeholder)
        prog = st.empty()

        def tick(key, state):
            st.session_state.pipeline_steps[key] = state
            draw_status(sidebar_placeholder)

        try:
            prog.markdown("""
            <div class="notif">
                <div class="notif-dot"></div>
                Pipeline initialised — monitor progress in the sidebar.
            </div>""", unsafe_allow_html=True)

            tick("audio", "active");      chunks     = process_input(source, chunk_minutes=chunk_minutes);               tick("audio", "done")
            tick("transcript", "active"); transcript = transcribe_all(chunks, language, model_size=model_size);    tick("transcript", "done")
            tick("title", "active");      title      = generate_title(transcript);          tick("title", "done")
            tick("summary", "active");    summary    = summarize(transcript);               tick("summary", "done")

            tick("extract", "active")
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor() as ex:
                fa = ex.submit(extract_action_items,  transcript)
                fd = ex.submit(extract_key_decisions, transcript)
                fq = ex.submit(extract_questions,     transcript)
                action_items = fa.result()
                decisions    = fd.result()
                questions    = fq.result()
            tick("extract", "done")

            tick("rag", "active"); rag_chain = build_rag_chain(transcript); tick("rag", "done")

            st.session_state.result = {
                "title": title, "transcript": transcript, "summary": summary,
                "action_items": action_items, "key_decisions": decisions,
                "open_questions": questions, "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            prog.success("Analysis complete.")
            time.sleep(0.6)
            prog.empty()
            st.rerun()

        except Exception as e:
            for k, *_ in STEPS_META:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "failed"
            draw_status(sidebar_placeholder)
            prog.error(f"Pipeline failed: {e}")

# ─── Results ──────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="title-card">
        <div class="tc-lbl">Session Title</div>
        <div class="tc-val">{r['title']}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">Summary</div>
            <div class="card-body">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        with st.expander("Full Transcript"):
            st.markdown(
                f'<div class="tx-box">{r["transcript"]}</div>',
                unsafe_allow_html=True,
            )

    c1, c2, c3 = st.columns(3, gap="medium")
    for col, label, content in [
        (c1, "Action Items",   r["action_items"]),
        (c2, "Key Decisions",  r["key_decisions"]),
        (c3, "Open Questions", r["open_questions"]),
    ]:
        with col:
            st.markdown(f"""
            <div class="card">
                <div class="card-label">{label}</div>
                <div class="card-body">{content}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="chat-section-title">Interrogate</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                html += (
                    '<div class="msg" style="align-items:flex-end">'
                    '<span class="msg-label user-label">You</span>'
                    f'<div class="msg-bubble user-bubble">{msg["content"]}</div>'
                    '</div>'
                )
            else:
                html += (
                    '<div class="msg" style="align-items:flex-start">'
                    '<span class="msg-label bot-label">Lens AI</span>'
                    f'<div class="msg-bubble bot-bubble">{msg["content"]}</div>'
                    '</div>'
                )
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="await-card">
            <div class="await-label">Awaiting Query</div>
            <div class="await-body">
                Ask anything about your meeting — decisions, owners, unresolved threads.
            </div>
        </div>""", unsafe_allow_html=True)

    q_col, btn_col = st.columns([5, 1], gap="small")
    with q_col:
        user_q = st.text_input(
            "Query",
            placeholder="Who owns the migration task?",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send", use_container_width=True)

    if send and user_q.strip():
        with st.spinner("Processing…"):
            answer = ask_question(r["rag_chain"], user_q.strip())
        st.session_state.chat_history += [
            {"role": "user",      "content": user_q.strip()},
            {"role": "assistant", "content": answer},
        ]
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear History", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("""
    <div style="margin-top:1.5rem">
        <span class="tag tag-indigo">Transcription</span>
        <span class="tag tag-cyan">Summarisation</span>
        <span class="tag tag-dim">RAG Chat</span>
    </div>""", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-glyph">LENS</div>
        <div class="empty-title">Ready to Analyse</div>
        <div class="empty-body">
            Paste a YouTube URL or local file path in the sidebar,
            select your language, and run the pipeline.
        </div>
        <div style="margin-top:2rem">
            <span class="tag tag-indigo">Transcription</span>
            <span class="tag tag-cyan">Summarisation</span>
            <span class="tag tag-dim">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)
