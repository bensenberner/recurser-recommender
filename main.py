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
    # TODO: remove me!!
    return create_df_with_regex_pattern(regex_str, initial_offset=1750)


def _overwrite_backup_and_save_df(
    df, backup_pickle_filename, current_pickle_filename
) -> None:
    if os.path.exists(backup_pickle_filename):
        os.remove(backup_pickle_filename)
    if os.path.exists(current_pickle_filename):
        os.rename(current_pickle_filename, backup_pickle_filename)
    df.to_pickle(current_pickle_filename)


def _load_fake_df():
    return pd.DataFrame(
        {
            "name": ["Ben", "Toph", "Christine", "Johann"],
            "rating": [None, None, Rating.SNOOZED.value, Rating.SNOOZED.value],
            "email": [
                "hacker_man@big.data",
                "toph@allen.ai",
                "christine@data.science",
                "johann@sebastian.bach",
            ],
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


class Runner:
    # TODO: don't do this
    def __init__(
        self,
        is_prod,
        current_pickle_filename="data/ratings.pickle",
        backup_pickle_filename="data/ratings_backup.pickle",
    ):
        self.current_pickle_filename = current_pickle_filename
        self.backup_pickle_filename = backup_pickle_filename
        self.is_prod = is_prod
        if self.is_prod:
            self._create_ratings_pickle_if_not_exists_or_exit()

    @staticmethod
    def filter_and_sort(df: pd.DataFrame, rating_filter: str):
        # None represents not-yet-rated aka 'new' (to the user) recursers
        filtered_df = (
            df[df["rating"].isna()]
            if rating_filter == "n"
            else df[df["rating"] == Rating.SNOOZED.value]
        )
        return filtered_df.sort_values(by="most_recent_date", ascending=False)

    def display_row(self, row: pd.Series):
        url = BASE_DIRECTORY_URL + row["slug"]
        print(row["name"] + "|" + url)
        if self.is_prod:
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
                "q to quit, leaving this recurser's rating unchanged, saving all of session ratings\n"
                "! to quit WITHOUT saving any changes from this session>",
                allowRegexes=["^[misq!]$"],
                blockRegexes=[".*"],
            )
            if user_input == "!":
                return
            if user_input == "q":
                _overwrite_backup_and_save_df(
                    original_df,
                    self.backup_pickle_filename,
                    self.current_pickle_filename,
                )
                return
            rating = user_input_to_rating[user_input]
            original_df.at[i, "rating"] = rating

        should_save = pyip.inputStr(
            "You are all out of recursers to message!\n"
            "Enter y to save this session's ratings, or any other letter to exit without saving>"
        )
        if should_save == "y":
            _overwrite_backup_and_save_df(
                original_df, self.backup_pickle_filename, self.current_pickle_filename
            )

    def _create_ratings_pickle_if_not_exists_or_exit(self) -> None:
        if os.path.exists(self.current_pickle_filename):
            return
        choice = pyip.inputStr(
            prompt=(
                f"Could not find pickle file located at {self.current_pickle_filename}.\n"
                f"Would you like to pull fresh data from the RC directory? [y/n]>"
            ),
            allowRegexes=["^[yn]$"],
            blockRegexes=[".*"],
        )
        if choice == "y":
            df = _build_new_df_from_scratch()
            df.to_pickle(self.current_pickle_filename)
        else:
            print("Okay, exiting without doing anything.")
            sys.exit(0)

    def run(self):
        usage_option = pyip.inputStr(
            prompt="Enter:\nn for unseen recursers\ns for snoozed recursers\nu to update the database with new recursers and exit\nq to quit>",
            allowRegexes=["^[nsqu]$"],
            blockRegexes=[".*"],
        )
        if usage_option == "q":
            return
        if usage_option == "u":
            raise NotImplementedError

        current_df = (
            pd.read_pickle(self.current_pickle_filename)
            if self.is_prod
            else _load_fake_df()
        )
        rating_filter = usage_option
        filtered_df = self.filter_and_sort(current_df, rating_filter)
        self.rate_recursers(current_df, filtered_df)


# TODO: just merge this in with the main stuff
class DataUpdater:
    def __init__(self, current_pickle_filename, new_pickle_filename):
        self.current_pickle_filename = current_pickle_filename
        self.new_pickle_filename = new_pickle_filename

    def update(self):
        current_data = pd.read_pickle(self.current_pickle_filename)
        new_rows = pd.read_pickle(self.new_pickle_filename)
        unseen_rows = new_rows[new_rows["slug"] != current_data["slug"]]
        updated_df = pd.concat([current_data, unseen_rows]).reset_index(drop=True)
        _overwrite_backup_and_save_df(
            df=updated_df,
            backup_pickle_filename=self.current_pickle_filename + "_old",
            current_pickle_filename=self.current_pickle_filename,
        )


# TODO: add a CLI debug mode?? to load db from memory
if __name__ == "__main__":
    runner = Runner(is_prod=False)
    runner.run()
