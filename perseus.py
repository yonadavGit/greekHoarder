import requests
import requests_cache
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from ebook_utils import create_interlinear_epub
from tqdm import tqdm
requests_cache.install_cache('my_perseus_cache', expire_after=3600*24*100)


def parse_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all():
        if tag.name in ["p", "br", "ul", "ol", "li"]:
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

if __name__ == '__main__':
    # Example usage
    source_xml_url = 'https://www.perseus.tufts.edu/hopper/xmltoc?doc=Perseus%3Atext%3A1999.01.0169%3Atext%3DCrito%3Asection%3D43a'
    translation_xml_url = "https://www.perseus.tufts.edu/hopper/xmltoc?doc=Perseus%3Atext%3A1999.01.0170%3Atext%3DCrito%3Asection%3D43a"
    source = extract_refs_and_texts(source_xml_url)
    source = [tuple(d.values()) for d in source]
    translation = extract_refs_and_texts(translation_xml_url)
    translation = [tuple(d.values()) for d in translation]
    create_interlinear_epub(source, translation, title="Crito Greek English Interlinear", output_filename="crito_interlinear.epub")
