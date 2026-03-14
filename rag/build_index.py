"""
최초 1회만 실행:
    python rag/build_index.py
    python rag/build_index.py --force
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()
from rag.vector_store import build_index

if __name__ == "__main__":
    build_index(force="--force" in sys.argv)
