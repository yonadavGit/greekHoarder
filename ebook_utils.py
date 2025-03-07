from importlib.metadata import metadata

from ebooklib import epub
import re
import urllib.parse


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
        source_meta = urllib.parse.unquote(source_meta)
        translation_meta, translation_text = translation_tuple
        translation_meta = urllib.parse.unquote(translation_meta)

        # if source_meta != translation_meta:
        #     raise ValueError(f"Metadata mismatch: {source_meta} vs {translation_meta}")

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