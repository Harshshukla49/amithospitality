import os
import re
import csv
from typing import List, Dict, Any, Optional

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract pages and text from PDF using PyMuPDF."""
    try:
        import pymupdf
        doc = pymupdf.open(file_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:
                pages.append({
                    "page_number": page_num + 1,
                    "title": f"Page {page_num + 1}",
                    "content": text
                })
        doc.close()
        return pages
    except Exception as e:
        return [{"page_number": 1, "title": "Raw PDF Fallback", "content": f"[PDF Extraction Error: {str(e)}]"}]

def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extract paragraphs and tables from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        sections = []
        current_heading = "Document Content"
        current_paragraphs = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            if p.style.name.startswith("Heading"):
                if current_paragraphs:
                    sections.append({
                        "page_number": 1,
                        "title": current_heading,
                        "content": "\n".join(current_paragraphs)
                    })
                    current_paragraphs = []
                current_heading = text
            else:
                current_paragraphs.append(text)

        if current_paragraphs:
            sections.append({
                "page_number": 1,
                "title": current_heading,
                "content": "\n".join(current_paragraphs)
            })

        # Also extract structured tables (menus, pricing tables)
        for t_idx, table in enumerate(doc.tables):
            rows_data = []
            for row in table.rows:
                row_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                if any(row_cells):
                    rows_data.append(" | ".join(row_cells))
            if rows_data:
                sections.append({
                    "page_number": 1,
                    "title": f"Table {t_idx + 1}",
                    "content": "\n".join(rows_data)
                })

        return sections if sections else [{"page_number": 1, "title": "General", "content": "Empty Document"}]
    except Exception as e:
        return [{"page_number": 1, "title": "DOCX Fallback", "content": f"[DOCX Extraction Error: {str(e)}]"}]

def extract_text_from_spreadsheet(file_path: str, is_xlsx: bool = True) -> List[Dict[str, Any]]:
    """Extract rows and sheets from XLSX or CSV into structured readable representations."""
    sections = []
    if is_xlsx:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                rows = list(sheet.iter_rows(values_only=True))
                if not rows or len(rows) < 1:
                    continue
                header = [str(col).strip() if col is not None else f"Column_{i+1}" for i, col in enumerate(rows[0])]
                sheet_lines = [f"### Sheet: {sheet_name}"]
                for row_idx, row in enumerate(rows[1:], start=2):
                    pairs = []
                    for h, val in zip(header, row):
                        if val is not None and str(val).strip():
                            pairs.append(f"{h}: {str(val).strip()}")
                    if pairs:
                        sheet_lines.append(f"Row {row_idx}: " + " | ".join(pairs))
                
                if len(sheet_lines) > 1:
                    sections.append({
                        "page_number": 1,
                        "title": f"Sheet: {sheet_name}",
                        "content": "\n".join(sheet_lines)
                    })
            return sections if sections else [{"page_number": 1, "title": "Empty Spreadsheet", "content": "No tabular data found."}]
        except Exception as e:
            pass

    # CSV or fallback
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return [{"page_number": 1, "title": "CSV", "content": "Empty CSV file"}]
            header = [c.strip() if c.strip() else f"Col_{i+1}" for i, c in enumerate(rows[0])]
            lines = ["### CSV Records:"]
            for r_idx, row in enumerate(rows[1:], start=2):
                pairs = [f"{h}: {val.strip()}" for h, val in zip(header, row) if val.strip()]
                if pairs:
                    lines.append(f"Record {r_idx}: " + " | ".join(pairs))
            return [{
                "page_number": 1,
                "title": "Tabular Data",
                "content": "\n".join(lines)
            }]
    except Exception as e:
        return [{"page_number": 1, "title": "Spreadsheet Error", "content": f"[Spreadsheet Extraction Error: {str(e)}]"}]

def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """Extract plain text or markdown with encoding fallbacks."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read().strip()
                return [{"page_number": 1, "title": "General Content", "content": content}]
        except Exception:
            continue
    return [{"page_number": 1, "title": "Error", "content": "Unable to decode text file."}]

def extract_document_content(file_path: str, file_type: str) -> List[Dict[str, Any]]:
    """Route document to specialized parser based on extension."""
    ft = file_type.upper()
    if ft == "PDF":
        return extract_text_from_pdf(file_path)
    elif ft in ["DOCX", "DOC"]:
        return extract_text_from_docx(file_path)
    elif ft in ["XLSX", "XLS"]:
        return extract_text_from_spreadsheet(file_path, is_xlsx=True)
    elif ft == "CSV":
        return extract_text_from_spreadsheet(file_path, is_xlsx=False)
    else:
        return extract_text_from_txt(file_path)

def chunk_text(
    sections: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 75
) -> List[Dict[str, Any]]:
    """
    Split extracted document sections into semantic chunks with token/word overlap.
    Preserves section title, page number, and sequential index.
    """
    chunks = []
    chunk_global_idx = 0

    for section in sections:
        title = section.get("title", "Section")
        page_num = section.get("page_number", 1)
        raw_content = section.get("content", "").strip()

        if not raw_content:
            continue

        # Split on natural paragraph or newline boundaries first
        paragraphs = re.split(r'\n{2,}', raw_content)
        current_chunk_words: List[str] = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            words = para.split()
            # If paragraph itself exceeds chunk_size, split by words
            if len(current_chunk_words) + len(words) > chunk_size:
                if current_chunk_words:
                    chunk_text_str = " ".join(current_chunk_words)
                    chunks.append({
                        "chunk_index": chunk_global_idx,
                        "title": title,
                        "page_number": page_num,
                        "content": f"[{title} | Page {page_num}]\n{chunk_text_str}",
                        "word_count": len(current_chunk_words),
                    })
                    chunk_global_idx += 1
                    # Keep overlap words
                    current_chunk_words = current_chunk_words[-chunk_overlap:] if chunk_overlap < len(current_chunk_words) else []

                # Now add words in slices
                while len(words) > chunk_size:
                    slice_words = words[:chunk_size]
                    chunk_text_str = " ".join(slice_words)
                    chunks.append({
                        "chunk_index": chunk_global_idx,
                        "title": title,
                        "page_number": page_num,
                        "content": f"[{title} | Page {page_num}]\n{chunk_text_str}",
                        "word_count": len(slice_words),
                    })
                    chunk_global_idx += 1
                    words = words[chunk_size - chunk_overlap:]
                current_chunk_words.extend(words)
            else:
                current_chunk_words.extend(words)

        if current_chunk_words:
            chunk_text_str = " ".join(current_chunk_words)
            chunks.append({
                "chunk_index": chunk_global_idx,
                "title": title,
                "page_number": page_num,
                "content": f"[{title} | Page {page_num}]\n{chunk_text_str}",
                "word_count": len(current_chunk_words),
            })
            chunk_global_idx += 1

    return chunks
