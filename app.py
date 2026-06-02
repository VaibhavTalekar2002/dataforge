import streamlit as st
import pandas as pd
import requests
import uuid
import datetime
import html

from cleaner import analyze_dataframe, clean_dataframe
from profiler import generate_profile
from store import datasets, jobs, audit_logs


st.set_page_config(
    page_title="DataForge - Smart Cleaning",
    page_icon="DF",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #07111f;
    --surface: #ffffff;
    --surface-soft: #f8fafc;
    --ink: #101828;
    --muted: #667085;
    --line: #d9e2ec;
    --primary: #2457d6;
    --primary-dark: #163f9f;
    --primary-soft: #eaf0ff;
    --teal: #0f8f83;
    --green: #11845b;
    --amber: #b7791f;
    --red: #c24138;
    --cyan: #22d3ee;
    --cyan-soft: rgba(34, 211, 238, 0.18);
    --violet: #7c3aed;
    --magenta: #d946ef;
    --electric: #38bdf8;
    --dark-panel: rgba(255, 255, 255, 0.95);
    --shadow: 0 18px 50px rgba(16, 24, 40, 0.08);
}

html, body, [class*="css"] {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 0%, rgba(34, 211, 238, 0.2), transparent 28rem),
        radial-gradient(circle at 86% 8%, rgba(124, 58, 237, 0.18), transparent 28rem),
        linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, #081426, #f5f7fb 420px),
        var(--bg);
    background-size: auto, auto, 42px 42px, 42px 42px, auto, auto;
    color: var(--ink);
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 1180px;
    padding: 2rem 2rem 4rem;
}

.app-shell {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.hero {
    background:
        linear-gradient(135deg, rgba(8, 20, 38, 0.98), rgba(16, 44, 91, 0.94)),
        radial-gradient(circle at 80% 20%, rgba(34, 211, 238, 0.34), transparent 24%),
        radial-gradient(circle at 10% 95%, rgba(124, 58, 237, 0.25), transparent 28%);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 8px;
    padding: 2.25rem;
    color: #ffffff;
    box-shadow: 0 24px 70px rgba(3, 12, 28, 0.32), 0 0 0 1px rgba(34, 211, 238, 0.08);
    position: relative;
    overflow: hidden;
    isolation: isolate;
    animation: panel-rise 680ms ease-out both;
}

.hero:before {
    content: "";
    position: absolute;
    inset: -2px;
    z-index: -1;
    background: linear-gradient(115deg, transparent 0%, rgba(34, 211, 238, 0.55) 24%, rgba(124, 58, 237, 0.5) 48%, transparent 72%);
    background-size: 220% 100%;
    animation: energy-sweep 7s ease-in-out infinite;
    opacity: 0.42;
}

.hero:after {
    content: "";
    position: absolute;
    right: -70px;
    bottom: -100px;
    width: 280px;
    height: 280px;
    border: 1px solid rgba(255, 255, 255, 0.24);
    border-radius: 50%;
    animation: orbit-pulse 9s ease-in-out infinite;
}

.eyebrow {
    margin: 0 0 0.8rem;
    color: rgba(255, 255, 255, 0.78);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
}

.hero h1 {
    margin: 0;
    font-size: clamp(2.2rem, 5vw, 4.35rem);
    line-height: 1;
    letter-spacing: 0;
    text-shadow: 0 0 32px rgba(34, 211, 238, 0.36);
}

.hero p {
    max-width: 680px;
    margin: 1rem 0 0;
    color: rgba(255, 255, 255, 0.84);
    font-size: 1.02rem;
    line-height: 1.65;
}

.hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin-top: 1.35rem;
}

.tag {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 0 0.8rem;
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 700;
    backdrop-filter: blur(12px);
    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

.tag:hover {
    transform: translateY(-2px);
    border-color: rgba(34, 211, 238, 0.68);
    background: rgba(34, 211, 238, 0.14);
}

.section-head {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 2.2rem 0 1rem;
    padding: 0.8rem 0.9rem;
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 8px;
    background:
        linear-gradient(90deg, rgba(8, 20, 38, 0.92), rgba(16, 44, 91, 0.68)),
        radial-gradient(circle at 95% 50%, rgba(217, 70, 239, 0.16), transparent 34%);
    box-shadow: 0 14px 34px rgba(3, 12, 28, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    animation: panel-rise 520ms ease-out both;
    position: relative;
    overflow: hidden;
}

.section-head:before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(115deg, transparent 0%, rgba(34, 211, 238, 0.16) 42%, transparent 70%);
    transform: translateX(-100%);
    animation: glass-scan 5.5s ease-in-out infinite;
    pointer-events: none;
}

.section-head:after {
    content: "";
    flex: 1;
    min-width: 42px;
    height: 3px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--cyan), var(--magenta), transparent, var(--cyan));
    background-size: 220% 100%;
    box-shadow: 0 0 18px rgba(34, 211, 238, 0.45);
    animation: neon-flow 3.2s ease-in-out infinite;
    position: relative;
    z-index: 1;
}

.step {
    width: 34px;
    height: 34px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    color: #ffffff;
    font-size: 0.82rem;
    font-weight: 800;
    box-shadow: 0 0 22px rgba(34, 211, 238, 0.25);
    animation: step-glow 3.8s ease-in-out infinite;
    position: relative;
    z-index: 1;
}

.section-head h2 {
    margin: 0;
    color: #ffffff;
    font-size: 1.12rem;
    line-height: 1.2;
    letter-spacing: 0;
    text-shadow: 0 0 18px rgba(34, 211, 238, 0.34);
    position: relative;
    z-index: 1;
}

.issue-count {
    border-radius: 999px;
    background: rgba(217, 70, 239, 0.16);
    color: #ffffff;
    border: 1px solid rgba(217, 70, 239, 0.35);
    padding: 0.28rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 800;
    box-shadow: 0 0 18px rgba(217, 70, 239, 0.18);
    position: relative;
    z-index: 1;
}

.hint {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.6;
    margin: -0.35rem 0 1rem;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.96)),
        radial-gradient(circle at 88% 12%, var(--cyan-soft), transparent 32%);
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 8px;
    padding: 1.1rem 1.15rem;
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.04);
    transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    animation: panel-rise 560ms ease-out both;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    border-color: rgba(34, 211, 238, 0.55);
    box-shadow: 0 18px 34px rgba(16, 24, 40, 0.12), 0 0 26px rgba(34, 211, 238, 0.16);
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: var(--ink);
    font-size: 2rem;
    font-weight: 800;
}

[data-testid="stMetricDelta"] {
    color: var(--green);
}

[data-testid="stFileUploader"] {
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.97), rgba(239, 246, 255, 0.94));
    border: 1px dashed rgba(34, 211, 238, 0.46);
    border-radius: 8px;
    padding: 0.55rem;
    box-shadow: 0 12px 28px rgba(16, 24, 40, 0.05);
    transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
    animation: panel-rise 600ms ease-out both;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--cyan);
    background: #fbfdff;
    transform: translateY(-2px);
    box-shadow: 0 18px 34px rgba(16, 24, 40, 0.1), 0 0 28px rgba(34, 211, 238, 0.18);
}

[data-testid="stFileUploadDropzone"] {
    background:
        linear-gradient(135deg, rgba(248, 250, 252, 0.96), rgba(234, 240, 255, 0.9)),
        radial-gradient(circle at 92% 20%, rgba(217, 70, 239, 0.1), transparent 30%);
    border-radius: 8px;
}

.stButton > button, .stDownloadButton > button {
    min-height: 44px;
    border-radius: 8px;
    border: 1px solid transparent;
    font-weight: 800;
    letter-spacing: 0;
    transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--violet));
    color: #ffffff;
    box-shadow: 0 10px 22px rgba(36, 87, 214, 0.22), 0 0 22px rgba(34, 211, 238, 0.12);
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: linear-gradient(135deg, var(--primary-dark), #5b21b6);
    color: #ffffff;
    border-color: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 16px 32px rgba(36, 87, 214, 0.25), 0 0 32px rgba(34, 211, 238, 0.22);
}

.stDownloadButton > button {
    background: #ffffff;
    color: var(--primary-dark);
    border-color: #b9c7dd;
}

.stDownloadButton > button:hover {
    background: var(--primary-soft);
    color: var(--primary-dark);
    border-color: var(--primary);
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 8px;
    box-shadow: 0 10px 28px rgba(16, 24, 40, 0.05), 0 0 24px rgba(34, 211, 238, 0.08);
    overflow: hidden;
    animation: panel-rise 560ms ease-out both;
}

div[data-testid="stAlert"] {
    border-radius: 8px;
}

[data-testid="stCheckbox"] {
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.94));
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.45rem 0 0.9rem;
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

[data-testid="stCheckbox"]:hover {
    border-color: rgba(34, 211, 238, 0.55);
    background: #fbfdff;
    transform: translateX(3px);
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.08);
}

[data-testid="stCheckbox"] label {
    color: var(--ink);
    font-weight: 700;
}

.rec-card {
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94)),
        radial-gradient(circle at 94% 18%, rgba(34, 211, 238, 0.12), transparent 30%);
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-left: 5px solid var(--primary);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    margin: 0.75rem 0 0.45rem;
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.04);
    transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    animation: panel-rise 520ms ease-out both;
}

.rec-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 34px rgba(16, 24, 40, 0.12), 0 0 24px rgba(34, 211, 238, 0.12);
}

.rec-card.high { border-left-color: var(--red); }
.rec-card.high:hover { box-shadow: 0 18px 34px rgba(16, 24, 40, 0.12), 0 0 28px rgba(194, 65, 56, 0.18); }
.rec-card.medium { border-left-color: var(--amber); }
.rec-card.medium:hover { box-shadow: 0 18px 34px rgba(16, 24, 40, 0.12), 0 0 28px rgba(183, 121, 31, 0.2); }
.rec-card.low { border-left-color: var(--teal); }
.rec-card.low:hover { box-shadow: 0 18px 34px rgba(16, 24, 40, 0.12), 0 0 28px rgba(15, 143, 131, 0.2); }

.rec-title {
    margin: 0;
    color: var(--ink);
    font-size: 1rem;
    font-weight: 800;
}

.rec-desc {
    margin: 0.35rem 0 0;
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.55;
}

.comparison-panel {
    border: 1px solid rgba(34, 211, 238, 0.2);
    border-radius: 8px;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.94));
    padding: 1rem;
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.04);
    animation: panel-rise 540ms ease-out both;
    position: relative;
    overflow: hidden;
}

.panel-title {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    margin: 0 0 0.85rem;
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.empty-state {
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.95)),
        radial-gradient(circle at 90% 12%, rgba(34, 211, 238, 0.18), transparent 34%);
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 8px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    animation: panel-rise 640ms ease-out both;
}

.empty-state:before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, transparent 0%, rgba(34, 211, 238, 0.08) 50%, transparent 100%);
    transform: translateX(-100%);
    animation: glass-scan 6s ease-in-out infinite;
    pointer-events: none;
}

.empty-state h3 {
    margin: 0;
    color: var(--ink);
    font-size: 1.35rem;
}

.empty-state p {
    margin: 0.65rem 0 1.2rem;
    color: var(--muted);
    line-height: 1.6;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.75rem;
}

.feature-item {
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 8px;
    padding: 0.9rem;
    background: linear-gradient(145deg, #ffffff, #eef6ff);
    color: var(--ink);
    font-size: 0.86rem;
    font-weight: 800;
    transition: transform 160ms ease, border-color 160ms ease, color 160ms ease;
}

.feature-item:hover {
    transform: translateY(-3px);
    border-color: rgba(34, 211, 238, 0.55);
    color: var(--primary-dark);
}

@keyframes panel-rise {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes energy-sweep {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes orbit-pulse {
    0%, 100% {
        transform: translate(0, 0) scale(1);
        opacity: 0.75;
    }
    50% {
        transform: translate(-16px, -10px) scale(1.08);
        opacity: 1;
    }
}

@keyframes step-glow {
    0%, 100% { box-shadow: 0 0 0 rgba(34, 211, 238, 0); }
    50% { box-shadow: 0 0 22px rgba(34, 211, 238, 0.28); }
}

@keyframes line-scan {
    0% { left: -30%; opacity: 0; }
    20% { opacity: 1; }
    100% { left: 100%; opacity: 0; }
}

@keyframes neon-flow {
    0%, 100% { background-position: 0% 50%; opacity: 0.78; }
    50% { background-position: 100% 50%; opacity: 1; }
}

@keyframes glass-scan {
    0%, 45% { transform: translateX(-100%); }
    75%, 100% { transform: translateX(100%); }
}

@media (prefers-reduced-motion: reduce) {
    *, *:before, *:after {
        animation-duration: 1ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 1ms !important;
    }
}

@media (max-width: 760px) {
    .block-container { padding: 1rem 1rem 3rem; }
    .hero { padding: 1.5rem; }
    .feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== DSR DASHBOARD VISUAL SYSTEM APPLIED TO DATAFORGE ===== */
.block-container {
    padding-top: 1.5rem !important;
    max-width: 1180px !important;
}

header { visibility: hidden; }
footer { visibility: hidden; }

/* ===== ANIMATED BACKGROUND ===== */
.stApp {
    background: linear-gradient(-45deg, #0f0f0f, #141414, #101820, #0d1117) !important;
    background-size: 400% 400% !important;
    animation: gradientMove 18s ease infinite !important;
    color: white !important;
}

@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== GLOBAL TEXT ===== */
.hint,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: rgba(255, 255, 255, 0.78) !important;
}

/* ===== KPI / PANEL ANIMATIONS FROM DSR ===== */
@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(0,255,255,0.2); }
    50% { box-shadow: 0 0 25px rgba(0,255,255,0.4); }
    100% { box-shadow: 0 0 15px rgba(0,255,255,0.2); }
}

@keyframes textFlow {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

/* ===== HERO AS PREMIUM GLASS CARD ===== */
.hero {
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.15) !important;
    animation: fadeSlideUp 0.8s ease both, pulseGlow 4s infinite ease-in-out !important;
    transition: transform 0.4s ease, box-shadow 0.4s ease !important;
}

.hero:hover {
    transform: translateY(-8px) scale(1.01) !important;
    box-shadow: 0 0 40px rgba(0,255,255,0.7),
                0 0 80px rgba(0,255,255,0.25) !important;
}

.hero:before {
    content: "" !important;
    position: absolute !important;
    top: 0 !important;
    left: -80% !important;
    width: 60% !important;
    height: 100% !important;
    background: linear-gradient(120deg, rgba(255,255,255,0.05), rgba(255,255,255,0.35), rgba(255,255,255,0.05)) !important;
    transform: skewX(-25deg) !important;
    transition: 0.8s !important;
    z-index: 1 !important;
    opacity: 1 !important;
    animation: none !important;
}

.hero:hover:before { left: 130% !important; }

.hero:after {
    border-color: rgba(0,255,255,0.18) !important;
    box-shadow: 0 0 60px rgba(0,255,255,0.12) !important;
}

.hero h1 {
    background: linear-gradient(90deg, #00ffff, #00ff99, #00ccff, #00ffff) !important;
    background-size: 200% auto !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    animation: textFlow 4s linear infinite !important;
    text-shadow: none !important;
}

.eyebrow {
    color: #cfcfcf !important;
}

.tag {
    background: rgba(31,31,31,0.72) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.08) !important;
}

.tag:hover {
    transform: translateY(-4px) scale(1.03) !important;
    border-color: rgba(0,255,255,0.65) !important;
    box-shadow: 0 0 28px rgba(0,255,255,0.38) !important;
}

/* ===== SECTION HEADERS ===== */
.section-head {
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.15) !important;
    animation: fadeSlideUp 0.7s ease both, pulseGlow 4s infinite ease-in-out !important;
    transition: transform 0.4s ease, box-shadow 0.4s ease !important;
}

.section-head:hover {
    transform: translateY(-6px) scale(1.01) !important;
    box-shadow: 0 0 40px rgba(0,255,255,0.55),
                0 0 80px rgba(0,255,255,0.2) !important;
}

.section-head:before {
    background: linear-gradient(120deg, rgba(255,255,255,0.05), rgba(255,255,255,0.35), rgba(255,255,255,0.05)) !important;
    transform: skewX(-25deg) translateX(-150%) !important;
    animation: headerShine 5s ease-in-out infinite !important;
}

@keyframes headerShine {
    0%, 45% { transform: skewX(-25deg) translateX(-150%); }
    70%, 100% { transform: skewX(-25deg) translateX(260%); }
}

.section-head:after {
    background: linear-gradient(90deg, #00ffff, #00ff99, #00ccff) !important;
    box-shadow: 0 0 22px rgba(0,255,255,0.65) !important;
}

.section-head h2 {
    color: #ffffff !important;
    text-shadow: 0 0 18px rgba(0,255,255,0.32) !important;
}

.step {
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 0 24px rgba(0,255,255,0.35) !important;
}

.issue-count {
    background: rgba(0,255,255,0.10) !important;
    border: 1px solid rgba(0,255,255,0.35) !important;
    color: #00ffff !important;
}

/* ===== STREAMLIT METRICS AS DSR KPI CARDS ===== */
[data-testid="metric-container"] {
    position: relative !important;
    display: block !important;
    width: 100% !important;
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(18px) !important;
    padding: 20px !important;
    border-radius: 18px !important;
    text-align: center !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    overflow: hidden !important;
    margin-bottom: 10px !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.15) !important;
    transition: transform 0.4s ease, box-shadow 0.4s ease !important;
    will-change: transform !important;
    animation: fadeSlideUp 0.7s ease both, pulseGlow 4s infinite ease-in-out !important;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-12px) scale(1.03) !important;
    box-shadow: 0 0 40px rgba(0,255,255,0.7),
                0 0 80px rgba(0,255,255,0.25) !important;
}

[data-testid="metric-container"]::before {
    content: "" !important;
    position: absolute !important;
    top: 0 !important;
    left: -80% !important;
    width: 60% !important;
    height: 100% !important;
    background: linear-gradient(120deg, rgba(255,255,255,0.05), rgba(255,255,255,0.35), rgba(255,255,255,0.05)) !important;
    transform: skewX(-25deg) !important;
    transition: 0.8s !important;
}

[data-testid="metric-container"]:hover::before { left: 130% !important; }

[data-testid="stMetricLabel"] {
    color: #cfcfcf !important;
    font-size: 10px !important;
}

[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #00ffff, #00ff99, #00ccff) !important;
    background-size: 200% auto !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    animation: textFlow 4s linear infinite !important;
}

/* ===== GLASS INPUTS, UPLOADERS, TABLES, ALERTS ===== */
[data-testid="stFileUploader"],
[data-testid="stDataFrame"],
div[data-testid="stAlert"],
[data-testid="stCheckbox"],
.rec-card,
.comparison-panel,
.empty-state,
.feature-item {
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 18px !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.15) !important;
    transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease !important;
    animation: fadeSlideUp 0.7s ease both !important;
}

[data-testid="stFileUploader"]:hover,
[data-testid="stCheckbox"]:hover,
.rec-card:hover,
.comparison-panel:hover,
.empty-state:hover,
.feature-item:hover {
    transform: translateY(-8px) scale(1.02) !important;
    border-color: rgba(0,255,255,0.45) !important;
    box-shadow: 0 0 40px rgba(0,255,255,0.55),
                0 0 80px rgba(0,255,255,0.18) !important;
}

[data-testid="stFileUploadDropzone"] {
    background: rgba(31,31,31,0.55) !important;
    border-radius: 16px !important;
}

[data-testid="stFileUploadDropzone"] * {
    color: #ffffff !important;
}

[data-testid="stDataFrame"] {
    padding: 16px !important;
}

[data-testid="stDataFrame"] * {
    color: inherit;
}

div[data-testid="stAlert"] {
    color: #ffffff !important;
}

[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label * {
    color: #ffffff !important;
}

/* ===== RECOMMENDATION CARDS ===== */
.rec-card {
    position: relative !important;
    overflow: hidden !important;
}

.rec-card:before,
.comparison-panel:before,
.empty-state:before,
.feature-item:before {
    content: "" !important;
    position: absolute !important;
    top: 0 !important;
    left: -80% !important;
    width: 60% !important;
    height: 100% !important;
    background: linear-gradient(120deg, rgba(255,255,255,0.05), rgba(255,255,255,0.30), rgba(255,255,255,0.05)) !important;
    transform: skewX(-25deg) !important;
    transition: 0.8s !important;
    pointer-events: none !important;
    opacity: 0 !important;
}

.rec-card:hover:before,
.comparison-panel:hover:before,
.empty-state:hover:before,
.feature-item:hover:before {
    left: 130% !important;
    opacity: 1 !important;
}

.rec-title,
.empty-state h3,
.panel-title {
    color: #ffffff !important;
}

.rec-desc,
.empty-state p {
    color: #cfcfcf !important;
}

.rec-card.high { border-left: 5px solid #ff4d6d !important; }
.rec-card.medium { border-left: 5px solid #00ffff !important; }
.rec-card.low { border-left: 5px solid #00ff99 !important; }

/* ===== BUTTONS ===== */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 25px rgba(0,114,255,0.4), 0 0 18px rgba(0,255,255,0.18) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-6px) scale(1.02) !important;
    color: white !important;
    box-shadow: 0 0 40px rgba(0,255,255,0.7),
                0 0 80px rgba(0,114,255,0.32) !important;
}

/* ===== EMPTY STATE FEATURES ===== */
.feature-item {
    color: #ffffff !important;
    position: relative !important;
    overflow: hidden !important;
    text-align: center !important;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 760px) {
    .section-head {
        align-items: flex-start !important;
        gap: 0.7rem !important;
    }
    .section-head:after {
        min-width: 28px !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== DATA ENGINEERING WORKSPACE STRUCTURE ===== */
[data-testid="stTabs"] {
    margin-top: 1.25rem;
}

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.65rem;
    border-bottom: 1px solid rgba(0,255,255,0.14);
}

[data-testid="stTabs"] [role="tab"] {
    min-height: 44px;
    padding: 0 1rem;
    border-radius: 14px 14px 0 0;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.72);
    font-weight: 800;
    transition: all 0.25s ease;
}

[data-testid="stTabs"] [role="tab"]:hover {
    color: #ffffff;
    border-color: rgba(0,255,255,0.45);
    box-shadow: 0 0 24px rgba(0,255,255,0.18);
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #00ffff !important;
    background: linear-gradient(145deg, rgba(0,255,255,0.14), rgba(0,114,255,0.10)) !important;
    border-color: rgba(0,255,255,0.45) !important;
}

.ops-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 0.25rem;
}

.ops-card {
    position: relative;
    overflow: hidden;
    min-height: 92px;
    padding: 1rem;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 0 15px rgba(0,255,255,0.12);
    backdrop-filter: blur(18px);
}

.ops-card:before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.12), transparent);
    transform: translateX(-100%) skewX(-25deg);
    animation: headerShine 6s ease-in-out infinite;
}

.ops-k {
    color: #cfcfcf !important;
    font-size: 0.72rem !important;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.55rem !important;
}

.ops-v {
    color: #ffffff !important;
    font-size: 1.4rem !important;
    font-weight: 900;
    margin: 0 !important;
    background: linear-gradient(90deg, #00ffff, #00ff99, #00ccff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textFlow 4s linear infinite;
}

.terminal-note {
    border-left: 3px solid #00ffff;
    background: rgba(0,255,255,0.08);
    color: rgba(255,255,255,0.82);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin: 0.75rem 0 1rem;
    font-family: Consolas, "Courier New", monospace;
    font-size: 0.86rem;
}

.table-shell {
    position: relative;
    overflow: auto;
    max-height: 430px;
    margin: 0.8rem 0 1.2rem;
    padding: 0;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 0 15px rgba(0,255,255,0.15);
    backdrop-filter: blur(18px);
    scrollbar-color: rgba(0,255,255,0.55) rgba(255,255,255,0.08);
}

.table-shell::-webkit-scrollbar {
    height: 10px;
    width: 10px;
}

.table-shell::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
}

.table-shell::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #00ffff, #0072ff);
    border-radius: 999px;
}

.dataforge-table {
    width: 100%;
    min-width: max-content;
    border-collapse: collapse;
    color: #f8fbff;
    font-size: 0.82rem;
    line-height: 1.3;
    margin: 0;
}

.dataforge-table thead th {
    position: static;
    background: linear-gradient(135deg, #0f5878, #0c3f69);
    color: #ffffff;
    padding: 0.82rem 0.9rem;
    text-align: left;
    border-bottom: 1px solid rgba(0,255,255,0.3);
    border-right: 1px solid rgba(255,255,255,0.08);
    white-space: nowrap;
    text-shadow: 0 0 12px rgba(0,255,255,0.28);
}

.dataforge-table thead th:first-child {
    border-top-left-radius: 16px;
}

.dataforge-table thead th:last-child {
    border-top-right-radius: 16px;
}

.dataforge-table tbody td,
.dataforge-table tbody th {
    padding: 0.72rem 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    border-right: 1px solid rgba(255,255,255,0.045);
    color: rgba(255,255,255,0.86);
    background: rgba(7,17,31,0.42);
    white-space: nowrap;
}

.dataforge-table tbody tr:nth-child(even) td,
.dataforge-table tbody tr:nth-child(even) th {
    background: rgba(255,255,255,0.045);
}

.dataforge-table tbody tr:hover td,
.dataforge-table tbody tr:hover th {
    background: rgba(0,255,255,0.12);
    color: #ffffff;
}

.uploaded-file-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 0.85rem 0 0;
    padding: 0.9rem 1rem;
    border-radius: 16px;
    background: linear-gradient(145deg, rgba(0,255,255,0.10), rgba(255,255,255,0.035));
    border: 1px solid rgba(0,255,255,0.24);
    box-shadow: 0 0 18px rgba(0,255,255,0.14);
}

.uploaded-file-name {
    color: #ffffff !important;
    font-weight: 900;
    margin: 0 !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.uploaded-file-meta {
    color: #00ffff !important;
    font-size: 0.8rem;
    font-weight: 800;
    margin: 0 !important;
    white-space: nowrap;
}

.uploader-has-file [data-testid="stFileUploadDropzone"] {
    display: block !important;
}

.uploader-has-file [data-testid="stFileUploader"] {
    padding: 0.55rem !important;
}

/* ===== POLISHED FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background: linear-gradient(145deg, rgba(255,255,255,0.075), rgba(255,255,255,0.025)) !important;
    border: 1px solid rgba(0,255,255,0.22) !important;
    box-shadow: 0 0 24px rgba(0,255,255,0.14), inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

[data-testid="stFileUploadDropzone"] {
    background: linear-gradient(145deg, rgba(12,22,35,0.96), rgba(8,15,25,0.92)) !important;
    border: 1px dashed rgba(0,255,255,0.38) !important;
    box-shadow: inset 0 0 22px rgba(0,255,255,0.08) !important;
}

[data-testid="stFileUploadDropzone"] * {
    color: rgba(255,255,255,0.86) !important;
}

[data-testid="stFileUploadDropzone"] small,
[data-testid="stFileUploadDropzone"] span {
    color: rgba(207,207,207,0.86) !important;
}

[data-testid="stFileUploadDropzone"] button {
    min-width: 132px !important;
    background: linear-gradient(135deg, #ff8a00, #ff3d81) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 22px rgba(255,61,129,0.48), 0 8px 24px rgba(255,138,0,0.26) !important;
    font-weight: 900 !important;
}

[data-testid="stFileUploadDropzone"] button:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 0 36px rgba(255,61,129,0.74), 0 12px 32px rgba(255,138,0,0.42) !important;
}

[data-testid="stFileUploadDropzone"] button:disabled,
[data-testid="stFileUploadDropzone"] button[disabled] {
    background: linear-gradient(135deg, #ff8a00, #ff3d81) !important;
    color: #ffffff !important;
    opacity: 1 !important;
    border-color: rgba(255,255,255,0.24) !important;
    box-shadow: 0 0 24px rgba(255,61,129,0.45), 0 8px 24px rgba(255,138,0,0.24) !important;
}

[data-testid="stFileUploadDropzone"] [data-testid="baseButton-secondary"],
[data-testid="stFileUploadDropzone"] [data-testid="stBaseButton-secondary"],
[data-testid="stFileUploadDropzone"] button[kind="secondary"],
[data-testid="stFileUploadDropzone"] button {
    background: linear-gradient(135deg, #ff8a00, #ff3d81) !important;
    background-color: #ff3d81 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    opacity: 1 !important;
    filter: none !important;
    box-shadow: 0 0 26px rgba(255,61,129,0.58), 0 10px 28px rgba(255,138,0,0.32) !important;
}

[data-testid="stFileUploadDropzone"] [data-testid="baseButton-secondary"]:hover,
[data-testid="stFileUploadDropzone"] [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stFileUploadDropzone"] button[kind="secondary"]:hover,
[data-testid="stFileUploadDropzone"] button:hover {
    background: linear-gradient(135deg, #ffb000, #ff2f92) !important;
    background-color: #ff2f92 !important;
    box-shadow: 0 0 40px rgba(255,47,146,0.82), 0 12px 34px rgba(255,176,0,0.42) !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    background: rgba(8,15,25,0.72) !important;
    border: 1px solid rgba(0,255,255,0.16) !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
    color: rgba(255,255,255,0.9) !important;
}

.compare-title {
    margin: 0 0 1rem;
    color: #ffffff !important;
    font-size: 0.82rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.compare-metric {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 0;
    border-top: 1px solid rgba(255,255,255,0.10);
}

.compare-label {
    color: #cfcfcf !important;
    font-size: 0.82rem;
    font-weight: 800;
}

.compare-value {
    color: #00ffff !important;
    font-size: 1.45rem;
    font-weight: 900;
    line-height: 1;
    text-shadow: 0 0 18px rgba(0,255,255,0.35);
}

.compare-delta {
    color: #00ff99 !important;
    font-size: 0.78rem;
    font-weight: 800;
    margin-left: 0.35rem;
}

.issue-chip-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin: 0.75rem 0 1.2rem;
    padding: 0.9rem;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(255,255,255,0.065), rgba(255,255,255,0.02));
    border: 1px solid rgba(0,255,255,0.16);
    box-shadow: 0 0 18px rgba(0,255,255,0.10);
}

.issue-chip {
    max-width: 100%;
    padding: 0.48rem 0.7rem;
    border-radius: 999px;
    background: rgba(255,176,0,0.12);
    border: 1px solid rgba(255,176,0,0.28);
    color: rgba(255,255,255,0.9);
    font-size: 0.74rem;
    font-weight: 800;
    line-height: 1.25;
    box-shadow: 0 0 14px rgba(255,176,0,0.08);
}

.issue-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 0.9rem 0 1.2rem;
    position: relative;
    overflow: visible;
    min-height: 150px;
}

.issue-flip {
    min-height: 150px;
    perspective: 1000px;
    cursor: default;
    position: relative;
    z-index: 1;
}

.issue-flip-inner {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    min-height: 150px;
    transform-style: preserve-3d;
    transition: transform 0.7s cubic-bezier(0.4, 0.2, 0.2, 1), width 0.28s ease, min-height 0.28s ease, left 0.28s ease, right 0.28s ease;
}

.issue-flip:hover .issue-flip-inner {
    transform: rotateY(180deg);
    width: min(620px, 92vw);
    min-height: 330px;
    z-index: 200;
}

.issue-flip:nth-child(3):hover .issue-flip-inner,
.issue-flip:nth-child(4):hover .issue-flip-inner {
    left: auto;
    right: 0;
}

.issue-flip:nth-child(2):hover .issue-flip-inner {
    left: 50%;
    transform: translateX(-28%) rotateY(180deg);
}

.issue-face {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-radius: 18px;
    padding: 1rem;
    backface-visibility: hidden;
    overflow: hidden;
    background: linear-gradient(145deg, #1b232d, #111923);
    border: 1px solid rgba(0,255,255,0.20);
    box-shadow: 0 0 18px rgba(0,255,255,0.13);
    transition: box-shadow 0.28s ease, min-height 0.28s ease;
    min-height: 150px;
}

.issue-flip:hover {
    z-index: 300;
}

.issue-flip:hover .issue-face {
    background: linear-gradient(145deg, #202a34, #101820);
    box-shadow: 0 0 44px rgba(0,255,255,0.32), 0 18px 70px rgba(0,0,0,0.72);
    min-height: 330px;
}

.issue-face:before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.12), transparent);
    transform: translateX(-110%) skewX(-25deg);
    transition: transform 0.7s ease;
}

.issue-flip:hover .issue-face:before {
    transform: translateX(120%) skewX(-25deg);
}

.issue-back {
    transform: rotateY(180deg);
    justify-content: flex-start;
}

.issue-kpi-label {
    margin: 0 0 0.55rem !important;
    color: #cfcfcf !important;
    font-size: 0.74rem;
    font-weight: 900;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

.issue-kpi-value {
    margin: 0 !important;
    color: #00ffff !important;
    font-size: 2.25rem;
    font-weight: 950;
    line-height: 1;
    text-shadow: 0 0 24px rgba(0,255,255,0.42);
}

.issue-kpi-help {
    margin: 0.65rem 0 0 !important;
    color: rgba(255,255,255,0.58) !important;
    font-size: 0.72rem;
    font-weight: 800;
}

.issue-list {
    margin: 0.65rem 0 0;
    padding: 0;
    list-style: none;
    max-height: 250px;
    overflow: auto;
}

.issue-list li {
    color: rgba(255,255,255,0.86) !important;
    font-size: 0.86rem;
    font-weight: 750;
    line-height: 1.45;
    padding: 0.48rem 0;
    border-top: 1px solid rgba(255,255,255,0.08);
}

.issue-list-empty {
    color: rgba(255,255,255,0.52) !important;
    font-size: 0.78rem;
    font-weight: 800;
}

.issue-missing .issue-face { border-color: rgba(255,176,0,0.32); box-shadow: 0 0 18px rgba(255,176,0,0.14); }
.issue-missing .issue-kpi-value { color: #ffb000 !important; text-shadow: 0 0 22px rgba(255,176,0,0.36); }
.issue-duplicate .issue-face { border-color: rgba(255,77,109,0.34); box-shadow: 0 0 18px rgba(255,77,109,0.16); }
.issue-duplicate .issue-kpi-value { color: #ff4d6d !important; text-shadow: 0 0 22px rgba(255,77,109,0.36); }
.issue-datatype .issue-face { border-color: rgba(0,255,255,0.32); }
.issue-outlier .issue-face { border-color: rgba(0,255,153,0.32); box-shadow: 0 0 18px rgba(0,255,153,0.13); }
.issue-outlier .issue-kpi-value { color: #00ff99 !important; text-shadow: 0 0 22px rgba(0,255,153,0.32); }

@media (max-width: 1000px) {
    .issue-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 620px) {
    .issue-kpi-grid { grid-template-columns: 1fr; }
}

@media (max-width: 900px) {
    .ops-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
""", unsafe_allow_html=True)


def section_header(step, title, badge=None, accent=None):
    style = f' style="background:{accent}; color:#ffffff;"' if accent else ""
    badge_html = f'<span class="issue-count">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="section-head">
        <span class="step"{style}>{step}</span>
        <h2>{title}</h2>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)


def render_table(data, label):
    table_df = pd.DataFrame(data).copy()
    html = table_df.to_html(classes="dataforge-table", border=0, index=False, escape=True)
    st.markdown(f"""
    <div class="table-shell" aria-label="{label}">
        {html}
    </div>
    """, unsafe_allow_html=True)


def format_file_size(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def ops_cards(items):
    cards = "".join(
        f"""
        <div class="ops-card">
            <p class="ops-k">{label}</p>
            <p class="ops-v">{value}</p>
        </div>
        """
        for label, value in items
    )
    st.markdown(f'<div class="ops-grid">{cards}</div>', unsafe_allow_html=True)


def render_issue_chips(items):
    chips = "".join(f'<span class="issue-chip">{issue}</span>' for issue in items)
    st.markdown(f'<div class="issue-chip-wrap">{chips}</div>', unsafe_allow_html=True)


def render_issue_kpis(items):
    groups = {
        "Missing Values": {
            "class": "issue-missing",
            "items": [issue for issue in items if "missing" in issue.lower()]
        },
        "Duplicates": {
            "class": "issue-duplicate",
            "items": [issue for issue in items if "duplicate" in issue.lower()]
        },
        "Data Types": {
            "class": "issue-datatype",
            "items": [issue for issue in items if "datatype" in issue.lower() or "text" in issue.lower()]
        },
        "Outliers": {
            "class": "issue-outlier",
            "items": [issue for issue in items if "outlier" in issue.lower()]
        }
    }
    cards = []
    for label, config in groups.items():
        issue_items = config["items"]
        if issue_items:
            list_items = "".join(f"<li>{html.escape(str(issue))}</li>" for issue in issue_items)
        else:
            list_items = '<li class="issue-list-empty">No issues detected</li>'
        cards.append(
            f'<div class="issue-flip {config["class"]}">'
            f'<div class="issue-flip-inner">'
            f'<div class="issue-face issue-front">'
            f'<p class="issue-kpi-label">{html.escape(label)}</p>'
            f'<p class="issue-kpi-value">{len(issue_items)}</p>'
            f'<p class="issue-kpi-help">Hover for details</p>'
            f'</div>'
            f'<div class="issue-face issue-back">'
            f'<p class="issue-kpi-label">{html.escape(label)} Details</p>'
            f'<ul class="issue-list">{list_items}</ul>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
    st.html(f'<div class="issue-kpi-grid">{"".join(cards)}</div>')


st.markdown("""
<div class="hero">
    <div class="eyebrow">Data Engineering Platform</div>
    <h1>DataForge</h1>
    <p>Upload a CSV, inspect quality issues, generate recommended cleaning actions, and export a cleaner dataset without changing your backend workflow.</p>
    <div class="hero-tags">
        <span class="tag">FastAPI Engine</span>
        <span class="tag">Smart Detection</span>
        <span class="tag">Column Profiling</span>
        <span class="tag">Audit Trail</span>
        <span class="tag">One-Click Cleaning</span>
    </div>
</div>
""", unsafe_allow_html=True)


# SESSION STATE
if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "selected_actions" not in st.session_state:
    st.session_state.selected_actions = []


# STEP 1 - UPLOAD
section_header("01", "Upload Dataset")
st.markdown('<p class="hint">Choose a CSV file to start analysis. Your existing in-memory dataset store and backend connection are unchanged.</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    st.markdown(f"""
    <div class="uploaded-file-card">
        <p class="uploaded-file-name">{uploaded_file.name}</p>
        <p class="uploaded-file-meta">{format_file_size(uploaded_file.size)} CSV staged</p>
    </div>
    """, unsafe_allow_html=True)


dataset_id = None
df = None
issues = []


if uploaded_file is not None:

    dataset_id = str(uuid.uuid4())
    df = pd.read_csv(uploaded_file)
    datasets[dataset_id] = {"df": df, "filename": uploaded_file.name}

    # STEP 2: SUMMARY
    section_header("02", "Dataset Overview")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Rows", f"{df.shape[0]:,}")
    with c2:
        st.metric("Total Columns", f"{df.shape[1]}")
    with c3:
        st.metric("Total Cells", f"{df.shape[0] * df.shape[1]:,}")

    st.markdown('<p class="hint">Previewing the first 10 rows from the uploaded file.</p>', unsafe_allow_html=True)
    render_table(df.head(10), "Uploaded data preview")

    # STEP 3: ISSUES
    issues = analyze_dataframe(df)
    datasets[dataset_id]["issues"] = issues

    section_header("03", "Quality Analysis", f"{len(issues)} ISSUES" if issues else None)

    if not issues:
        st.success("Dataset is clean. No quality issues were detected.")
    else:
        st.markdown(f'<p class="hint">{len(issues)} issue{"s" if len(issues)>1 else ""} detected. Review them before generating cleaning recommendations.</p>', unsafe_allow_html=True)
        render_issue_kpis(issues)

    # STEP 4: PROFILING
    section_header("04", "Column Profiling")

    profile_df = generate_profile(df)
    render_table(profile_df, "Column profile")


# STEP 5 - RECOMMENDATIONS
section_header("05", "Smart Recommendations")

job_id = st.session_state.job_id

if uploaded_file is not None and st.button("Analyse & Recommend", type="primary"):

    if dataset_id is None:
        st.error("No dataset loaded.")
        st.stop()

    st.session_state.job_id = str(uuid.uuid4())
    job_id = st.session_state.job_id
    jobs[job_id] = {"dataset_id": dataset_id, "status": "running"}

    try:
        with st.spinner("Contacting analysis engine..."):
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json={"dataset_id": dataset_id, "issues": issues}
            )
            result = response.json()
            jobs[job_id]["status"] = "done"
            jobs[job_id]["recommendations"] = result["recommendations"]
        st.success(f"Analysis complete. {result['total_actions']} action(s) recommended.")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        st.error(f"Engine error: {str(e)}")

elif uploaded_file is None:
    st.info("Upload a dataset first to enable analysis.")


# LOAD RECOMMENDATIONS
recommendations = []
job_id = st.session_state.job_id
if job_id and job_id in jobs:
    recommendations = jobs[job_id].get("recommendations", [])

if recommendations:

    section_header("06", "Select Cleaning Actions")

    for rec in recommendations:

        css = {"high": "high", "medium": "medium", "low": "low"}.get(rec["severity"], "low")
        severity_label = {"high": "High impact", "medium": "Medium impact", "low": "Review"}.get(rec["severity"], "Review")

        st.markdown(f"""
        <div class="rec-card {css}">
            <p class="rec-title">{rec['title']} - {severity_label}</p>
            <p class="rec-desc">{rec['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        checked = st.checkbox(
            f"Apply - {rec['title']}",
            key=f"{job_id}_{rec['action']}"
        )
        if checked:
            if rec["action"] not in st.session_state.selected_actions:
                st.session_state.selected_actions.append(rec["action"])
        else:
            if rec["action"] in st.session_state.selected_actions:
                st.session_state.selected_actions.remove(rec["action"])


# EXECUTE CLEANING
if uploaded_file is not None and len(st.session_state.selected_actions) > 0:

    if st.button("Execute Cleaning Pipeline", type="primary"):

        df = datasets[dataset_id]["df"]
        original_rows = len(df)
        original_missing = df.isnull().sum().sum()

        with st.spinner("Executing pipeline..."):
            cleaned_df = clean_dataframe(df, st.session_state.selected_actions)

        new_rows = len(cleaned_df)
        new_missing = cleaned_df.isnull().sum().sum()

        section_header("OK", "Pipeline Complete", accent="linear-gradient(135deg,#11845b,#0f8f83)")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="comparison-panel">
                <p class="compare-title">Before Cleaning</p>
                <div class="compare-metric">
                    <span class="compare-label">Rows</span>
                    <span class="compare-value">{original_rows:,}</span>
                </div>
                <div class="compare-metric">
                    <span class="compare-label">Missing Values</span>
                    <span class="compare-value">{original_missing:,}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="comparison-panel">
                <p class="compare-title">After Cleaning</p>
                <div class="compare-metric">
                    <span class="compare-label">Rows</span>
                    <span>
                        <span class="compare-value">{new_rows:,}</span>
                        <span class="compare-delta">-{original_rows-new_rows:,} removed</span>
                    </span>
                </div>
                <div class="compare-metric">
                    <span class="compare-label">Missing Values</span>
                    <span>
                        <span class="compare-value">{new_missing:,}</span>
                        <span class="compare-delta">-{original_missing-new_missing:,} fixed</span>
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.success(f"{original_rows-new_rows:,} duplicate rows removed. {original_missing-new_missing:,} missing values resolved.")
        render_table(cleaned_df.head(10), "Cleaned data preview")

        csv = cleaned_df.to_csv(index=False)
        st.download_button("Export Clean Dataset", csv, "cleaned_data.csv", "text/csv")

        audit_logs.append({
            "dataset_id": dataset_id,
            "job_id": job_id,
            "actions": st.session_state.selected_actions,
            "original_rows": original_rows,
            "new_rows": new_rows,
            "timestamp": str(datetime.datetime.now())
        })
        st.session_state.selected_actions = []


# AUDIT LOG
section_header("07", "Audit Trail")

if audit_logs:
    render_table(audit_logs, "Audit log")
else:
    st.info("No operations recorded yet. Completed cleaning runs will appear here.")


# EMPTY STATE
if uploaded_file is None:
    st.markdown("""
    <div class="empty-state">
        <h3>Ready for a dataset</h3>
        <p>Once you upload a CSV, DataForge will show the preview, quality findings, column profile, recommended actions, cleaning controls, and audit trail in one focused workflow.</p>
        <div class="feature-grid">
            <div class="feature-item">Auto Detect</div>
            <div class="feature-item">Smart Engine</div>
            <div class="feature-item">Deep Profile</div>
            <div class="feature-item">One-Click Fix</div>
            <div class="feature-item">Audit Trail</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
