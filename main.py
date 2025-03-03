import requests
import requests_cache
from ebooklib import epub
import re
import subprocess, os

requests_cache.install_cache('my_cache', expire_after=3600*24*100)  # Cache expires after 1 hour
from bs4 import BeautifulSoup


def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_text = soup.get_text()
    return raw_text

def query_api(base_url, path, node_names):
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
            return {"exists": True, "data": (path_string, response.text)}
        else:
            return {"exists": False, "data": None}
    except requests.RequestException:
        # Network error, timeout, etc.
        return {"exists": False, "data": None}

def traverse_book(base_url, node_names):
    depth = len(node_names)
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
            result["data"] = (result["data"][0], parse_response(result["data"][1]))
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


def parse_metadata(metadata):
    """Parses dynamic metadata and formats it into a readable header and ID."""
    parts = dict(re.findall(r'(\w+)=(\w+)', metadata))
    header = ", ".join([f"{k.capitalize()} {v}" for k, v in parts.items()])
    element_id = "_".join([f"{k}{v}" for k, v in parts.items()])
    return header, element_id

def create_interlinear_epub(source_tuples, translation_tuples, output_filename="result.epub", title="Interlinear Text"):
    if len(source_tuples) != len(translation_tuples):
        raise ValueError("Source and translation lists must have the same length.")

    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('en')
    # book.add_author('Yonadav')

    chapters = []
    for source_tuple, translation_tuple in zip(source_tuples, translation_tuples):
        source_meta, source_text = source_tuple
        translation_meta, translation_text = translation_tuple

        if source_meta != translation_meta:
            raise ValueError(f"Metadata mismatch: {source_meta} vs {translation_meta}")

        header, element_id = parse_metadata(source_meta)

        chapter = epub.EpubHtml(title=header, file_name=f'{element_id}.xhtml', lang='en')
        chapter.content = f"""
            <h2>{header}</h2>
            <p id="source-{element_id}">
                {source_text}
            </p>
            <p id="trans-{element_id}" style="color: green;">
                {translation_text}
            </p>
        """
        book.add_item(chapter)
        chapters.append(chapter)

    # Define table of contents
    book.toc = [epub.Link(ch.file_name, ch.title, ch.file_name) for ch in chapters]

    # Add navigation and spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ['nav'] + chapters

    # Write the EPUB file
    epub.write_epub(output_filename, book, {})


    print(f"EPUB created: {output_filename}")



if __name__ == '__main__':
    # main_text_perseus_id = "1999.01.0207"
    # secondary_text_perseus_id = "1999.01.0208"

    main_text_perseus_id = "1999.01.0169"
    secondary_text_perseus_id = "1999.01.0170"
    base_url = f"https://www.perseus.tufts.edu/hopper/loadquery?doc=Perseus:text:{main_text_perseus_id}"
    source = traverse_book(base_url,["text", "section"])
    base_url = f"https://www.perseus.tufts.edu/hopper/loadquery?doc=Perseus:text:{secondary_text_perseus_id}"
    translation = traverse_book(base_url, ["text", "section"])
    print(len(source) == len(translation))
    create_interlinear_epub(source, translation, title="Euthyphro, Apology, Crito, Phaedo Interlinear")



