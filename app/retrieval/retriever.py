from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.retrieval.loader import load_documents


class KnowledgeRetriever:
    """
    Lightweight metadata-aware TF-IDF retriever.

    Semantic similarity is combined with document authority and
    status so superseded/internal documents don't incorrectly
    outrank active customer-facing policy.
    """

    def __init__(self, directory="knowledge-base"):
        self.documents = load_documents(directory)

        if not self.documents:
            raise ValueError("No knowledge-base documents found.")

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        corpus = [
            self._document_text(document)
            for document in self.documents
        ]

        self.matrix = self.vectorizer.fit_transform(corpus)

    @staticmethod
    def _document_text(document):
        return " ".join(
            [
                str(document.get("title", "")),
                str(document.get("heading", "")),
                str(document.get("content", "")),
            ]
        )

    @staticmethod
    def _authority_score(document):
        """
        Explicit metadata-based trust score.

        Higher = more suitable as customer-facing authority.
        """
        score = 0.0

        status = str(document.get("status", "")).lower()
        authority = str(
            document.get("policy_authority", "")
        ).lower()
        audience = str(document.get("audience", "")).lower()

        customer_answering = document.get(
            "customer_answering", True
        )

        if status == "active":
            score += 0.30
        elif status == "superseded":
            score -= 0.35
        elif status == "draft":
            score -= 0.45

        if authority == "official":
            score += 0.25
        elif authority == "none":
            score -= 0.30

        if audience == "customer":
            score += 0.15
        elif audience == "internal":
            score -= 0.30

        if customer_answering is False:
            score -= 0.50

        return score

    @staticmethod
    def _keyword_score(query, document):
        """
        Small exact-term boost.

        This helps cases where the query contains an important
        policy/product term that appears directly in the heading.
        """
        query_terms = {
            term.lower()
            for term in query.split()
            if len(term) > 2
        }

        heading = str(
            document.get("heading", "")
        ).lower()

        title = str(
            document.get("title", "")
        ).lower()

        score = 0.0

        for term in query_terms:
            if term in heading:
                score += 0.08
            elif term in title:
                score += 0.04

        return min(score, 0.25)

    def search(self, query, top_k=5):
        if not query or not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.matrix,
        )[0]

        results = []

        for index, similarity in enumerate(similarities):
            document = self.documents[index]

            semantic_score = float(similarity)

            authority_score = self._authority_score(document)
            keyword_score = self._keyword_score(
                query,
                document,
            )

            final_score = (
                semantic_score
                + authority_score
                + keyword_score
            )

            results.append(
                {
                    **document,
                    "semantic_score": round(
                        semantic_score, 4
                    ),
                    "authority_score": round(
                        authority_score, 4
                    ),
                    "keyword_score": round(
                        keyword_score, 4
                    ),
                    "score": round(
                        final_score, 4
                    ),
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]

    def format_sources(self, results):
        """
        Create concise source citations.
        """
        sources = []

        seen = set()

        for result in results:
            key = (
                result["filename"],
                result["heading"],
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "filename": result["filename"],
                    "heading": result["heading"],
                    "document_id": result.get(
                        "document_id"
                    ),
                    "status": result.get("status"),
                }
            )

        return sources
