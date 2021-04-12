from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import re
import csv

end_of_results_text = "End of Results"
page_chunk_size = 10


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.

    Taken from:
    https://stackoverflow.com/a/312464
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_title_and_link(element):
    """
    Gets the title and the link to a page from the search results.

    Returns: tuple of the format: `(title, link)`
    """
    link = element.find_element_by_css_selector('a').get_attribute("href")
    title = element.find_element_by_css_selector(
        'span').get_attribute("innerHTML")
    return (title, link)


def seperated_number_to_int(number):
    """
    Turns a number with seperating commas (eg. `198,220`) into an int.
    """
    no_commas = ''.join([c for c in number if c != ','])
    return int(no_commas)


def get_keywords():
    with open("keywords.csv") as f:
        return f.read().split(',')


class Scraper:
    def __init__(self):
        # Sets the browser language to English.
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--lang=en-us")

        # Opens the browser.
        # Make sure you have a chromedriver.exe that matches you Chrome version in the same directory.
        self.driver = webdriver.Chrome(options=self.options)

        # The triggeredResetProfileSettings tab opened each time, fix that worked for me:
        # https://support.leapwork.com/hc/en-us/articles/115001642052-Chrome-browser-is-opening-Settings-as-the-default-tab-and-asking-to-reset-chrome-settings

    def run(self, keywords):
        """
        Runs the search and writes the results to `results.csv`.

        CAUTION: Will overwrite any existing `results.csv` file.
        """

        search_results = self.search_keywords(keywords)
        process_results = self.process_pages(search_results)
        self.driver.quit()
        self.write_results(process_results)

    def write_results(self, results) -> None:
        """
        Writes the results to a file `results.csv`.

        Takes `results` as a list of tuples in the format `(title, link, likes, follows)`.

        Results are written to the file in four columns: `Title`, `Link`, `Likes`, and `Follows`.

        CAUTION: Will overwrite any existing `results.csv` file.
        """

        with open("results.csv", 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Link", "Likes", "Follows"])
            writer.writerows(results)

    def process_pages(self, pages) -> list:
        """
        Checks the number of likes and follows each pages has.

        Takes `pages` as a list of tuples in the format `(title, link)`.

        Returns a list of tuples in the format `(title, link, likes, follows)` containing details
        about the pages.
        """

        # In order for Facebook to show me the pages without having to log in,
        # I need to open a new browser every 10 pages or so.
        # Does not fully work, but gets more information than not splitting it up.

        results = []

        for chunk in chunks(pages, 10):
            for page in chunk:
                results.append(self.process_page(page))

            self.driver.quit()
            self.driver = webdriver.Chrome(options=self.options)

        return results

    def process_page(self, page) -> tuple:
        """
        Checks the number of likes and follows the page has.

        Takes `page` as a tuple in the format `(title, link)`.

        Returns a tuple in the format `(title, link, likes, follows)` containing details about the page.
        """
        # Go to the page.
        self.driver.get(page[1])

        # Get the page source.
        page_source = self.driver.find_element_by_xpath(
            "//*").get_attribute("outerHTML")

        # Extract the number of Likes and Follows from the source using RegEx.
        likes_search = re.search(
            r"<div>([^\s]+) people like this", page_source)
        follows_search = re.search(
            r"<div>([^\s]+) people follow this", page_source)

        # Sometimes Facebook requires us to log in to see a page,
        # in that case we just skip the page and write "Could Not Access" in the likes and follows.
        if "login" in self.driver.current_url:
            likes = "Could Not Access"
            follows = "Could Not Access"

        else:
            # Likes and Follows come in a seperated format (eg. `198,220`),
            # so I turn them into ints.
            # Additionally, sometimes, when there are no likes or follows at all, it doesn't say
            # "0 people follow/like this", so the match fails.
            if likes_search:
                likes = seperated_number_to_int(likes_search.group(1))
            else:
                likes = 0

            if follows_search:
                follows = seperated_number_to_int(follows_search.group(1))
            else:
                follows = 0

        return (page[0], page[1], likes, follows)

    def search_keywords(self, keywords) -> list:
        """
        Searches the Facebook Directory for all the keywords (not all at once).

        Returns a list of tuples in the format `(title, link)` containing
        every page found that had the searched keyword in its title.
        """

        pages = []
        for keyword in keywords:
            pages = [*pages, *(self.search_keyword(keyword))]

        return pages

    def search_keyword(self, keyword) -> list:
        """
        Searches the Facebook Directory for the keyword.

        Returns a list of tuples in the format `(title, link)` of all the pages
        from the search that contain the keyword in their title.
        """

        self.driver.get(
            f"https://www.facebook.com/public?query={keyword}&type=pages")

        # Scroll all the way down by selecting the email field and pressing PageDown.
        email_field = self.driver.find_element_by_css_selector(
            'input[type="email"]')

        # While there's no end of results text in the page source, send PageDown (scroll down).
        while end_of_results_text not in self.driver.find_element_by_xpath(
                "//*").get_attribute("outerHTML"):
            email_field.send_keys(Keys.PAGE_DOWN)

        # Done scrolling.

        # A list of all the results on the page.
        feed = self.driver.find_elements_by_css_selector(
            'div[data-testid="browse-result-content"]')

        pages_unfiltered = [get_title_and_link(p) for p in feed]

        # We get a lot of irrelevant Pages that don't contain the keyword in the title,
        # so I'll filter just to the pages that do.
        pages_filtered = list(filter(lambda p: keyword.lower()
                                     in p[0].lower(), pages_unfiltered))

        return pages_filtered


def main():
    scraper = Scraper()
    scraper.run(get_keywords())


if __name__ == "__main__":
    main()
