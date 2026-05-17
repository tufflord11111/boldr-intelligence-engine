"""
Step 2: Knowledge Base Loader
Loads all KB sources, chunks them, builds a FAISS vector index,
and provides semantic search.
"""
import json, csv
from pathlib import Path

import PyPDF2
import docx
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    USE_FAISS = True
except ImportError:
    USE_FAISS = False
    print("  [KB] sentence-transformers/faiss not available — using keyword search fallback")


class KBLoader:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.index_path = self.data_dir / "kb_faiss.index"
        self.chunks = []  # list of {"text": str, "source": str, "chunk_id": int}
        self.index = None
        self.model = None
        self._full_context = ""

    def _chunk_text(self, text: str, source: str, max_len: int = 400) -> list:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_len // 2):
            chunk = " ".join(words[i:i + max_len])
            if chunk.strip():
                chunks.append({"text": chunk, "source": source, "chunk_id": len(self.chunks) + len(chunks)})
        return chunks

    def _load_pdf(self, path: Path) -> str:
        try:
            text = ""
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            return text
        except Exception as e:
            print(f"  [KB] PDF load error {path.name}: {e}")
            return ""

    def _load_docx(self, path: Path) -> str:
        try:
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            print(f"  [KB] DOCX load error {path.name}: {e}")
            return ""

    def _load_csv(self, path: Path) -> str:
        try:
            rows = []
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(" | ".join(f"{k}: {v}" for k, v in row.items() if v))
            return "\n".join(rows)
        except Exception as e:
            print(f"  [KB] CSV load error {path.name}: {e}")
            return ""

    def build_index(self, force_rebuild: bool = False):
        """Load all KB sources and build FAISS index."""
        sources = [
            ("04_faq_document.pdf", self._load_pdf),
            ("05b_product_reference.docx", self._load_docx),
            ("05a_SOP.docx", self._load_docx),
            ("03a_rate_card_engraving.csv", self._load_csv),
            ("03b_rate_card_servicing.csv", self._load_csv),
        ]

        all_text_parts = []
        self.chunks = []

        for filename, loader in sources:
            path = self.data_dir / filename
            if not path.exists():
                print(f"  [KB] Missing: {filename} — skipping")
                continue
            print(f"  [KB] Loading {filename}...")
            text = loader(path)
            if text:
                all_text_parts.append(f"=== {filename.upper()} ===\n{text}")
                new_chunks = self._chunk_text(text, filename)
                self.chunks.extend(new_chunks)
                print(f"         → {len(new_chunks)} chunks")

        self._full_context = "\n\n".join(all_text_parts)
        print(f"  [KB] Total: {len(self.chunks)} chunks, {len(self._full_context):,} chars")

        # Build FAISS index if available
        if USE_FAISS and self.chunks:
            if not force_rebuild and self.index_path.exists():
                print(f"  [KB] Loading existing FAISS index...")
                try:
                    self.model = SentenceTransformer("all-MiniLM-L6-v2")
                    self.index = faiss.read_index(str(self.index_path))
                    if self.index.ntotal == len(self.chunks):
                        print(f"  [KB] FAISS index loaded ({self.index.ntotal} vectors)")
                        return
                    else:
                        print(f"  [KB] Index size mismatch — rebuilding")
                except Exception as e:
                    print(f"  [KB] Index load error: {e} — rebuilding")

            print(f"  [KB] Building FAISS index ({len(self.chunks)} chunks)...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            texts = [c["text"] for c in self.chunks]
            embeddings = self.model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings, dtype="float32")
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings)
            faiss.write_index(self.index, str(self.index_path))
            print(f"  [KB] FAISS index built and saved.")

    def search(self, query: str, top_k: int = 5) -> list:
        """Search KB for relevant chunks. Returns list of {text, source, score}."""
        if not self.chunks:
            return []

        if USE_FAISS and self.index and self.model:
            try:
                q_emb = self.model.encode([query], show_progress_bar=False)
                q_emb = np.array(q_emb, dtype="float32")
                distances, indices = self.index.search(q_emb, min(top_k, len(self.chunks)))
                results = []
                for dist, idx in zip(distances[0], indices[0]):
                    if idx < len(self.chunks):
                        chunk = self.chunks[idx]
                        results.append({
                            "text": chunk["text"],
                            "source": chunk["source"],
                            "score": float(1 / (1 + dist))
                        })
                return results
            except Exception as e:
                print(f"  [KB] FAISS search error: {e} — falling back to keyword")

        # Keyword fallback
        query_words = set(query.lower().split())
        scored = []
        for chunk in self.chunks:
            chunk_words = set(chunk["text"].lower().split())
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"text": c["text"], "source": c["source"], "score": s / 10}
                for s, c in scored[:top_k]]

    def get_full_context(self) -> str:
        return self._full_context
