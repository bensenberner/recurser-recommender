import os
import re
from urllib.parse import urlencode

import pandas as pd
import requests


def _get_auth_token() -> str:
    return (
        os.environ.get("RECURSE_AUTH_TOKEN")
        if os.environ.get("RECURSE_AUTH_TOKEN")
        else input(
            "Could not find a $RECURSE_AUTH_TOKEN in your environment.\n"
            "Please visit https://www.recurse.com/settings/apps to create a new app token and paste it in here:"
        )
    )


def _collect_directory_into_df(initial_offset=0) -> pd.DataFrame:
    # currently 1773 recursers; about 3Mb of data
    url_base = "https://www.recurse.com/api/v1/profiles?"
    auth_token = _get_auth_token()
    headers = {"Authorization": "Bearer " + auth_token}
    offset = initial_offset
    limit = 15
    full_results = []
    while True:
        query_string = urlencode(dict(offset=offset, limit=limit))
        url = url_base + query_string
        response = requests.get(url, headers=headers)
        new_results = response.json()
        if not new_results:
            break
        full_results.extend(new_results)
        offset += limit
    return pd.DataFrame(full_results)


def _get_attendance_date_column(df):
    def most_recent_attendance(row):
        stints = row["stints"]
        if not stints:
            return None
        most_recent_start_date = stints[0]["start_date"]
        if len(stints) == 1:
            return most_recent_start_date
        for stint in stints[1:]:
            # using start date because some people don't have end dates
            curr_start_date = stint["start_date"]
            most_recent_start_date = max(most_recent_start_date, curr_start_date)
        return most_recent_start_date

    return pd.to_datetime(df.apply(lambda row: most_recent_attendance(row), axis=1))


def _create_df_filtered_by_pattern(
    df: pd.DataFrame, regex_pattern: re.Pattern
) -> pd.DataFrame:
    def filter_for_keywords(*values):
        return any(bool(regex_pattern.search(value)) for value in values)

    text_cols = df[
        [
            "before_rc_rendered",
            "interests_rendered",
            "bio_rendered",
            "during_rc_rendered",
        ]
    ]
    return df[text_cols.apply(lambda values: filter_for_keywords(*values), axis=1)]


def create_df_with_regex_pattern(pattern_str: str, initial_offset=0):
    regex_pattern = re.compile(pattern_str, flags=re.IGNORECASE)
    original_df = _collect_directory_into_df(initial_offset)
    original_df["most_recent_date"] = _get_attendance_date_column(original_df)
    keyword_filtered_df = _create_df_filtered_by_pattern(original_df, regex_pattern)
    small_df = keyword_filtered_df[["name", "email", "slug", "most_recent_date"]]
    return small_df.assign(rating=None)
