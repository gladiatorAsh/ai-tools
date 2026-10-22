---
name: document-ingestion
description: Guides turning PDFs, Office files, HTML and scans into clean, structured, chunked text with metadata for RAG - choosing Docling vs MarkItDown vs OCR, preserving tables and headings, structure-aware chunking, provenance and ACL metadata, idempotent re-ingestion, and quality checks. Use when building or fixing an ingestion pipeline that feeds a search index or knowledge base.
---

# Document Ingestion

## Overview

Garbage in, hallucination out. Most RAG quality problems start at conversion: lost tables, merged columns,
headers repeated on every chunk, scanned pages with no text. Pick the converter for the document type, keep
structure, attach provenance and permissions, and check the output before indexing.

## When to Use

- New document sources or file types are being added to RAG.
- Answers miss information you can see in the original files (tables, figures, scanned pages).
- NOT for query-time retrieval — that's `azure-ai-search-rag`.

## Process

1. **Inventory the corpus.** Count by type (born-digital PDF, scanned PDF, DOCX, PPTX, XLSX, HTML), language,
   and whether layout matters (tables, multi-column). Sample 10 documents per type.
2. **Choose the converter per type:**

   | Situation | Tool |
   |---|---|
   | Layout matters: tables, multi-column PDFs, reading order | **Docling** (MIT) — `DocumentConverter().convert(path).document.export_to_markdown()` |
   | Simple Office/HTML/text, speed and few dependencies | **MarkItDown** (MIT) — `MarkItDown().convert(path).text_content` |
   | Scanned or image-only pages, multilingual OCR | Docling with OCR enabled, PaddleOCR, or Azure AI Document Intelligence (stays inside Azure) |

   Docling pulls ML models (heavier install); MarkItDown is lightweight. Use `choose-ai-tool` to compare more.
3. **Chunk on structure.** Split on headings/sections first, then by size (a few hundred tokens) with small overlap.
   Keep tables intact (or one row-group per chunk with repeated headers). Prefix each chunk with its document title
   and section path so it stands alone. Docling's `HybridChunker` does structure + token-aware splitting.
4. **Attach metadata to every chunk:** stable document ID, source URI, chunk index, section path, page numbers,
   content hash, last-modified, language, and the **ACL/group field** used for security trimming.
5. **Make it idempotent.** Key chunks by `doc_id + chunk_index`; skip unchanged documents by content hash; delete
   chunks of removed or shrunk documents. Re-runs must not create duplicates.
6. **Check quality before indexing.** For sampled docs: compare page count vs extracted text, flag near-empty
   pages (missed OCR), verify table cell counts, and diff a few conversions by eye. Log per-document failures and
   continue; don't abort the batch.
7. **Process untrusted files safely.** Enforce size/page limits, run converters with timeouts in an isolated
   worker, and treat extracted text as untrusted (it may contain prompt-injection text).

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "PDF to text is a solved problem" | Not for tables, columns or scans. Check outputs; most RAG misses start here. |
| "Fixed 1,000-character chunks are fine" | They split tables and sentences mid-way and lose section context. |
| "We'll handle deletes later" | Deleted or revoked documents keep answering questions until you do. |

## Red Flags

- One converter for every file type with no sampling of its output.
- Chunks without source URI, page or ACL metadata.
- Re-ingestion that duplicates chunks or never removes stale ones.
- Scanned PDFs producing empty or tiny text with no warning.

## Verification

- [ ] Sample conversions per file type were inspected; tables and reading order are intact.
- [ ] Every chunk carries doc ID, source, section/page and ACL metadata.
- [ ] Re-running ingestion on an unchanged corpus produces zero changes (test).
- [ ] Removing a document removes its chunks (test).
- [ ] Empty/failed extractions are reported with the document ID.
