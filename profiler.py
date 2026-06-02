import pandas as pd


def generate_profile(df):

    profile_data = []

    total_rows = len(df)

    for column in df.columns:

        missing_count = df[column].isnull().sum()

        missing_percent = round(
            (missing_count / total_rows) * 100,
            2
        )

        unique_count = df[column].nunique()

        unique_percent = round(
            (unique_count / total_rows) * 100,
            2
        )

        dtype = str(df[column].dtype)

        recommendation = "No action needed"

        # Smart recommendations
        if missing_percent > 30:

            recommendation = (
                "High missing values detected"
            )

        elif dtype == "object":

            recommendation = (
                "Check text consistency"
            )

        elif unique_percent < 5:

            recommendation = (
                "Possible categorical column"
            )

        profile_data.append({

            "Column": column,

            "Data Type": dtype,

            "Missing %": missing_percent,

            "Unique %": unique_percent,

            "Recommendation": recommendation
        })

    profile_df = pd.DataFrame(profile_data)

    return profile_df
