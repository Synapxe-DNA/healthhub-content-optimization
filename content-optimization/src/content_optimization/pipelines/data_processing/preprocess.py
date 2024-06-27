import re
import unicodedata

from bs4 import BeautifulSoup


class HTMLExtractor:
    """
    A class to extract and process various elements from HTML content using BeautifulSoup.

    Attributes:
        soup (BeautifulSoup): A BeautifulSoup object.
    """

    def __init__(self, html_content):
        """
        Initializes the HTMLExtractor with the given HTML content.

        Args:
            html_content (str): The HTML content to be processed.
        """
        self.soup = self.preprocess_html(html_content)

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Cleans the given text by normalizing Unicode characters,
        replacing problematic characters, and removing multiple whitespace.

        Args:
            text (str): The input text to be cleaned.

        Returns:
            str: The cleaned text with normalized Unicode characters,
                problematic characters replaced, and multiple whitespace
                replaced with a single space.
        """
        # Normalize Unicode characters
        text = unicodedata.normalize("NFKD", text)

        # Use ASCII encoding to handle special symbols e.g. copyright \xa9
        text = text.encode("ascii", "ignore").decode("utf-8")

        # Replace common problematic characters
        text = text.replace("\xa0", " ")  # non-breaking space
        text = text.replace("\u200b", "")  # zero-width space
        text = text.replace("\u2028", "\n")  # line separator
        text = text.replace("\u2029", "\n")  # paragraph separator

        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def preprocess_html(cls, html_content: str) -> BeautifulSoup:
        """
        Preprocesses the HTML content using BeautifulSoup and replaces <br> tags with newlines.

        Args:
            html_content (str): The HTML content to preprocess.

        Returns:
            BeautifulSoup: The BeautifulSoup object containing the parsed HTML content.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all <br> tags and replace them with newline
        for br in soup.find_all("br"):
            br.replace_with("\n")

        return soup

    def extract_related_sections(self) -> list[str]:
        """
        Extracts related sections from the HTML content.

        Returns:
            list[str]: A list of related sections as cleaned text.
        """
        related_sections = []
        read_these_next_ul = None
        # Extract "Related:" sections and "Read these next:" items
        for tag in self.soup.find_all(["p", "ul"]):
            if tag.name == "p" and tag.find("strong"):
                if "Related:" in tag.text:
                    related_sections.append(
                        re.sub(r"Related: ", "", self.clean_text(tag.text))
                    )
                elif "Read these next:" in tag.text:
                    read_these_next_ul = tag.find_next_sibling("ul")
            elif tag == read_these_next_ul:
                for li in tag.find_all("li"):
                    related_sections.append(self.clean_text(li.text))

        return related_sections

    def extract_text(self) -> str:
        """
        A function to extract cleaned text from HTML using BeautifulSoup

        Returns:
            str: cleaned text as string
        """

        # Unwrap if the HTML content is contained in a div
        if self.soup.div is not None:
            self.soup.div.unwrap()

        # Extract the main content
        content = []
        for tag in self.soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "div", "p", "ul", "ol"]
        ):
            if tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                # Provide paragraphing between key headers
                content.append("\n")
                content.append(self.clean_text(tag.text))

            elif tag.name == "p":
                # Remove all em tags
                for em in tag.find_all("em"):
                    em.extract()
                # Get the remaining text
                text = tag.get_text()
                # Remove sentences about HealthHub app, Google Play, and Apple Store
                if not re.search(
                    r"(HealthHub app|Google Play|Apple Store|Parent Hub)", text
                ):
                    if tag.find("strong"):
                        if "Related:" in tag.text:
                            text = self.clean_text(tag.text)
                            content.append(re.sub(r"\n", " ", text))
                        elif "Read these next:" in tag.text:
                            content.append(self.clean_text(tag.text))
                    else:
                        content.append(self.clean_text(text))
            # For unordered lists
            elif (
                tag.name == "ul" and tag.parent.name == "div"
            ):  # not "ul" so we avoid duplicates
                for li in tag.find_all("li"):
                    content.append("- " + self.clean_text(li.text))
            # For ordered lists
            elif tag.name == "ol":
                for i, li in enumerate(tag.find_all("li")):
                    content.append(f"{i + 1}. " + self.clean_text(li.text))
            # For texts within div
            elif tag.name == "div":
                content.append(self.clean_text(tag.text))

            content.append("")  # Add a blank line after each element

        # Remove empty strings from content
        content = [c for c in content if c]

        # Replace double newlines with single newlines and strip whitespace
        processed_text = "\n".join(content).replace("\n\n", "\n").strip()

        # # Edge case - HTML content contained in div tags
        # if processed_text.strip() == "":
        #     content = []
        #     # Unwrap if the HTML content is contained in a div
        #     if self.soup.div is not None:
        #         self.soup.div.unwrap()
        #         # For texts within div
        #         for tag in self.soup.find_all("div"):
        #             if tag.name == "div":
        #                 content.append(self.clean_text(tag.text))

        #         # Replace double newlines with single newlines and strip whitespace
        #         processed_text = "\n".join(content).replace("\n\n", "\n").strip()

        return processed_text

    def extract_links(self) -> list[tuple[str, str]]:
        """
        Extracts all links from the HTML content.

        Returns:
            list[tuple[str, str]]: A list of tuples containing the link text and URLs.
        """
        url_records = []

        # Extract title/text and links from anchor tags
        for link in self.soup.find_all("a"):
            url = link.get("href")
            text = link.get("title") or link.get_text()
            record = text, url
            url_records.append(record)

        return url_records

    def extract_headers(self) -> list[tuple[str, str]]:
        """
        Extracts headers from the HTML content.

        Returns:
            list[tuple[str, str]]: A list of tuples containing the header text and tag names.
        """
        headers = []

        for title in self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            tag = title.name
            text = title.get_text()
            record = text, tag
            headers.append(record)

        return headers
