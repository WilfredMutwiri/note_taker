from pypdf import PdfReader


def extract_text(file) -> str:
    """Extract plain text from an uploaded PDF file object.

    Only reads embedded text — scanned/image-only PDFs will yield an empty
    string, which the caller treats as "nothing to summarize".
    """
    reader = PdfReader(file)
    pages = [page.extract_text() or '' for page in reader.pages]
    return '\n\n'.join(pages).strip()
