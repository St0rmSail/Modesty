"""Bounded local text extraction for private reading material."""

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile


class BookReadError(RuntimeError):
    """Raised when a reading file cannot be interpreted safely."""


@dataclass(frozen=True)
class BookText:
    title: str
    author: str
    sections: tuple[tuple[str, str], ...]
    truncated: bool = False

    @property
    def word_count(self) -> int:
        return sum(len(text.split()) for _, text in self.sections)


class _TextHTMLParser(HTMLParser):
    BLOCKS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.ignored += 1
        elif not self.ignored and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.ignored:
            self.ignored -= 1
        elif not self.ignored and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignored:
            self.parts.append(data)

    def text(self) -> str:
        return _clean_text("".join(self.parts))


def read_book(path: Path, max_characters: int = 8_000_000, max_pdf_pages: int = 500) -> BookText:
    """Read one supported private document without executing embedded content."""

    extension = path.suffix.casefold()
    if extension in {".txt", ".md"}:
        text = _decode_text(path.read_bytes())
        return _bounded(path.stem, "Unknown Author", (("Text", text),), max_characters)
    if extension in {".html", ".htm"}:
        parser = _TextHTMLParser()
        parser.feed(_decode_text(path.read_bytes()))
        return _bounded(path.stem, "Unknown Author", (("Document", parser.text()),), max_characters)
    if extension == ".docx":
        return _read_docx(path, max_characters)
    if extension == ".epub":
        return _read_epub(path, max_characters)
    if extension == ".pdf":
        return _read_pdf(path, max_characters, max_pdf_pages)
    raise BookReadError(f"Reading {extension or 'that format'} is not implemented yet.")


def _read_docx(path: Path, limit: int) -> BookText:
    try:
        with zipfile.ZipFile(path) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            core = _optional_xml(archive, "docProps/core.xml")
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
        raise BookReadError("The Word document container could not be read safely.") from error
    paragraphs = []
    for paragraph in document.iter():
        if _local(paragraph.tag) != "p":
            continue
        text = "".join(node.text or "" for node in paragraph.iter() if _local(node.tag) in {"t", "tab", "br"})
        if text.strip():
            paragraphs.append(text.strip())
    title = _xml_value(core, "title") or path.stem
    author = _xml_value(core, "creator") or "Unknown Author"
    return _bounded(title, author, (("Document", "\n\n".join(paragraphs)),), limit)


def _read_epub(path: Path, limit: int) -> BookText:
    try:
        with zipfile.ZipFile(path) as archive:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = next(node.attrib["full-path"] for node in container.iter() if _local(node.tag) == "rootfile")
            package = ET.fromstring(archive.read(rootfile))
            title = next((node.text or "" for node in package.iter() if _local(node.tag) == "title"), "").strip() or path.stem
            author = next((node.text or "" for node in package.iter() if _local(node.tag) == "creator"), "").strip() or "Unknown Author"
            manifest = {node.attrib.get("id", ""): node.attrib.get("href", "") for node in package.iter() if _local(node.tag) == "item"}
            spine = [node.attrib.get("idref", "") for node in package.iter() if _local(node.tag) == "itemref"]
            base = PurePosixPath(rootfile).parent
            sections = []
            for index, item_id in enumerate(spine, 1):
                href = manifest.get(item_id, "").split("#", 1)[0]
                if not href:
                    continue
                member = str(base / PurePosixPath(href))
                parser = _TextHTMLParser()
                parser.feed(_decode_text(archive.read(member)))
                text = parser.text()
                if text:
                    sections.append((f"Section {index}", text))
    except (OSError, KeyError, StopIteration, zipfile.BadZipFile, ET.ParseError) as error:
        raise BookReadError("The EPUB container could not be read safely.") from error
    if not sections:
        raise BookReadError("The EPUB contains no readable spine text.")
    return _bounded(title, author, tuple(sections), limit)


def _read_pdf(path: Path, limit: int, max_pages: int) -> BookText:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise BookReadError("PDF reading requires the project's pypdf dependency.") from error
    try:
        reader = PdfReader(path, strict=False)
        metadata = reader.metadata or {}
        title = str(metadata.get("/Title") or path.stem).strip()
        author = str(metadata.get("/Author") or "Unknown Author").strip()
        sections = []
        used = 0
        pages = min(len(reader.pages), max_pages)
        for index in range(pages):
            text = _clean_text(reader.pages[index].extract_text() or "")
            if not text:
                continue
            remaining = limit - used
            if remaining <= 0:
                break
            sections.append((f"Page {index + 1}", text[:remaining]))
            used += len(text[:remaining])
        truncated = len(reader.pages) > pages or used >= limit
    except Exception as error:
        raise BookReadError("The PDF text layer could not be read safely.") from error
    if not sections:
        raise BookReadError("The PDF has no readable text layer; it may require OCR later.")
    return BookText(title or path.stem, author or "Unknown Author", tuple(sections), truncated)


def _bounded(title: str, author: str, sections, limit: int) -> BookText:
    result = []
    used = 0
    truncated = False
    for heading, raw in sections:
        text = _clean_text(raw)
        if not text:
            continue
        remaining = limit - used
        if remaining <= 0:
            truncated = True
            break
        result.append((heading, text[:remaining]))
        used += len(text[:remaining])
        if len(text) > remaining:
            truncated = True
            break
    if not result:
        raise BookReadError("The document contains no readable text.")
    return BookText(title.strip() or "Untitled", author.strip() or "Unknown Author", tuple(result), truncated)


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise BookReadError("The document uses an unsupported text encoding.")


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _optional_xml(archive: zipfile.ZipFile, member: str):
    try:
        return ET.fromstring(archive.read(member))
    except (KeyError, ET.ParseError):
        return None


def _xml_value(root, local_name: str) -> str:
    if root is None:
        return ""
    return next(((node.text or "").strip() for node in root.iter() if _local(node.tag) == local_name), "")
