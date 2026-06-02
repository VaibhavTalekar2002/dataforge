from __future__ import annotations

from collections import Counter
from typing import Iterable

import pandas as pd
import streamlit as st

from dataforge.utils.formatting import escape


def topbar(filename: str | None, health: int | None) -> None:
    status = "No dataset" if not filename else f"{filename}"
    score = "Upload CSV" if health is None else f"Health {health}/100"
    st.markdown(
        f"""
<div class="df-topbar">
  <div class="df-brand">
    <div class="df-mark">DF</div>
    <div>
      <h1>DataForge</h1>
      <p>Premium CSV quality and engineering workspace</p>
    </div>
  </div>
  <div class="df-top-actions">
    <span class="df-chip">{escape(status)}</span>
    <span class="df-chip good">{escape(score)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(score: int | None = None, rows: int | None = None, columns: int | None = None) -> None:
    score_value = 0 if score is None else score
    rows_label = "Awaiting dataset" if rows is None else f"{rows:,} rows"
    columns_label = "Schema pending" if columns is None else f"{columns:,} columns"
    st.markdown(
        f"""
<div class="df-hero">
  <div class="df-hero-grid">
    <div>
      <p class="df-eyebrow">Command Center</p>
      <h2>CSV intelligence, cleaned into focus.</h2>
      <p>Profile schema, score quality, detect issues, run cleaning pipelines, and export engineering reports from one offline analytics workspace.</p>
      <div class="df-chip-row">
        <span class="df-chip">Offline first</span>
        <span class="df-chip">FastAPI engine</span>
        <span class="df-chip">Pipeline audit</span>
        <span class="df-chip">Visual insights</span>
      </div>
    </div>
    <div class="df-hero-panel">
      <div class="df-health" style="--score:{score_value}">
        <div class="df-health-inner">
          <div>
            <div class="df-health-score">{score_value}</div>
            <div class="df-health-label">Quality</div>
          </div>
        </div>
      </div>
      <div class="df-chip-row">
        <span class="df-chip">{escape(rows_label)}</span>
        <span class="df-chip">{escape(columns_label)}</span>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def section(title: str, meta: str | None = None, description: str | None = None) -> None:
    desc = f"<p>{escape(description)}</p>" if description else ""
    st.markdown(
        f"""
<div class="df-section">
  <div>
    <h2>{escape(title)}</h2>
    {desc}
  </div>
  <span>{escape(meta or "")}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def panel_start() -> None:
    st.markdown('<div class="df-panel">', unsafe_allow_html=True)


def panel_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def table(df: pd.DataFrame | list[dict], *, height: int = 340) -> None:
    data = pd.DataFrame(df)
    st.dataframe(data, use_container_width=True, height=height, hide_index=True)


def metric_card(label: str, value: str | int, delta: str | None = None, icon: str = "") -> None:
    st.markdown(
        f"""
<div class="df-metric">
  <div class="df-metric-top">
    <p class="df-metric-label">{escape(label)}</p>
    <span class="df-metric-icon">{escape(icon)}</span>
  </div>
  <p class="df-metric-value">{escape(value)}</p>
  <p class="df-metric-delta">{escape(delta or "")}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def score_badge(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Healthy"
    if score >= 50:
        return "Needs work"
    return "High risk"


def health_ring(score: int, label: str = "Dataset health") -> None:
    st.markdown(
        f"""
<div class="df-health" style="--score:{score}">
  <div class="df-health-inner">
    <div>
      <div class="df-health-score">{score}</div>
      <div class="df-health-label">{escape(label)}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def issue_summary(issues: list[dict]) -> None:
    counts = Counter(issue.get("severity", "low").title() for issue in issues)
    cols = st.columns(4)
    values = [
        ("Findings", len(issues), "Total detected", ""),
        ("High", counts.get("High", 0), "Immediate review", ""),
        ("Medium", counts.get("Medium", 0), "Pipeline candidates", ""),
        ("Low", counts.get("Low", 0), "Informational", ""),
    ]
    for col, (label, value, delta, icon) in zip(cols, values):
        with col:
            metric_card(label, value, delta, icon)


def recommendation_card(rec: dict) -> None:
    severity = rec.get("severity", "low")
    auto = "Auto applicable" if rec.get("auto_applicable", True) else "Review only"
    st.markdown(
        f"""
<div class="df-card df-rec {escape(severity)}">
  <p class="df-rec-title">{escape(rec.get("title", "Recommendation"))}</p>
  <p class="df-rec-desc">{escape(rec.get("description", ""))}</p>
  <div class="df-chip-row">
    <span class="df-chip">{escape(severity.title())} impact</span>
    <span class="df-chip">{escape(auto)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def timeline(items: list[dict]) -> None:
    if not items:
        empty_state("No activity yet", "Cleaning runs and processing milestones will appear here.")
        return
    rows = []
    for idx, item in enumerate(items, start=1):
        title = item.get("Action") or item.get("Actions") or item.get("File") or "Activity"
        meta = " · ".join(str(value) for key, value in item.items() if key != "Action" and value not in ("", None))
        rows.append(
            f"""
<div class="df-step">
  <div class="df-step-dot">{idx}</div>
  <div>
    <p class="df-step-title">{escape(title)}</p>
    <p class="df-step-meta">{escape(meta)}</p>
  </div>
  <span class="df-chip">Complete</span>
</div>
"""
        )
    st.markdown(f'<div class="df-timeline">{"".join(rows)}</div>', unsafe_allow_html=True)


def empty_state(title: str, message: str, items: Iterable[str] = ()) -> None:
    badges = "".join(f'<span class="df-badge">{escape(item)}</span>' for item in items)
    st.markdown(
        f"""
<div class="df-empty">
  <h3>{escape(title)}</h3>
  <p class="df-muted">{escape(message)}</p>
  <div class="df-badges">{badges}</div>
</div>
""",
        unsafe_allow_html=True,
    )
