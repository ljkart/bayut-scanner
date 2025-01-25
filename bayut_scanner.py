import requests
from bs4 import BeautifulSoup
import time
import re
import random
from typing import List, Dict, Optional
from sematics_matcher import analyze_property_description
import traceback


class BayutScraper:
    def __init__(self):
        self.base_url = "https://www.bayut.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Make a GET request with rate limiting and return BeautifulSoup object"""
        try:
            # Random delay between requests (1-3 seconds)
            time.sleep(random.uniform(1, 3))

            print(f"Fetching URL: {url}")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()

            # Debug response
            print(f"Response status: {response.status_code}")
            print(f"Response content length: {len(response.text)}")

            soup = BeautifulSoup(response.text, "html.parser")

            return soup

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None

    def _parse_property(self, prop_elem) -> Optional[Dict]:
        """Parse individual property listing"""
        property_data = {}
        property_base_url = "https://www.bayut.com"
        link = prop_elem.find("a")
        if link:
            property_data["url"] = f"{property_base_url}{link["href"]}"
            property_data["title"] = link["title"]

        # get picture
        picture_tag = prop_elem.find("picture", class_="a659dd2e")
        if picture_tag:
            property_data["image_url"] = picture_tag.find("img").get("src")

        # Get Location
        location_tag = prop_elem.find("h3", class_="_4402bd70")
        if location_tag:
            property_data["location"] = location_tag.string
        # price data
        property_data["price"] = self._get_price_info(prop_elem)

        # property description filter
        property_data["is_bills_included"] = self._is_bills_included(
            property_data["url"]
        )

        return property_data

    def _get_price_info(self, prop_elem):
        price_tag = prop_elem.find("div", class_="_2923a568")
        if not price_tag:
            return ""
        return price_tag.find("span", class_="dc381b54").text
        # return {
        #     "currency": price_tag.find("span", class_="_06f65f02").text,
        #     "price": price_tag.find("span", class_="dc381b54").text,
        #     "frequency": prop_elem.find("span", class_="fc7b94b8").text,
        # }

    def _is_bills_included(self, property_url):
        response = requests.get(property_url, timeout=10)
        soup_ = BeautifulSoup(response.text, "html.parser")
        details_tag = soup_.find("span", class_="_3547dac9")
        if not details_tag:
            return False
        property_desc = details_tag.get_text(strip=True)
        # now sematically check if the description contain word like
        # electricty and water included
        match = analyze_property_description(property_desc)
        if match["has_free_utilities"]:
            return True

        return False

    def _get_next_page(self, search_url):
        current_page = re.search(r"page-(\d+)", search_url)
        page_split = search_url.split("/")
        if current_page is None:
            return f"{"/".join(page_split[:-1])}/page-2/{page_split[-1]}"
        else:
            return f"{"/".join(page_split[:-2])}/page-{int(current_page.group(1))+1}/{page_split[-1]}"

    def search_properties(
        self,
        location: str,
        min_price: int,
        max_price: int,
        rooms: str,
        baths: str = 1,
        check_bills_included: bool = True,
        max_page_count: int = 1,
    ) -> List[Dict]:
        """Search properties with given filters"""
        results = []
        location_parts = location.lower().split(",")
        if len(location_parts) != 2:
            raise Exception(
                "Location must be in format: 'emirate, area' (e.g., 'abu dhabi, khalifa city')"
            )

        emirate = location_parts[0].strip().replace(" ", "-")
        area = location_parts[1].strip().replace(" ", "-")

        search_url = f"{self.base_url}/to-rent/{rooms}-bedroom-property/{emirate}/{area}/"
        if max_price == 0:
            raise Exception(
                "Max price shouldnt be 0, give higher values eg: 45000"
            )

        search_url = f"{search_url}?price_min={min_price}?price_max={max_price}?baths_in={baths}"
        page_cnt = 1

        while search_url:
            try:

                print(
                    f"Current page URL: {search_url}"
                )  # Debug URL construction

                soup = self._get_page(search_url)
                if not soup:
                    return []

                # Find all property listings
                properties = []
                class_name = "a37d52f0"
                elements = soup.find_all(["article", "li"], class_=class_name)
                if elements:
                    properties.extend(elements)
                    print(
                        f"Found {len(elements)} properties with class '{class_name}'"
                    )

                if not properties:
                    print(f"No properties found on page: {search_url}")
                    return []

                for prop in properties:
                    try:
                        property_data = self._parse_property(prop)
                        if (
                            int(property_data["price"].replace(",", ""))
                            > max_price
                        ):
                            continue
                        if not check_bills_included:
                            results.append(property_data)
                        else:
                            if property_data["is_bills_included"]:
                                results.append(property_data)

                    except Exception as e:
                        print(f"Failed to parse property")
                        traceback.print_exc()
                        continue

                if page_cnt >= max_page_count:
                    break
                # get next page and continue search
                search_url = self._get_next_page(search_url)
                page_cnt += 1

            except Exception as e:
                print(f"Search failed: {str(e)}")
                return []

        return results
