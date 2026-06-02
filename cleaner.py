import pandas as pd


# ─────────────────────────────
# ANALYZE DATAFRAME
# ─────────────────────────────
def analyze_dataframe(df):

    issues = []

    # ─────────────────────────────
    # CHECK 1: Missing Values
    # ─────────────────────────────
    missing = df.isnull().sum()

    for col, count in missing.items():

        if count > 0:

            pct = round((count / len(df)) * 100, 1)

            issues.append(
                f"Column '{col}' has {count} missing values ({pct}% of rows)"
            )

    # ─────────────────────────────
    # CHECK 2: Duplicate Rows
    # ─────────────────────────────
    dupes = df.duplicated().sum()

    if dupes > 0:

        issues.append(
            f"{dupes} duplicate rows found in the dataset"
        )

    # ─────────────────────────────
    # CHECK 3: Data Type Issues
    # ─────────────────────────────
    expected_numeric_cols = [
        "age",
        "salary",
        "performance_score"
    ]

    for col in expected_numeric_cols:

        if col in df.columns:

            converted = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            invalid_values = (
                converted.isna().sum()
                - df[col].isna().sum()
            )

            if invalid_values > 0:

                issues.append(
                    f"Column '{col}' has "
                    f"{invalid_values} datatype issues "
                    f"(text inside numeric column)"
                )

    # ─────────────────────────────
    # CHECK 4: Outliers
    # ─────────────────────────────
    for col in expected_numeric_cols:

        if col in df.columns:

            numeric_col = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            Q1 = numeric_col.quantile(0.25)
            Q3 = numeric_col.quantile(0.75)

            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            outliers = (
                (numeric_col < lower) |
                (numeric_col > upper)
            ).sum()

            if outliers > 0:

                issues.append(
                    f"Column '{col}' has "
                    f"{outliers} potential outliers "
                    f"(unusually high or low values)"
                )

    return issues


# ─────────────────────────────
# CLEAN DATAFRAME
# ─────────────────────────────
def clean_dataframe(df, actions):

    df = df.copy()

    # ─────────────────────────────
    # REMOVE DUPLICATES
    # ─────────────────────────────
    if "remove_duplicates" in actions:

        df = df.drop_duplicates()

    # ─────────────────────────────
    # FILL MISSING NUMERIC VALUES
    # ─────────────────────────────
    if "fill_missing_mean" in actions:

        for col in df.select_dtypes(include='number').columns:

            df[col] = df[col].fillna(
                df[col].mean()
            )

    # ─────────────────────────────
    # FILL MISSING TEXT VALUES
    # ─────────────────────────────
    if "fill_missing_mode" in actions:

        for col in df.select_dtypes(include='object').columns:

            if not df[col].mode().empty:

                df[col] = df[col].fillna(
                    df[col].mode()[0]
                )

    # ─────────────────────────────
    # FIX DATA TYPES
    # ─────────────────────────────
    if "fix_dtypes" in actions:

        expected_numeric_cols = [
            "age",
            "salary",
            "performance_score"
        ]

        for col in expected_numeric_cols:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

    return df
