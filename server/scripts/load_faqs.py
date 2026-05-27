#!/usr/bin/env python3
"""
Ingest FAQ entries into ChromaDB vector store.
Run AFTER setting OPENAI_API_KEY in .env.
Usage:  python scripts/load_faqs.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

FAQS = [
    "Refunds take 5-7 business days to process back to your original payment method.",
    "You can track your orders in the 'My Orders' section of your profile using the order ID.",
    "Our customer support team is available 24/7 via chat and email.",
    "We offer a 30-day return policy for all unused items in their original packaging.",
    "Shipping typically takes 3-5 business days for standard domestic orders.",
    "Express shipping is available at checkout and arrives within 1-2 business days.",
    "International shipping usually takes 10-14 business days.",
    "You can cancel your order within 1 hour of placing it if it has not shipped yet.",
    "Damaged or defective items can be replaced at no cost — contact support with a photo.",
    "Gift cards are non-refundable but never expire.",
]


def load_faqs():
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_OPENAI_KEY_HERE":
        print("ERROR: Set OPENAI_API_KEY in server/.env first.")
        sys.exit(1)

    from langchain.schema import Document
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings

    docs = [Document(page_content=faq) for faq in FAQS]
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    print(f"Indexing {len(docs)} FAQ entries...")
    Chroma.from_documents(docs, embeddings, persist_directory="/app/faq_db")
    print("FAQ ingestion complete. Vector store saved to /app/faq_db")


if __name__ == "__main__":
    load_faqs()
