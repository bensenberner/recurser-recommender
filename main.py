import os
import sys
import webbrowser
from enum import Enum

import click
import pandas as pd
import pyinputplus as pyip

from scraper import create_df_with_regex_pattern


class Rating(Enum):
    MESSAGED = "messaged"
    SNOOZED = "snoozed"
    IGNORED = "ignored"


BASE_DIRECTORY_URL = "https://www.recurse.com/directory/"


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


def _load_fake_updated_df():
    return pd.DataFrame(
        {
            "name": ["Ben", "Plato"],
            "rating": [None, None],
            "email": ["hacker_man@big.data", "good@republ.ic"],
            "slug": ["3890-ben-lerner", "1002-plato-greek"],
            "most_recent_date": ["2011-01-01", "1990-02-03"],
        }
    )


class Runner:
    def __init__(
        self, is_debug, current_pickle_filename, backup_pickle_filename, initial_offset,
    ):
        self.is_debug = is_debug
        self.current_pickle_filename = current_pickle_filename
        self.backup_pickle_filename = backup_pickle_filename
        self.initial_offset = initial_offset
        if not self.is_debug:
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

    def _display_row(self, row: pd.Series):
        url = BASE_DIRECTORY_URL + row["slug"]
        print(f"{row['name']} | {url}")
        if not self.is_debug:
            webbrowser.open(url)

    def _overwrite_backup_and_save_df(self, df) -> None:
        if os.path.exists(self.backup_pickle_filename):
            os.remove(self.backup_pickle_filename)
        if os.path.exists(self.current_pickle_filename):
            os.rename(self.current_pickle_filename, self.backup_pickle_filename)
        df.to_pickle(self.current_pickle_filename)

    def rate_recursers(self, original_df, filtered_df):
        user_input_to_rating = {
            "m": Rating.MESSAGED.value,
            "i": Rating.IGNORED.value,
            "s": Rating.SNOOZED.value,
        }
        print("------------------")
        help_msg = (
            "h to print this message\n"
            "m to indicate that this person has already been messaged\n"
            "i to ignore this person, preventing them from showing up in the future\n"
            "s to snooze this person, allowing you to encounter them later\n"
            "q to quit, leaving this recurser's rating unchanged, saving all of session ratings\n"
            "! to quit WITHOUT saving any changes from this session\n"
            "-------------------"
        )
        print(help_msg)
        for i, row in filtered_df.iterrows():
            self._display_row(row)
            while True:
                user_input = pyip.inputStr(
                    "Enter a char in [hmisq!] >\n",
                    allowRegexes=["^[hmisq!]$"],
                    blockRegexes=[".*"],
                )
                if user_input != "h":
                    break
                print(help_msg)
            if user_input == "!":
                return
            if user_input == "q":
                self._overwrite_backup_and_save_df(original_df)
                return
            rating = user_input_to_rating[user_input]
            original_df.at[i, "rating"] = rating

        should_save = pyip.inputStr(
            "You are all out of recursers to message!\n"
            "Enter s to save this session's ratings, or any other letter to exit without saving>"
        )
        if should_save == "s":
            self._overwrite_backup_and_save_df(original_df)

    def _build_new_df_from_scratch(self) -> pd.DataFrame:
        if self.is_debug:
            return _load_fake_updated_df()
        regex_str = pyip.inputStr(
            "Enter a regex to filter recurser bios. The regex '.*' will match everything. Don't include quotation marks>\n"
        )
        return create_df_with_regex_pattern(
            regex_str, initial_offset=self.initial_offset
        )

    def _create_ratings_pickle_if_not_exists_or_exit(self) -> None:
        if os.path.exists(self.current_pickle_filename):
            return
        choice = pyip.inputStr(
            prompt=(
                f"Could not find pickle file located at {self.current_pickle_filename}.\n"
                f"Would you like to pull fresh data from the RC directory? (offset {self.initial_offset}) [y/n]>\n"
            ),
            allowRegexes=["^[yn]$"],
            blockRegexes=[".*"],
        )
        if choice == "y":
            df = self._build_new_df_from_scratch()
            df.to_pickle(self.current_pickle_filename)
        else:
            print("Okay, exiting without doing anything.")
            sys.exit(0)

    def _update(self, current_df):
        new_df = self._build_new_df_from_scratch()
        current_slugs = set(current_df["slug"])
        never_before_seen_rows = new_df[
            new_df.apply(lambda row: row["slug"] not in current_slugs, axis=1)
        ]
        print(f"{never_before_seen_rows.shape[0]} new rows added")
        updated_df = pd.concat([current_df, never_before_seen_rows]).reset_index(
            drop=True
        )
        self._overwrite_backup_and_save_df(df=updated_df)

    def run(self):
        usage_option = pyip.inputStr(
            prompt=(
                "n for unseen recursers\n"
                "s for snoozed recursers\n"
                f"u to update the database with new recursers (offset {self.initial_offset}) and exit\n"
                "q to quit>\n"
            ),
            allowRegexes=["^[nsuq]$"],
            blockRegexes=[".*"],
        )
        if usage_option == "q":
            return

        current_df = (
            _load_fake_df()
            if self.is_debug
            else pd.read_pickle(self.current_pickle_filename)
        )
        if usage_option == "u":
            self._update(current_df)
            return self.run()
        rating_filter = usage_option
        filtered_df = self.filter_and_sort(current_df, rating_filter)
        self.rate_recursers(current_df, filtered_df)


@click.command()
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="With debug on, all data will come from statically defined dataframes; no disc or internet I/O",
)
@click.option(
    "--current_pickle",
    type=str,
    default="data/recursers.pickle",
    help="Path of the pickle file with the current db",
)
@click.option(
    "--backup_pickle",
    type=str,
    default="data/recursers_backup.pickle",
    help="Path of the pickle file with the previous version of the db",
)
@click.option(
    "--initial_offset",
    type=int,
    # TODO: change this for demo
    default=1700,
    help="The initial offset for requests made to the recurse API. ",
)
def main(debug, current_pickle, backup_pickle, initial_offset):
    runner = Runner(
        is_debug=debug,
        current_pickle_filename=current_pickle,
        backup_pickle_filename=backup_pickle,
        initial_offset=initial_offset,
    )
    runner.run()


if __name__ == "__main__":
    main()
