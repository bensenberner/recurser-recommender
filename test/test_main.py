import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from main import Rating, Runner


class TestProd(TestCase):
    @patch("builtins.input")
    def test_creates_rating_pickle_if_not_exist(self, mock_input):
        mock_input.side_effect = ["y", ".*"]
        with tempfile.TemporaryDirectory() as tmpdir:
            original_filename = os.sep.join([tmpdir, "original.pickle"])

            self.assertFalse(os.path.exists(original_filename))
            Runner(current_pickle_filename=original_filename, is_prod=True)
            self.assertTrue(os.path.exists(original_filename))


class TestNonProd(TestCase):
    @patch("builtins.input", return_value="q")
    def test_quit(self, mock_input):
        runner = Runner(is_prod=False)
        runner.run()


class TestMerge(TestCase):
    # to make tests easier to read
    @patch("sys.stdout")
    @patch("builtins.input")
    @patch("main.create_df_with_regex_pattern")
    def test_merge_does_not_affect_existing_rows(self, mock_scraper, mock_input, _):
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
        mock_scraper.return_value = new_df

        with tempfile.TemporaryDirectory() as tmpdir:
            original_filename = os.sep.join([tmpdir, "original.pickle"])
            backup_filename = os.sep.join([tmpdir, "backup.pickle"])

            original_df.to_pickle(original_filename)

            runner = Runner(
                is_prod=True,
                current_pickle_filename=original_filename,
                backup_pickle_filename=backup_filename,
            )

            # first "update", then pass in a regex for filtering the new df
            mock_input.side_effect = ["u", ".*"]
            runner.run()

            actual_updated_df = pd.read_pickle(original_filename)
            actual_backup_df = pd.read_pickle(backup_filename)
            pd.testing.assert_frame_equal(expected_updated_df, actual_updated_df)
            pd.testing.assert_frame_equal(original_df, actual_backup_df)
