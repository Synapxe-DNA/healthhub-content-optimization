import re
import unicodedata

from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
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


def extract_content(
    html_content: str,
) -> tuple[list[str], str, list[tuple[str, str]], list[tuple[str, str]]]:
    """
    A function to extract content from HTML using BeautifulSoup
    and clean the extracted content for further processing.

    Args:
        html_content (str): The HTML content to extract text from.

    Returns: tuple[list[str], str, list[tuple[str, str]], list[tuple[str, str]]]:
        A tuple containing a list of related sections, cleaned main content, links and headers
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <br> tags and replace them with newline
    for br in soup.find_all("br"):
        br.replace_with("\n")

    related_sections = extract_related_sections(soup)
    processed_text = extract_text(soup)
    links = extract_links(soup)
    headers = extract_headers(soup)

    return related_sections, processed_text, links, headers


def extract_related_sections(soup: BeautifulSoup) -> list[str]:
    """
    A function to extract related sections as cleaned text from HTML using BeautifulSoup

    Args:
        soup: A BeautifulSoup object containing the HTML content to extract text from.

    Returns:
        list[str]: A list of related sections as string
    """
    related_sections = []
    read_these_next_ul = None
    # Extract "Related:" sections and "Read these next:" items
    for tag in soup.find_all(["p", "ul"]):
        if tag.name == "p" and tag.find("strong"):
            if "Related:" in tag.text:
                related_sections.append(re.sub(r"Related: ", "", clean_text(tag.text)))
            elif "Read these next:" in tag.text:
                read_these_next_ul = tag.find_next_sibling("ul")
        elif tag == read_these_next_ul:
            for li in tag.find_all("li"):
                related_sections.append(clean_text(li.text))

    return related_sections


def extract_text(soup: BeautifulSoup) -> str:
    """
    A function to extract cleaned text from HTML using BeautifulSoup

    Args:
        soup: A BeautifulSoup object containing the HTML content to extract text from.

    Returns:
        str: cleaned text as string
    """
    # Extract the main content
    content = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol"]):
        if tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Provide paragraphing between key headers
            content.append("\n")
            content.append(clean_text(tag.text))

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
                        text = clean_text(tag.text)
                        content.append(re.sub(r"\n", " ", text))
                    elif "Read these next:" in tag.text:
                        content.append(clean_text(tag.text))
                else:
                    content.append(clean_text(text))
        # For unordered lists
        elif (
            tag.name == "ul" and tag.parent.name == "div"
        ):  # not "ul" so we avoid duplicates
            for li in tag.find_all("li"):
                content.append("- " + clean_text(li.text))
        # For ordered lists
        elif tag.name == "ol":
            for i, li in enumerate(tag.find_all("li")):
                content.append(f"{i + 1}. " + clean_text(li.text))

        content.append("")  # Add a blank line after each element

    # Remove empty strings from content
    content = [c for c in content if c]

    # Replace double newlines with single newlines and strip whitespace
    processed_text = "\n".join(content).replace("\n\n", "\n").strip()

    # Edge case - HTML content contained in div tags
    if processed_text.strip() == "":
        content = []
        # Unwrap if the HTML content is contained in a div
        if soup.div is not None:
            soup.div.unwrap()
            # For texts within div
            for tag in soup.find_all("div"):
                if tag.name == "div":
                    content.append(clean_text(tag.text))

            # Replace double newlines with single newlines and strip whitespace
            processed_text = "\n".join(content).replace("\n\n", "\n").strip()

    return processed_text


def extract_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """
    A function to extract links from HTML using BeautifulSoup

    Args:
        soup: A BeautifulSoup object containing the HTML content to extract text from.

    Returns:
        list[tuple[str, str]]: A list containing a tuple of anchor text and urls
    """
    url_records = []

    # Extract title/text and links from anchor tags
    for link in soup.find_all("a"):
        url = link.get("href")
        text = link.get("title") or link.get_text()
        record = text, url
        url_records.append(record)

    return url_records


def extract_headers(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """
    A function to extract headers as cleaned text from HTML using BeautifulSoup

    Args:
        soup: A BeautifulSoup object containing the HTML content to extract text from.

    Returns:
        list[tuple[str, str]]: A list containing a tuple of header text and tag
    """
    headers = []

    for title in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        tag = title.name
        text = title.get_text()
        record = text, tag
        headers.append(record)

    return headers
