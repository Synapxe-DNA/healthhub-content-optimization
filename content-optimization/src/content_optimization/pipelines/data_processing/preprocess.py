import re
import unicodedata

from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    # Normalize Unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Replace common problematic characters
    text = text.replace("\xa0", " ")  # non-breaking space
    text = text.replace("\u200b", "")  # zero-width space
    text = text.replace("\u2028", "\n")  # line separator
    text = text.replace("\u2029", "\n")  # paragraph separator
    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <br> tags and replace them with newline
    for br in soup.find_all("br"):
        br.replace_with("\n")

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

    # Extract the main content
    content = []
    for tag in soup.find_all(["h2", "h3", "h4", "p", "ul", "ol"]):
        if tag.name in ["h2", "h3", "h4"]:
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
        # For ordred lists
        elif tag.name == "ol":
            for i, li in enumerate(tag.find_all("li")):
                content.append(f"{i + 1}. " + clean_text(li.text))

        content.append("")  # Add a blank line after each element

    # Remove empty strings from content
    content = [c for c in content if c]

    return related_sections, "\n".join(content)
