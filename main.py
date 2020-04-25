import sys
import webbrowser
from enum import Enum

import os
import pandas as pd
import pyinputplus as pyip


class Rating(Enum):
    MESSAGED = 'messaged'
    SNOOZED = 'snoozed'
    IGNORED = 'ignored'


PICKLE_FILENAME = 'ratings.pickle'
OLD_PICKLE_FILENAME = 'old_ratings.pickle'
BASE_DIRECTORY_URL = "https://www.recurse.com/directory/"


def load_df(debug=False):
    if debug:
        return pd.DataFrame({
            'name': ['Ben', 'Toph', 'Christine', 'Johann'],
            'rating': [None, None, Rating.SNOOZED.value, Rating.SNOOZED.value],
            'slug': ['3890-ben-lerner', '3585-toph-allen', '3858-christine-jiang', '3718-johann-diedrick'],
            'most_recent_date': ['2011-01-01', '2013-01-01', '2017-01-01', '2019-01-01']
        })
    if not os.path.exists(PICKLE_FILENAME):
        raise FileNotFoundError(f'Make sure to create a {PICKLE_FILENAME}!')
    return pd.read_pickle(PICKLE_FILENAME)


def filter_and_sort(df: pd.DataFrame, rating_filter: str):
    # None represents not-yet-rated aka 'new' (to the user) recursers
    filtered_df = (
        df[df['rating'].isna()]
        if rating_filter == 'n' else
        df[df['rating'] == Rating.SNOOZED.value]
    )
    return filtered_df.sort_values(by='most_recent_date', ascending=False)


def display_row(row: pd.Series):
    url = BASE_DIRECTORY_URL + row['slug']
    print(row['name'] + "|" + url)
    webbrowser.open(url)


def save_df_and_exit(df):
    if os.path.exists(OLD_PICKLE_FILENAME):
        os.remove(OLD_PICKLE_FILENAME)
    if os.path.exists(PICKLE_FILENAME):
        os.rename(PICKLE_FILENAME, OLD_PICKLE_FILENAME)
    df.to_pickle(PICKLE_FILENAME)
    sys.exit(0)


def rate_recursers(original_df, filtered_df):
    user_input_to_rating = {
        'm': Rating.MESSAGED.value,
        'i': Rating.IGNORED.value,
        's': Rating.SNOOZED.value
    }
    for i, row in filtered_df.iterrows():
        display_row(row)
        user_input = pyip.inputStr(
            'm to indicate that this person has already been messaged\n'
            'i to ignore this person, preventing them from showing up in the future\n'
            's to snooze this person, allowing you to encounter them later\n'
            "q to quit, leaving this recurser's rating unchanged, saving all of session ratings>",
            allowRegexes=['^[misq]$'],
            blockRegexes=['.*']
        )
        if user_input == 'q':
            save_df_and_exit(original_df)
        rating = user_input_to_rating[user_input]
        original_df.at[i, 'rating'] = rating

    print("You are all out of recursers to message! Wow! Maybe you should go back and widen your search a bit?")
    save_df_and_exit(original_df)


def main():
    original_df = load_df()
    rating_filter = pyip.inputStr(
        prompt="Enter:\nn for unseen recursers\ns for snoozed recursers\nq to quit>",
        allowRegexes=['^[nsq]$'],
        blockRegexes=['.*']
    )
    if rating_filter == 'q':
        sys.exit(0)
    filtered_df = filter_and_sort(original_df, rating_filter)
    rate_recursers(original_df, filtered_df)


# TODO: add a CLI debug mode?? to load db from memory
if __name__ == "__main__":
    main()
