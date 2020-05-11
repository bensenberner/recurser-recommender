import sys
import webbrowser
from enum import Enum

import os
import pandas as pd
import pyinputplus as pyip


class Rating(Enum):
    MESSAGED = "messaged"
    SNOOZED = "snoozed"
    IGNORED = "ignored"


BASE_DIRECTORY_URL = "https://www.recurse.com/directory/"


def _read_pickle(pickle_filename) -> pd.DataFrame:
    if isinstance(pickle_filename, str) and not os.path.exists(pickle_filename):
        raise FileNotFoundError(f"Make sure to create a {pickle_filename}!")
    return pd.read_pickle(pickle_filename)


def save_df(df, old_pickle_filename, current_pickle_filename) -> None:
    if os.path.exists(old_pickle_filename):
        os.remove(old_pickle_filename)
    if os.path.exists(current_pickle_filename):
        os.rename(current_pickle_filename, old_pickle_filename)
    df.to_pickle(current_pickle_filename)


def save_df_and_exit(df, old_pickle_filename, current_pickle_filename):
    save_df(df, old_pickle_filename, current_pickle_filename)
    sys.exit(0)


class Runner:
    def __init__(self, current_pickle_filename, old_pickle_filename):
        self.current_pickle_filename = current_pickle_filename
        self.old_pickle_filename = old_pickle_filename

    def _load_df(self, debug=False):
        if debug:
            return pd.DataFrame(
                {
                    "name": ["Ben", "Toph", "Christine", "Johann"],
                    "rating": [None, None, Rating.SNOOZED.value, Rating.SNOOZED.value],
                    "slug": [
                        "3890-ben-lerner",
                        "3585-toph-allen",
                        "3858-christine-jiang",
                        "3718-johann-diedrick",
                    ],
                    "most_recent_date": [
                        "2011-01-01",
                        "2013-01-01",
                        "2017-01-01",
                        "2019-01-01",
                    ],
                }
            )
        return _read_pickle(self.current_pickle_filename)

    @staticmethod
    def filter_and_sort(df: pd.DataFrame, rating_filter: str):
        # None represents not-yet-rated aka 'new' (to the user) recursers
        filtered_df = (
            df[df["rating"].isna()]
            if rating_filter == "n"
            else df[df["rating"] == Rating.SNOOZED.value]
        )
        return filtered_df.sort_values(by="most_recent_date", ascending=False)

    @staticmethod
    def display_row(row: pd.Series):
        url = BASE_DIRECTORY_URL + row["slug"]
        print(row["name"] + "|" + url)
        webbrowser.open(url)

    def rate_recursers(self, original_df, filtered_df):
        user_input_to_rating = {
            "m": Rating.MESSAGED.value,
            "i": Rating.IGNORED.value,
            "s": Rating.SNOOZED.value,
        }
        for i, row in filtered_df.iterrows():
            self.display_row(row)
            user_input = pyip.inputStr(
                "m to indicate that this person has already been messaged\n"
                "i to ignore this person, preventing them from showing up in the future\n"
                "s to snooze this person, allowing you to encounter them later\n"
                "q to quit, leaving this recurser's rating unchanged, saving all of session ratings>",
                allowRegexes=["^[misq]$"],
                blockRegexes=[".*"],
            )
            if user_input == "q":
                save_df_and_exit(
                    original_df, self.old_pickle_filename, self.current_pickle_filename
                )
            rating = user_input_to_rating[user_input]
            original_df.at[i, "rating"] = rating

        print(
            "You are all out of recursers to message! Wow! Maybe you should go back and widen your search a bit?"
        )
        save_df_and_exit(
            original_df, self.old_pickle_filename, self.current_pickle_filename
        )

    def run(self):
        original_df = self._load_df()
        rating_filter = pyip.inputStr(
            prompt="Enter:\nn for unseen recursers\ns for snoozed recursers\nq to quit>",
            allowRegexes=["^[nsq]$"],
            blockRegexes=[".*"],
        )
        if rating_filter == "q":
            sys.exit(0)
        filtered_df = self.filter_and_sort(original_df, rating_filter)
        self.rate_recursers(original_df, filtered_df)


class DataUpdater:
    def __init__(self, current_pickle_filename, new_pickle_filename):
        self.current_pickle_filename = current_pickle_filename
        self.new_pickle_filename = new_pickle_filename

    def update(self):
        current_data = _read_pickle(self.current_pickle_filename)
        new_rows = _read_pickle(self.new_pickle_filename)
        unseen_rows = new_rows[new_rows["slug"] != current_data["slug"]]
        updated_df = pd.concat([current_data, unseen_rows]).reset_index(drop=True)
        save_df(
            df=updated_df,
            old_pickle_filename=self.current_pickle_filename + "_old",
            current_pickle_filename=self.current_pickle_filename,
        )


# TODO: add a CLI debug mode?? to load db from memory
if __name__ == "__main__":
    PICKLE_FILENAME = "ratings.pickle"
    OLD_PICKLE_FILENAME = "old_ratings.pickle"
    runner = Runner(
        current_pickle_filename=PICKLE_FILENAME, old_pickle_filename=OLD_PICKLE_FILENAME
    )
    runner.run()
