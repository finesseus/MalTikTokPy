"""
Synchronous API for data scraping
"""

from __future__ import annotations

import json
import traceback
import warnings
from time import sleep
import re
import os
from typing import Literal, Optional, Type, TypeVar, Union

from playwright.sync_api import Page, Route, TimeoutError, sync_playwright
from pydantic import ValidationError
from . import ERROR_CODES, TikTokAPIError, TikTokAPIWarning
from .models.challenge import Challenge
from .models.raw_data import (
    ChallengePage,
    PrimaryResponseType,
    SentToLoginResponse,
    UserResponse,
    VideoPage,
)
from .models.user import User, user_link
from .models.video import Video, is_mobile_share_link
from .util.queries import get_challenge_detail_sync, get_video_detail_sync

from urllib.parse import urlparse

if os.environ.get("img_block") == 'True':
    async def intercept(route, request):
        if request.resource_type in {'image'}:
            await route.abort()
        else:
            await route.continue_()

_DataModelT = TypeVar("_DataModelT", bound=PrimaryResponseType, covariant=True)
"""
Generic used for data scraping.
"""
def parse_proxy1(proxy_string):
    """Parse a proxy string into its components."""
    protocol, rest = proxy_string.split('://', 1)
    user_pass, server_port = rest.split('@')
    username, password = user_pass.split(':')
    server, port = server_port.split(':')
    thing =  {
        'protocol': protocol,
        'username': username,
        'password': password,
        'server': server,
        'port': port
    }
    print(thing)
    exit()

def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    parsed = urlparse(proxy_str)
    proxyInfo = {
        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
        "username": parsed.username,
        "password": parsed.password
    }
    return proxyInfo
    

class TikTokAPI:
    """Synchronous API used to scrape data from TikTok"""

    def __init__(
        self,
        *,
        proxy: Optional[str] = None,
        headless: bool = None,
        data_dump_file: str = None,
        navigation_timeout: float = 30,
        navigation_retries: int = 0,
        context_kwargs: dict = None,
        navigator_type: Optional[
            Literal["Firefox", "firefox", "Chromium", "chromium"]
        ] = None,
        **kwargs,
    ):
        """
        :param headless: Whether to use headless browsing.
        :param data_dump_file: If the data scraped from TikTok should also be dumped to a JSON file before parsing,
            specify the name of the dump file (excluding '.json').
        :param navigation_timeout: How long (in milliseconds) page navigation should wait before timing out. Set to 0 to
            disable the timeout.
        :param navigation_retries: How many times to retry navigation if ``network_timeout`` is exceeded. Set to 0 to
            not retry navigation.
        :param context_kwargs: Any extra kwargs used to initialize the playwright browser context. For full details,
            see `Browser::new_context() <https://playwright.dev/python/docs/api/class-browser#browser-new-context>`_.
        :param navigator_type: **DEPRECATED as of 0.1.13**, left in for backwards-compatibility.
        :param kwargs: Any extra kwargs used to initialize the playwright browser (e.g.: proxy, etc.).
            For full details, see
            `BrowserType::launch() <https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch>`_.
        """
        self.headless = headless
        self.proxy = parse_proxy(proxy)
        self.data_dump_file = data_dump_file
        self.context_kwargs = context_kwargs or {}
        self.navigation_timeout = navigation_timeout * 1000
        self.navigation_retries = navigation_retries
        self.kwargs = kwargs
        if navigator_type is not None:
            warnings.warn(
                "The navigator_type parameter is deprecated. Chromium is always used as of 0.1.13.",
                category=DeprecationWarning,
                stacklevel=2,
            )

    def __enter__(self) -> TikTokAPI:
        self._playwright = sync_playwright().start()

        
        self._browser = self.playwright.chromium.launch(
            headless=self.headless, proxy=self.proxy,
        )

        context_kwargs = self.context_kwargs
        context_kwargs.update(self.playwright.devices["Desktop Edge"])

        self._context = self.browser.new_context(**context_kwargs)
        self.context.set_default_navigation_timeout(self.navigation_timeout)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    @property
    def playwright(self):
        """The playwright instance used for data scraping"""
        if not hasattr(self, "_playwright"):
            raise TikTokAPIError("TikTokAPI must be used as a context manager")
        return self._playwright

    @property
    def browser(self):
        """The playwright Browser instance used for data scraping"""
        if not hasattr(self, "_browser"):
            raise TikTokAPIError("TikTokAPI must be used as a context manager")
        return self._browser

    @property
    def context(self):
        """The playwright Context instance used for data scraping"""
        if not hasattr(self, "_context"):
            raise TikTokAPIError("TikTokAPI must be used as a context manager")
        return self._context

    def challenge(self, challenge_name: str, *, video_limit: int = -1) -> Challenge:
        """
        Retrieve data on a :class:`.Challenge` (hashtag) from TikTok. Only up to the ``video_limit`` most recent videos
        will be retrievable by the scraper.

        :param challenge_name: The name of the challenge. e.g.: ``"fyp"``
        :return: A :class:`.Challenge` object containing the scraped data
        :rtype: :class:`.Challenge`
        """
        response = ChallengePage.model_validate(
            get_challenge_detail_sync(challenge_name, self.context)
        )
        challenge = self._extract_challenge_from_response(response)
        challenge.videos.limit(video_limit)
        return challenge

    def user(self, user: Union[int, str], *, video_limit: int = -1) -> User:
        """
        Retrieve data on a :class:`.User` from TikTok. Only up to the ``video_limit`` most recent videos will be
        retrievable by the scraper.

        :param user: The unique user or id of the user. e.g.: for @tiktok, use ``"tiktok"``
        :return: A :class:`.User` object containing the scraped data
        :rtype: :class:`.User`
        """
        link = user_link(user)
        response = self._scrape_data(
            link,
            UserResponse,
        )
        user = self._extract_user_from_response(response)
        user.videos.limit(video_limit)
        return user

    def video(
        self,
        link_or_id: Union[int, str],
    ) -> Video:
        """
        Retrieve data on a :class:`.Video` from TikTok. If the video is a slideshow, :attr:`.emulate_mobile` must be
        set to ``True`` at API initialization or this method will raise a :exc:`TikTokAPIError`.

        :param link_or_id: The link to the video or its unique ID.
        :return: A :class:`.Video` object containing the scraped data
        :rtype: :class:`.Video`
        """
        if isinstance(link_or_id, str):
            if is_mobile_share_link(link_or_id):
                self.context.clear_cookies()
                page: Page = self.context.new_page()
                page.add_init_script(
                    """
    if (navigator.webdriver === false) {
        // Post Chrome 89.0.4339.0 and already good
    } else if (navigator.webdriver === undefined) {
        // Pre Chrome 89.0.4339.0 and already good
    } else {
        // Pre Chrome 88.0.4291.0 and needs patching
        delete Object.getPrototypeOf(navigator).webdriver
    }
                """
                )

                def ignore_scripts(route: Route):
                    if route.request.resource_type == "script":
                        return route.abort()
                    return route.continue_()

                page.route("**/*", ignore_scripts)
                if os.environ.get("img_block") == 'True':
                    page.route("**/*", lambda route: route.abort()
                        if route.request.resource_type in ["image", "media"]
                        else route.continue_()
                        )
                page.goto(link_or_id, wait_until=None)
                page.wait_for_selector("#SIGI_STATE", state="attached")

                link_or_id = page.url

                page.close()
            video_id = link_or_id.split("/")[-1].split("?")[0]
        else:
            video_id = link_or_id

        response = VideoPage.model_validate(
            get_video_detail_sync(video_id, self.context)
        )
        return self._extract_video_from_response(response)

    def _scrape_data(
        self,
        link: str,
        data_model: Type[_DataModelT],
    ) -> _DataModelT:
        for _ in range(self.navigation_retries + 1):
            self.context.clear_cookies()
            page: Page = self.context.new_page()
            page.add_init_script(
                """
if (navigator.webdriver === false) {
    // Post Chrome 89.0.4339.0 and already good
} else if (navigator.webdriver === undefined) {
    // Pre Chrome 89.0.4339.0 and already good
} else {
    // Pre Chrome 88.0.4291.0 and needs patching
    delete Object.getPrototypeOf(navigator).webdriver
}
            """
            )

            def ignore_scripts(route: Route):
                if route.request.resource_type == "script":
                    return route.abort()
                return route.continue_()

            # page.route("**/*", ignore_scripts)
            # page.route('**/*', intercept)
            if os.environ.get("img_block") == 'True':
                page.route("**/*", lambda route: route.abort()
                    if route.request.resource_type in ["image", "media"]
                    else route.continue_()
                    )

            try:
                # page.goto("https://www.google.com/search?q=tabitha+swatosh+tiktok")
                # sleep(1000)

                page.goto(link, wait_until=None)




                # page.goto("https://www.google.com/search?q=tabitha+swatosh+tiktok")
                # # page.goto('https://www.google.com/search?q=tabitha+swatosh+tiktok&btnI')

                # # # Input search query and press Enter
                # # page.fill('input[name="q"]', "Your Search Query Here")
                # # sleep(1)
                # # page.press('input[name="q"]', "Enter")
                # # sleep(1)
                # # # Wait for results to load
                # # page.wait_for_selector("h3")
                # # sleep(1)
                # # # Click the first search result link
                # # page.click("h3:first-child")
                # sleep(10)
                # links = page.locator('h3')
                # print(links.count())
                # import pkg_resources

                # playwright_version = pkg_resources.get_distribution("playwright").version
                # print(playwright_version)
                # for i in range(links.count()):
                #     print(links.nth(i))
                #     stuff = links.nth(i).inner_html()
                #     # pattern = r"url='(https?://[^']+)'"
                #     # match = re.search(pattern, str(links.nth(i)))
                #     # url = ''
                #     # if match:
                #     #     url = match.group(1)
                #     #     print(url)
                #     # else:
                #     #     print("No URL found")
                #     # if 'tabitaswatosh' in url:
                #     #     # print(links.nth(i).url)
                #     #     input('good?')
                #     #     links.nth(i).click()
                #     if '@tabithaswatosh' in stuff:
                #         print("BOOOOO")
                #         print(stuff)
                #         links.nth(i).click()
                #         break
                # # sleep(10000)


                # # page.goto(link, wait_until=None)
                # # sleep(2)
                # # page.reload()
                # sleep(3)
                page.wait_for_selector("#SIGI_STATE", state="attached")
                content = page.content()


                data = content.split(
                    '<script id="SIGI_STATE" type="application/json">'
                )[1].split("</script>")[0]

                if "LoginContextModule" in data:
                    warnings.warn(
                        "Redirected to a login page. Trying again...",
                        category=TikTokAPIWarning,
                        stacklevel=2,
                    )
                    sent_to_login = SentToLoginResponse.model_validate_json(data)
                    page.goto(
                        sent_to_login.login_context_module.redirect_url, wait_until=None
                    )
                    page.wait_for_selector("#SIGI_STATE", state="attached")
                    content = page.content()
                    data = content.split(
                        '<script id="SIGI_STATE" type="application/json">'
                    )[1].split("</script>")[0]

                page.close()

                extracted = self._extract_and_dump_data(data, data_model)
            except (ValidationError, IndexError) as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                page.close()
                continue
            except TimeoutError:
                warnings.warn(
                    "Reached navigation timeout. Retrying...",
                    category=TikTokAPIWarning,
                    stacklevel=2,
                )
                page.close()
                continue
            break
        else:
            raise TikTokAPIError(
                f"Data scraping unable to complete in {self.navigation_timeout / 1000}s "
                f"(retries: {self.navigation_retries})"
            )

        return extracted

    def _extract_and_dump_data(self, data: str, data_model: Type[_DataModelT]):
        if self.data_dump_file:
            with open(
                f"{self.data_dump_file}.{data_model.__name__}.json",
                "w+",
                encoding="utf-8",
            ) as f:
                j = json.loads(data)
                json.dump(j, f, indent=2)

        parsed = data_model.model_validate_json(data)
        return parsed

    def _extract_challenge_from_response(
        self,
        response: ChallengePage,
    ):
        if response.status_code:
            raise TikTokAPIError(
                f"Error in challenge extraction: status code {response.status_code} "
                f"({ERROR_CODES[response.status_code]})"
            )
        challenge = response.challenge_info.challenge
        challenge.stats = response.challenge_info.stats
        challenge._api = self

        return challenge

    def _extract_user_from_response(
        self,
        response: UserResponse,
    ):
        if response.user_page.status_code:
            raise TikTokAPIError(
                f"Error in user extraction: status code {response.user_page.status_code} "
                f"({ERROR_CODES[response.user_page.status_code]})"
            )
        name, user = list(response.user_module.users.items())[0]
        
        user.stats = response.user_module.stats[name]
        user._api = self

        return user

    def _extract_video_from_response(
        self,
        response: VideoPage,
    ):
        if response.status_code:
            raise TikTokAPIError(
                f"Error in video extraction: status code {response.status_code} "
                f"({ERROR_CODES[response.status_code]})"
            )
        video = response.item_info.video
        video._api = self

        return video


__all__ = ["TikTokAPI"]
