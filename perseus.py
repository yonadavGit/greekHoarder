import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup




def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return raw_text
def fetch_text_from_ref(ref):
    base_url = 'https://www.perseus.tufts.edu/hopper/loadquery?doc='
    full_url = base_url + ref
    response = requests.get(full_url)
    if response.status_code == 200 and not "An Error Occurred" in response.text:
        # print(parse_response(response.text))
        return parse_response(response.text)
    else:
        return None

def extract_refs_and_texts(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    xml_content = response.content

    root = ET.fromstring(xml_content)

    refs_list = []

    for elem in root.findall('.//*[@ref]'):
        ref_value = elem.get('ref')
        text_content = fetch_text_from_ref(ref_value)
        if text_content:
            refs_list.append({'ref': ref_value, 'text': text_content})

    return refs_list

if __name__ == '__main__':
    # Example usage
    xml_url = 'https://www.perseus.tufts.edu/hopper/xmltoc?doc=Perseus%3Atext%3A1999.01.0177%3Atext%3DProt.%3Asection%3D309a'
    refs_and_texts = extract_refs_and_texts(xml_url)
    for item in refs_and_texts:
        print(f"Ref: {item['ref']}, Text: {item['text'][:100]}...")