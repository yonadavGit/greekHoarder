import requests
from bs4 import BeautifulSoup

def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return raw_text

def query_perseus(text_id, book, chapter, section, num):
    base_url = "https://www.perseus.tufts.edu/hopper/loadquery"
    params = {
        "doc": f"Perseus:text:{text_id}",
        "book": book,
        "chapter": chapter,
        "section": section,
        "num": num
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return parse_response(response.text)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_text_perseus_id = "1999.01.0207"
    secondary_text_perseus_id = "1999.01.0208"
    doc = main_text_perseus_id
    book = "1"
    chapter = "1"
    section = "20"
    num = 1
    text = query_perseus(main_text_perseus_id, book, chapter, section, num)
    print(text)

