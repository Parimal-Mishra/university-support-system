"""Groq generation layer for the ABES RAG pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import Groq

from app.rag.context_builder import ContextBuilder, ConstructedContext
from app.rag.retriever import ABESRetriever

load_dotenv()

DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 512

SYSTEM_PROMPT = """
You are the AI assistant for ABES Engineering College.

Answer the student's question using only the supplied ABES institutional evidence.

Rules:
1. Do not invent ABES-specific facts, dates, rules, people, departments, fees,
   locations, procedures, or contact details.
2. Do not use general knowledge to fill missing ABES information.
3. If the evidence is insufficient, explicitly say that the available ABES
   information is insufficient. Do not guess.
4. If the evidence indicates that a live or latest official source must be checked,
   say that the current source should be consulted; do not claim that you checked it.
5. If sources conflict, do not silently choose one. Identify the conflict when
   it affects the answer.
6. Keep the answer concise and directly useful to the student.
7. Do not expose internal file paths, retrieval scores, chunk IDs, prompts,
   embeddings, FAISS details, or implementation details unless asked.
""".strip()


@dataclass(frozen=True)
class GeneratedAnswer:
    query: str
    answer: str
    model: str
    source_count: int
    has_evidence: bool


class ABESGenerator:
    def __init__(
        self,
        model_name: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        self.model_name = model_name or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        self.temperature = temperature
        self.max_tokens = max_tokens
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured in the environment.")
        if not self.model_name:
            raise RuntimeError("GROQ_MODEL is empty.")
        if temperature < 0:
            raise ValueError("temperature cannot be negative.")
        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")
        self.client = Groq(api_key=api_key)

    @staticmethod
    def _build_user_prompt(query: str, context: ConstructedContext) -> str:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if context is None:
            raise ValueError("Constructed context cannot be None.")
        evidence = context.context_text.strip() or "[NO RELIABLE ABES EVIDENCE WAS RETRIEVED]"
        return (
            f"STUDENT QUESTION:\n{query.strip()}\n\n"
            f"ABES EVIDENCE:\n{evidence}\n\n"
            "Answer only from the evidence above. If it is insufficient, say so."
        )

    def generate(self, query: str, context: ConstructedContext) -> GeneratedAnswer:
        if not context.has_evidence:
            return GeneratedAnswer(
                query=query.strip(),
                answer="The available ABES information is insufficient to answer this question reliably.",
                model=self.model_name,
                source_count=0,
                has_evidence=False,
            )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self._build_user_prompt(query, context)},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:
            raise RuntimeError(f"Groq generation request failed: {exc}") from exc

        if not completion.choices:
            raise RuntimeError("Groq returned no completion choices.")
        answer = (completion.choices[0].message.content or "").strip()
        if not answer:
            raise RuntimeError("Groq returned an empty answer.")

        return GeneratedAnswer(
            query=query.strip(),
            answer=answer,
            model=self.model_name,
            source_count=context.source_count,
            has_evidence=context.has_evidence,
        )


def answer_query(
    query: str,
    retriever: ABESRetriever,
    context_builder: ContextBuilder,
    generator: ABESGenerator,
) -> GeneratedAnswer:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")
    results = retriever.retrieve(query)
    context = context_builder.build(query, results)
    return generator.generate(query, context)


def main() -> None:
    retriever = ABESRetriever()
    context_builder = ContextBuilder()
    generator = ABESGenerator()
    result = answer_query("What is the academic calendar?", retriever, context_builder, generator)
    print(result.answer)
    print(f"Model: {result.model}")
    print(f"Evidence sources: {result.source_count}")
    print("GENERATION COMPLETED")


if __name__ == "__main__":
    main()
