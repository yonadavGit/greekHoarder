import requests
import requests_cache
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from ebook_utils import create_interlinear_epub
from tqdm import tqdm
requests_cache.install_cache('my_perseus_cache', expire_after=3600*24*100)
import re
import urllib.parse



def parse_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all():
        if tag.name in ["p", "br", "ul", "ol", "li", "b", "strong"]:
            continue  # Keep these tags
        tag.unwrap()  # Remove all other tags but keep their content

    return str(soup)


# def parse_response(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     raw_text = soup.get_text()
#     return raw_text
def fetch_text_from_ref(ref):
    base_url = 'https://www.perseus.tufts.edu/hopper/loadquery?doc='
    full_url = base_url + ref
    response = requests.get(full_url)
    if response.status_code == 200 and not "An Error Occurred" in response.text:
        # print(parse_response(response.text))
        return parse_html(response.text)
    else:
        return None

def extract_refs_and_texts(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    xml_content = response.content

    root = ET.fromstring(xml_content)

    refs_list = []

    for elem in tqdm(root.findall('.//*[@ref]'), desc="scraping refs"):
        ref_value = elem.get('ref')
        text_content = fetch_text_from_ref(ref_value)
        if text_content:
            refs_list.append({'ref': ref_value, 'text': text_content})

    return refs_list
def get_suffix_after_third_colon(s: str) -> str:
    s = s.replace("%3A", ":")  # Normalize URL-encoded colons
    parts = s.split(":", 3)  # Split into at most 4 parts
    return parts[3] if len(parts) > 3 else ""

def filter_matching_suffixes(list1, list2):
    """Removes dicts from both lists if their suffix has no match in the other list."""
    # Extract suffixes from both lists
    suffixes1 = {get_suffix_after_third_colon(d["ref"]) for d in list1}
    suffixes2 = {get_suffix_after_third_colon(d["ref"]) for d in list2}

    # Find common suffixes
    common_suffixes = suffixes1 & suffixes2

    # Filter lists based on common suffixes
    filtered_list1 = [d for d in list1 if get_suffix_after_third_colon(d["ref"]) in common_suffixes]
    filtered_list2 = [d for d in list2 if get_suffix_after_third_colon(d["ref"]) in common_suffixes]

    return filtered_list1, filtered_list2
if __name__ == '__main__':
    # Example usage
    source_xml_url = 'https://www.perseus.tufts.edu/hopper/xmltoc?doc=Perseus%3Atext%3A1999.01.0135%3Abook%3D1%3Acard%3D1'
    translation_xml_url = "https://www.perseus.tufts.edu/hopper/xmltoc?doc=Perseus%3Atext%3A1999.01.0136%3Abook%3D2%3Acard%3D177"
    source = extract_refs_and_texts(source_xml_url)
    translation = extract_refs_and_texts(translation_xml_url)
    # source, translation = filter_matching_suffixes(source, translation)
    source = [tuple(d.values()) for d in source]
    translation = [tuple(d.values()) for d in translation]
    create_interlinear_epub(source, translation, title="Odyssey Greek English Interlinear", output_filename="odyssey_interlinear.epub")
