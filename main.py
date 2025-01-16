import requests
import requests_cache

requests_cache.install_cache('my_cache', expire_after=3600)  # Cache expires after 1 hour
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

def query_api(base_url, path, node_names):
    """
    Queries the API at base_url for the given book_name and path.
    Returns a dictionary with keys:
      - 'exists': bool indicating whether the resource exists
      - 'data': the API response data if exists, else None
    """

    path_string = ""
    for node_name, node_path_number in zip(node_names, path):
        path_string += f"{node_name}={node_path_number}:"
    path_string = path_string[:-1]
    url = f"{base_url}:{path_string}"

    try:
        # Make the HTTP request
        response = requests.get(url, timeout=5)
        # If the status code indicates success, we consider the line 'exists'
        if response.status_code == 200:
            print(url)
            return {"exists": True, "data": response.text}
        else:
            return {"exists": False, "data": None}
    except requests.RequestException:
        # Network error, timeout, etc.
        return {"exists": False, "data": None}

def traverse_book(base_url, depth, node_names):
    if depth < 1:
        raise ValueError("depth must be at least 1.")

    all_lines = []
    path = [1] * depth  # Initialize the path with the specified depth

    depth_to_update = depth - 1
    while True:
        if depth_to_update < 0:
            break
        result = query_api(base_url, path, node_names)

        if result["exists"]:
            all_lines.append(result["data"])
            depth_to_update = depth - 1
            path[depth_to_update] += 1
        else:
            depth_to_update = depth_to_update - 1
            for i in range(0,len(path)):
                if i == depth_to_update:
                    path[i] += 1
                if i > depth_to_update:
                    path[i] = 1
                else:
                    continue
    return all_lines




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
    base_url = "https://www.perseus.tufts.edu/hopper/loadquery?doc=Perseus:text:1999.01.0207"
    lines = traverse_book(base_url, 3, ["book", "chapter", "section"])
    print(lines)




