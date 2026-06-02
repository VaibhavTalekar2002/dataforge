from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class PipelineResult:
    df: pd.DataFrame
    history: list[dict] = field(default_factory=list)


def clean_dataframe(df: pd.DataFrame, actions: list[str]) -> pd.DataFrame:
    return run_pipeline(df, actions).df


def preview_cleaning(df: pd.DataFrame, actions: list[str], rows: int = 1000) -> PipelineResult:
    return run_pipeline(df.head(rows).copy(), actions)


def run_pipeline(df: pd.DataFrame, actions: list[str]) -> PipelineResult:
    current = df.copy()
    history: list[dict] = []
    for action in actions:
        before = _stats(current)
        current = _apply_action(current, action)
        after = _stats(current)
        history.append(
            {
                "Action": action,
                "Rows Before": before["rows"],
                "Rows After": after["rows"],
                "Missing Before": before["missing"],
                "Missing After": after["missing"],
                "Changed Cells": estimate_changed_cells(df if len(history) == 0 else None, current),
            }
        )
    return PipelineResult(df=current, history=history)


def _apply_action(df: pd.DataFrame, action: str) -> pd.DataFrame:
    result = df.copy()
    if action == "remove_duplicates":
        return result.drop_duplicates()
    if action == "drop_empty_columns":
        return result.dropna(axis=1, how="all")
    if action == "drop_constant_columns":
        constant_cols = [col for col in result.columns if result[col].nunique(dropna=True) <= 1]
        return result.drop(columns=constant_cols)
    if action == "normalize_text":
        for col in result.select_dtypes(include=["object"]).columns:
            result[col] = result[col].map(lambda value: value.strip() if isinstance(value, str) else value)
        return result
    if action == "standardize_case":
        for col in result.select_dtypes(include=["object"]).columns:
            unique_ratio = result[col].nunique(dropna=True) / max(len(result), 1)
            if unique_ratio <= 0.3:
                result[col] = result[col].map(lambda value: value.title() if isinstance(value, str) else value)
        return result
    if action == "fix_dtypes":
        for col in result.columns:
            non_null = result[col].dropna()
            if non_null.empty:
                continue
            numeric = pd.to_numeric(non_null, errors="coerce")
            if numeric.notna().mean() >= 0.85:
                result[col] = pd.to_numeric(result[col], errors="coerce")
        return result
    if action in {"fill_missing", "fill_missing_mean"}:
        for col in result.select_dtypes(include=np.number).columns:
            if result[col].isna().any():
                result[col] = result[col].fillna(result[col].median())
        if action == "fill_missing_mean":
            return result
    if action in {"fill_missing", "fill_missing_mode"}:
        for col in result.columns.difference(result.select_dtypes(include=np.number).columns):
            if result[col].isna().any() and not result[col].mode(dropna=True).empty:
                result[col] = result[col].fillna(result[col].mode(dropna=True).iloc[0])
        return result
    return result


def compare_dataframes(before: pd.DataFrame, after: pd.DataFrame) -> dict:
    return {
        "rows_before": len(before),
        "rows_after": len(after),
        "columns_before": len(before.columns),
        "columns_after": len(after.columns),
        "missing_before": int(before.isna().sum().sum()),
        "missing_after": int(after.isna().sum().sum()),
        "duplicates_before": int(before.duplicated().sum()),
        "duplicates_after": int(after.duplicated().sum()),
    }


def duplicate_preview(df: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    duplicates = df[df.duplicated(keep=False)]
    return duplicates.head(limit)


def estimate_changed_cells(before: pd.DataFrame | None, after: pd.DataFrame) -> int:
    if before is None or before.shape != after.shape:
        return 0
    comparable_before = before.reset_index(drop=True).astype(str)
    comparable_after = after.reset_index(drop=True).astype(str)
    return int((comparable_before != comparable_after).sum().sum())


def _stats(df: pd.DataFrame) -> dict:
    return {"rows": len(df), "missing": int(df.isna().sum().sum())}
