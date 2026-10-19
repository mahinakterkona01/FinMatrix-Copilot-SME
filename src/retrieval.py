"""
FinMatrix Copilot— RAG Retrieval & Knowledge Base Engine
Parses Bangladesh Bank CMSME circulars (PDFs/Text) and builds a citation-grounded index.
Handles encoding filters for clean policy search.
"""

import os
import glob
import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# Search hints only; these are not policy evidence and are never returned
# as part of the cited source text.
SOURCE_RETRIEVAL_METADATA = {
    "jul022026smespdl03e.pdf": (
        "Bangladesh Bank SMESPD Circular Letter No 03 July 2 2026 "
        "JICA assisted Urban Building Safety Project UBSP BD-P84 "
        "Operating Guidelines non-performing loans NPL ratio 20 percent"
    ),
    "sep132026smespd05.pdf": (
        "Bangladesh Bank SMESPD Circular No 05 September 13 2026 "
        "UDYOG young entrepreneurs age 28 district lead bank "
        "bank loan grant financial assistance youth entrepreneurship"
    ),
    "sep202026smespdl04.pdf": (
        "Bangladesh Bank SMESPD Circular Letter No 04 September 20 2026 "
        "CMSME Working Capital Refinance Fund finance companies "
        "eligible for refinancing circular 08 June 2026"
    ),
}


# Fail closed for PDFs whose extracted text was manually found to be corrupted.
PDF_EXTRACTION_QUARANTINE = {
    "sep132026smespd05.pdf": "Bangla extraction contains visibly corrupted words.",
    "sep202026smespdl04.pdf": "Legacy-encoded text is not reliably readable as extracted.",
}

# Only dates verified from the readable source document belong here.
SOURCE_EFFECTIVE_DATES = {
    "jul022026smespdl03e.pdf": "2026-07-02",
}

# Initial conservative floor; calibrate against a larger labeled query set.
MIN_POLICY_SIMILARITY = 0.10


class PolicyRAGEngine:
    def __init__(self, docs_dir: str = "data/rag_docs"):
        self.docs_dir = docs_dir
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self._is_indexed = False

    def _is_clean_text(self, text: str) -> bool:
        """Rejects empty text and text dominated by unreadable characters."""
        if not text or not text.strip():
            return False

        total_chars = len(text)
        readable_chars = len(
            re.findall(r'[a-zA-Z0-9\s.,;:\-()%]', text)
        )

        if (readable_chars / total_chars) > 0.6:
            return True

        non_whitespace_chars = len(re.sub(r'\s', '', text))
        if non_whitespace_chars == 0:
            return False

        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
        bengali_ratio = bengali_chars / non_whitespace_chars

        return bengali_ratio >= 0.25

    def _extract_pdf_text(self, file_path: str) -> List[str]:
        """Extracts text page-by-page from PDF files using pypdf with encoding filtering."""
        chunks = []
        file_name = file_path.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if file_name in PDF_EXTRACTION_QUARANTINE:
            return chunks
        if not PYPDF_AVAILABLE:
            return chunks

        try:
            reader = PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and len(text.strip()) > 30:
                    cleaned_text = " ".join(text.split())
                    if self._is_clean_text(cleaned_text):
                        chunks.append(f"[Page {page_num}] {cleaned_text}")
        except Exception as e:
            print(f"Warning: Could not parse PDF {file_path}: {e}")
        return chunks

    def load_and_chunk_documents(self) -> None:
        """Parses all PDFs and clean text files in data/rag_docs into structured policy chunks."""
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir, exist_ok=True)

        pdf_files = glob.glob(os.path.join(self.docs_dir, "*.pdf"))
        txt_files = glob.glob(os.path.join(self.docs_dir, "*.txt"))

        # 1. Process Text Files First (High Priority Structured Policy Maps)
        for txt_path in txt_files:
            file_name = os.path.basename(txt_path)

            # This summary contains unverified policy claims; never index it
            # as authoritative evidence.
            if file_name.lower() == "sme_circular_summary.txt":
                continue

            try:
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 20]
                for idx, p in enumerate(paragraphs):
                    self.documents.append({
                        "source": file_name,
                        "section": f"Policy-Rule-{idx+1}",
                        "text": p,
                        "effective_date": None
                    })
            except Exception:
                pass

        # 2. Process Clean PDF Circulars
        for pdf_path in pdf_files:
            file_name = os.path.basename(pdf_path)
            extracted_chunks = self._extract_pdf_text(pdf_path)
            for idx, chunk in enumerate(extracted_chunks):
                self.documents.append({
                    "source": file_name,
                    "section": f"PDF-Page-{idx+1}",
                    "text": chunk,
                    "effective_date": SOURCE_EFFECTIVE_DATES.get(pdf_path.replace("\\", "/").rsplit("/", 1)[-1].lower())
                })


    def _retrieval_text(self, doc: Dict[str, Any]) -> str:
        """Add source-level search hints without altering returned evidence."""
        source = str(doc.get("source", ""))
        hint = SOURCE_RETRIEVAL_METADATA.get(source, "")
        return f"{doc.get('text', '')} {hint}".strip()

    def build_index(self) -> None:
        """Constructs a fresh TF-IDF index across clean policy chunks."""
        self.documents = []
        self.tfidf_matrix = None
        self._is_indexed = False

        self.load_and_chunk_documents()
        corpus = [self._retrieval_text(doc) for doc in self.documents]
        if corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self._is_indexed = True

    def query_policy(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve relevant policy snippets; abstain when evidence is unavailable."""
        if not isinstance(query, str) or not query.strip() or top_k < 1:
            return []

        if not self._is_indexed:
            self.build_index()

        if (
            not self.documents
            or self.tfidf_matrix is None
            or not hasattr(self.vectorizer, "vocabulary_")
        ):
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        if similarities.size == 0 or similarities.max() < MIN_POLICY_SIMILARITY:
            return []

        ranked_indices = similarities.argsort()[::-1]
        results = []
        seen_sources = set()

        for idx in ranked_indices:
            score = float(similarities[idx])

            # Do not return documents with zero lexical similarity.
            if score <= 0:
                break

            doc = self.documents[idx].copy()
            source = doc.get("source")
            source_key = source if source else f"__document_{idx}"

            # Keep the highest-ranked chunk from each source document.
            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)
            doc["relevance_score"] = round(score, 4)
            results.append(doc)

            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":
    print("--- Testing Clean Policy RAG Knowledge Engine ---")
    rag = PolicyRAGEngine()
    rag.build_index()
    
    print(f"Total Clean Indexed Chunks: {len(rag.documents)}")
    
    test_query = "Working capital refinance interest rate for CMSME"
    retrieved_docs = rag.query_policy(test_query, top_k=2)
    
    print(f"\nQuery: '{test_query}'")
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"\n[{i}] Source: {doc['source']} | Score: {doc['relevance_score']}")
        print(f"    Snippet: {doc['text'][:150]}...")