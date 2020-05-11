import os
import tempfile
from unittest import TestCase

import pandas as pd

from main import Rating, DataUpdater


class TestMerge(TestCase):
    def test_merge_does_not_affect_existing_rows(self):
        original_df = pd.DataFrame(
            {
                "name": ["Ben", "Rob"],
                "rating": [Rating.IGNORED.value, None],
                "slug": ["3890-ben-lerner", "4269-rob-marley"],
                "most_recent_date": ["2011-01-01", "2011-04-20"],
            }
        )
        new_df = pd.DataFrame(
            {
                "name": ["Ben", "Anonymous"],
                "rating": [None, None],
                "slug": ["3890-ben-lerner", "6942-anonymous-person"],
                "most_recent_date": ["2011-01-01", "2011-02-09"],
            }
        )
        expected_updated_df = pd.DataFrame(
            {
                "name": ["Ben", "Rob", "Anonymous"],
                "rating": [Rating.IGNORED.value, None, None],
                "slug": [
                    "3890-ben-lerner",
                    "4269-rob-marley",
                    "6942-anonymous-person",
                ],
                "most_recent_date": ["2011-01-01", "2011-04-20", "2011-02-09"],
            }
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            original_filename = os.sep.join([tmpdir, "original.pickle"])
            new_filename = os.sep.join([tmpdir, "new.pickle"])
            original_df.to_pickle(original_filename)
            new_df.to_pickle(new_filename)
            updater = DataUpdater(
                current_pickle_filename=original_filename,
                new_pickle_filename=new_filename,
            )
            updater.update()
            actual_updated_df = pd.read_pickle(original_filename)
            pd.testing.assert_frame_equal(expected_updated_df, actual_updated_df)
