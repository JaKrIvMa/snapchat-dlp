"""The Main Snapchat Downloader Class."""
import concurrent.futures
import json
import os
import re
import time

import requests
from loguru import logger

from snapchat_dlp.downloader import download_url
from snapchat_dlp.utils import APIResponseError
from snapchat_dlp.utils import dump_response
from snapchat_dlp.utils import MEDIA_TYPE
from snapchat_dlp.utils import NoStoriesFound
from snapchat_dlp.utils import strf_time
from snapchat_dlp.utils import UserNotFoundError


class SnapchatDL:
    """Interact with Snapchat API to download story."""

    def __init__(
        self,
        directory_prefix=".",
        max_workers=2,
        limit_story=-1,
        sleep_interval=1,
        quiet=False,
        dump_json=False,
    ):
        self.directory_prefix = os.path.abspath(os.path.normpath(directory_prefix))
        self.max_workers = max_workers
        self.limit_story = limit_story
        self.sleep_interval = sleep_interval
        self.quiet = quiet
        self.dump_json = dump_json
        self.endpoint_web = "https://story.snapchat.com/@{}"
        self.regexp_web_json = (
            r'<script\s*id="__NEXT_DATA__"\s*type="application\/json">([^<]+)<\/script>'
        )

    def _api_response(self, username):
        web_url = self.endpoint_web.format(username)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            )
        }
        return requests.get(web_url, headers=headers)

    def _web_fetch_story(self, username):
        """Download user stories from Web.

        Args:
            username (str): Snapchat `username`

        Raises:
            APIResponseError: API Error

        Returns:
            (list, dict): stories, user_info
        """
        response = self._api_response(username)

        if response.status_code != requests.codes.ok:
            if response.status_code == 404:
                logger.error(f"User '{username}' not found (404).")
            else:
                logger.error(f"Failed to fetch data for '{username}'. Status code: {response.status_code}.")
            raise APIResponseError

        response_json_raw = re.findall(self.regexp_web_json, response.text)

        try:
            response_json = json.loads(response_json_raw[0])

            def util_web_user_info(content: dict):
                if "userProfile" in content["props"]["pageProps"]:
                    user_profile = content["props"]["pageProps"]["userProfile"]
                    field_id = user_profile["$case"]
                    return user_profile[field_id]
                else:
                    raise UserNotFoundError

            def util_web_story(content: dict):
                if "story" in content["props"]["pageProps"]:
                    return content["props"]["pageProps"]["story"]["snapList"]
                return list()

            user_info = util_web_user_info(response_json)
            stories = util_web_story(response_json)
            return stories, user_info
        except (IndexError, KeyError, ValueError) as e:
            logger.error(f"Error parsing response for '{username}': {e}")
            raise APIResponseError

    def _download_media(self, media, username, snap_user):
        snap_id = media["snapId"]["value"]
        media_url = media["snapUrls"]["mediaUrl"]
        media_type = media["snapMediaType"]
        timestamp = int(media["timestampInSec"]["value"])
        date_str = strf_time(timestamp, "%Y-%m-%d")

        dir_name = os.path.join(self.directory_prefix, username, date_str)
        os.makedirs(dir_name, exist_ok=True)  # Ensure the directory exists

        filename = strf_time(timestamp, "%Y-%m-%d_%H-%M-%S {} {}.{}").format(
            snap_id, username, MEDIA_TYPE[media_type]
        )

        if self.dump_json:
            filename_json = os.path.join(dir_name, f"{filename}.json")
            media_json = dict(media)
            media_json["snapUser"] = snap_user
            dump_response(media_json, filename_json)

        media_output = os.path.join(dir_name, filename)
        return media_url, media_output

    def download(self, username):
        """Download Snapchat Story for `username`.

        Args:
            username (str): Snapchat `username`
        """
        try:
            stories, snap_user = self._web_fetch_story(username)
        except APIResponseError:
            logger.error(f"Could not fetch data for '{username}'. The user may not exist or has no public stories.")
            return

        if not stories:
            if not self.quiet:
                logger.info(f"{username} has no stories.")
            return

        logger.info(f"[+] {username} has {len(stories)} stories.")

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        try:
            for media in stories:
                media_url, media_output = self._download_media(media, username, snap_user)
                executor.submit(download_url, media_url, media_output, self.sleep_interval)
        except KeyboardInterrupt:
            executor.shutdown(wait=False)

        logger.info(f"[✔] {len(stories)} stories downloaded for {username}.")
