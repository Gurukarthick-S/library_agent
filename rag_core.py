"""Documents, embeddings and retrieval (lessons 1 to 3)."""
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

KB_DIR = Path(__file__).parent / "knowledge_base"
EMBED_MODEL = "models/gemini-embedding-001"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4
FALLBACK = "I could not find that in the documents I have."


def clip(text, limit=600):
    """Shorten long text so tools and prompts stay small."""
    text = str(text)
    return text if len(text) <= limit else text[:limit] + "..."


def load_documents(folder=KB_DIR):
    """Read .txt, .md and text-based .pdf files from the folder."""
    docs = []
    for path in sorted(Path(folder).glob("*")):
        suffix = path.suffix.lower()
        text = ""
        if suffix in (".txt", ".md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".pdf":
            from pypdf import PdfReader
            text = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
        if text.strip():
            docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)


def make_embeddings(api_key):
    return GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=api_key)


def build_store(api_key):
    """Index the knowledge base once per visitor, using their own key."""
    docs = load_documents()
    if not docs:
        raise ValueError("No readable documents were found in knowledge_base/.")
    chunks = split_documents(docs)
    return InMemoryVectorStore.from_documents(chunks, make_embeddings(api_key))


def retrieve(store, question, k=TOP_K):
    """Return the top passages as a list of dicts: n, source, text."""
    found = store.similarity_search(question, k=k)
    return [
        {"n": i + 1, "source": d.metadata.get("source", "?"), "text": d.page_content}
        for i, d in enumerate(found)
    ]


def format_context(passages):
    return "\n\n".join(f"[{p['n']}] ({p['source']}) {p['text']}" for p in passages)
