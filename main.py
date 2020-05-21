import sys
import webbrowser
from enum import Enum

import os
import pandas as pd
import pyinputplus as pyip

from scraper import create_df_with_regex_pattern


class Rating(Enum):
    MESSAGED = "messaged"
    SNOOZED = "snoozed"
    IGNORED = "ignored"


BASE_DIRECTORY_URL = "https://www.recurse.com/directory/"


def _build_new_df_from_scratch() -> pd.DataFrame:
    regex_str = pyip.inputStr(
        "Enter a regex to filter recurser bios. The regex '.*' will match everything. Don't include quotation marks"
    )
    # TODO: remove this!!
    return create_df_with_regex_pattern(regex_str, initial_offset=1750)


def _read_pickle_or_create_new_data(pickle_filename) -> pd.DataFrame:
    if isinstance(pickle_filename, str) and not os.path.exists(pickle_filename):
        choice = pyip.inputStr(
            prompt=f"Could not find pickle file located at {pickle_filename}. Would you like to pull fresh data from the RC directory? [y/n]",
            allowRegexes=["^[yn]$"],
            blockRegexes=[".*"],
        )
        if choice == "y":
            return _build_new_df_from_scratch()
        else:
            print("Okay, exiting without doing anything.")
            sys.exit(0)
    return pd.read_pickle(pickle_filename)


def _overwrite_backup_and_save_df(
    df, backup_pickle_filename, current_pickle_filename
) -> None:
    if os.path.exists(backup_pickle_filename):
        os.remove(backup_pickle_filename)
    if os.path.exists(current_pickle_filename):
        os.rename(current_pickle_filename, backup_pickle_filename)
    df.to_pickle(current_pickle_filename)


class Runner:
    def __init__(self, current_pickle_filename, backup_pickle_filename):
        self.current_pickle_filename = current_pickle_filename
        self.backup_pickle_filename = backup_pickle_filename

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
        return _read_pickle_or_create_new_data(self.current_pickle_filename)

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
                _overwrite_backup_and_save_df(
                    original_df,
                    self.backup_pickle_filename,
                    self.current_pickle_filename,
                )
                return
            rating = user_input_to_rating[user_input]
            original_df.at[i, "rating"] = rating

        print(
            "You are all out of recursers to message! Wow! Maybe you should go back and widen your search a bit?"
        )
        _overwrite_backup_and_save_df(
            original_df, self.backup_pickle_filename, self.current_pickle_filename
        )

    def run(self):
        usage_option = pyip.inputStr(
            prompt="Enter:\nn for unseen recursers\ns for snoozed recursers\nu to update the database with new recursers\nq to quit>",
            allowRegexes=["^[nsqu]$"],
            blockRegexes=[".*"],
        )
        if usage_option == "q":
            return
        if usage_option == "u":
            raise NotImplementedError
        original_df = self._load_df()
        rating_filter = usage_option
        filtered_df = self.filter_and_sort(original_df, rating_filter)
        self.rate_recursers(original_df, filtered_df)


# TODO: just merge this in with the main stuff
class DataUpdater:
    def __init__(self, current_pickle_filename, new_pickle_filename):
        self.current_pickle_filename = current_pickle_filename
        self.new_pickle_filename = new_pickle_filename

    def update(self):
        current_data = _read_pickle_or_create_new_data(self.current_pickle_filename)
        new_rows = _read_pickle_or_create_new_data(self.new_pickle_filename)
        unseen_rows = new_rows[new_rows["slug"] != current_data["slug"]]
        updated_df = pd.concat([current_data, unseen_rows]).reset_index(drop=True)
        _overwrite_backup_and_save_df(
            df=updated_df,
            backup_pickle_filename=self.current_pickle_filename + "_old",
            current_pickle_filename=self.current_pickle_filename,
        )


# TODO: add a CLI debug mode?? to load db from memory
if __name__ == "__main__":
    CURRENT_PICKLE_FILENAME = "data/ratings.pickle"
    BACKUP_PICKLE_FILENAME = "data/old_ratings.pickle"
    runner = Runner(
        current_pickle_filename=CURRENT_PICKLE_FILENAME,
        backup_pickle_filename=BACKUP_PICKLE_FILENAME,
    )
    runner.run()
