import requests
from bs4 import BeautifulSoup

def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return raw_text

def query_perseus(text_id, book, chapter, section):
    base_url = "https://www.perseus.tufts.edu/hopper/loadquery"
    # params = {
    #     "doc": f"Perseus:text:{text_id}",
    #     "book": book,
    #     "chapter": chapter,
    #     "section": section,
    # }
    response = requests.get(f"{base_url}?doc=Perseus:text:{text_id}:book={book}:chapter={chapter}:section={section}")
    response.raise_for_status()
    return parse_response(response.text)

class BookNavigator:
    def __init__(self):
        self.book = 1
        self.chapter = 1
        self.section = 1

    def next_section(self):
        self.section += 1

    def next_chapter(self):
        self.chapter += 1
        self.section = 1  # Reset section to 1 when moving to the next chapter

    def next_book(self):
        self.book += 1
        self.chapter = 1  # Reset chapter to 1 when moving to the next book
        self.section = 1  # Reset section to 1 when moving to the next book

    def as_dict(self):
        return {"book": self.book, "chapter":self.chapter, "section":self.section}


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_text_perseus_id = "1999.01.0207"
    secondary_text_perseus_id = "1999.01.0208"
    nav = BookNavigator()
    while True:
        try:
            text = query_perseus(main_text_perseus_id, nav.book, nav.chapter, nav.section)
            print(text)
            nav.next_section()
        except:
            try:
                nav.next_chapter()
                text = query_perseus(main_text_perseus_id, nav.book, nav.chapter, nav.section)
                print(text)
                nav.next_section()
            except:
                try:
                    nav.next_book()
                    text = query_perseus(main_text_perseus_id, nav.book, nav.chapter, nav.section)
                    print(text)
                    nav.next_section()
                except:
                    print("end")



