#!/usr/bin/env python
"""Tests for `snapchat_dlp` package."""
import json
import os
import shutil
import unittest
from unittest import mock

from snapchat_dlp.snapchat_dlp import SnapchatDL
from snapchat_dlp.utils import APIResponseError
from snapchat_dlp.utils import NoStoriesFound
from snapchat_dlp.utils import UserNotFoundError


def teardown_module(module):
    shutil.rmtree(".test-data")


class TestSnapchat_dl(unittest.TestCase):
    """Tests for `snapchat_dlp` package."""

    def setUp(self):
        """Set up test fixtures."""
        self.snapchat_dlp = SnapchatDL(
            limit_story=10, quiet=True, directory_prefix=".test-data", dump_json=True,
        )
        self.test_url = "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"
        self.test_url404 = "https://google.com/error.html"
        self.username = "invalidusername"
        self.html = open(
            "tests/mock_data/invalidusername.html", "r", encoding="utf8"
        ).read()
        self.html_api_error = open(
            "tests/mock_data/api-error.html", "r", encoding="utf8"
        ).read()
        self.html_nostories = open(
            "tests/mock_data/invalidusername-nostories.html", "r", encoding="utf8"
        ).read()

    def test_class_init(self):
        """Test snapchat_dlp init."""
        self.assertTrue(self.snapchat_dlp)

    def test_invalid_username(self):
        """Test snapchat_dlp Stories are not available."""
        with self.assertRaises(UserNotFoundError):
            self.snapchat_dlp.download("username")

    @mock.patch("snapchat_dlp.snapchat_dlp.SnapchatDL._api_response")
    def test_api_error(self, api_response):
        """Test snapchat_dlp Download."""
        api_response.return_value = self.html_api_error
        with self.assertRaises(APIResponseError):
            self.snapchat_dlp.download(self.username)

    @mock.patch("snapchat_dlp.snapchat_dlp.SnapchatDL._api_response")
    def test_get_stories(self, api_response):
        """Test snapchat_dlp Download."""
        api_response.return_value = self.html
        self.snapchat_dlp.download(self.username)

    @mock.patch("snapchat_dlp.snapchat_dlp.SnapchatDL._api_response")
    def test_no_stories(self, api_response):
        """Test snapchat_dlp Download."""
        api_response.return_value = self.html_nostories
        with self.assertRaises(NoStoriesFound):
            self.snapchat_dlp.download(self.username)
