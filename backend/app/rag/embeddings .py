from sentence_transformers import SentenceTransformer


# ============================================================
# EMBEDDING CONFIGURATION
# ============================================================

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


# ============================================================
# EMBEDDING MODEL
# ============================================================

def load_embedding_model() -> SentenceTransformer:
    """
    Load the configured sentence-transformer embedding model.
    """

    print("=" * 60)
    print("LOADING EMBEDDING MODEL")
    print("=" * 60)

    print(
        f"Model: {EMBEDDING_MODEL_NAME}"
    )

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    print(
        "Embedding model loaded successfully."
    )

    return model


# ============================================================
# EMBED TEXT
# ============================================================

def embed_text(
    model: SentenceTransformer,
    text: str,
) -> list[float]:
    """
    Convert a single text string into an embedding vector.
    """

    if not text or not text.strip():
        raise ValueError(
            "Cannot generate embedding for empty text."
        )

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


# ============================================================
# EMBED DOCUMENTS
# ============================================================

def embed_documents(
    model: SentenceTransformer,
    texts: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for multiple text documents.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()


# ============================================================
# MODEL DIMENSION
# ============================================================

def get_embedding_dimension(
    model: SentenceTransformer,
) -> int:
    """
    Return the dimensionality of the embedding vectors.
    """

    dimension = model.get_sentence_embedding_dimension()

    if dimension is None:
        raise RuntimeError(
            "Unable to determine embedding dimension."
        )

    return dimension


# ============================================================
# TEST
# ============================================================

def main() -> None:

    model = load_embedding_model()

    dimension = get_embedding_dimension(
        model
    )

    print(
        f"\nEmbedding dimension: {dimension}"
    )

    test_text = (
        "What is the academic calendar "
        "for the current session?"
    )

    embedding = embed_text(
        model,
        test_text,
    )

    print(
        f"Test vector length: "
        f"{len(embedding)}"
    )

    print(
        "\nFirst 10 vector values:"
    )

    print(
        embedding[:10]
    )

    print("\n" + "=" * 60)
    print("EMBEDDING MODEL TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()