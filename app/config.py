from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    ai_provider: str = os.getenv("AI_PROVIDER", "openai").lower()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    chroma_path: str = os.getenv("CHROMA_PATH", "./storage/chroma")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "department_knowledge")
    faculty_file: str = os.getenv("FACULTY_FILE", "./data/faculty.json")
    department_notes_file: str = os.getenv(
        "DEPARTMENT_NOTES_FILE", "./data/department_demo_notes.json"
    )
    top_k: int = int(os.getenv("TOP_K", "4"))
    max_rag_distance: float = float(os.getenv("MAX_RAG_DISTANCE", "0.85"))
    allow_off_topic: bool = os.getenv("ALLOW_OFF_TOPIC", "false").lower() == "true"
    service_api_key: str | None = os.getenv("SERVICE_API_KEY")
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    max_question_chars: int = int(os.getenv("MAX_QUESTION_CHARS", "400"))

    def validate(self) -> None:
        if self.top_k < 1 or self.top_k > 20:
            raise ValueError("TOP_K must be between 1 and 20.")
        if self.max_rag_distance <= 0 or self.max_rag_distance > 2:
            raise ValueError("MAX_RAG_DISTANCE must be > 0 and <= 2.")
        if self.rate_limit_requests < 1:
            raise ValueError("RATE_LIMIT_REQUESTS must be >= 1.")
        if self.rate_limit_window_seconds < 1:
            raise ValueError("RATE_LIMIT_WINDOW_SECONDS must be >= 1.")
        if self.max_question_chars < 20:
            raise ValueError("MAX_QUESTION_CHARS must be >= 20.")
        if self.ai_provider not in {"openai", "gemini"}:
            raise ValueError("AI_PROVIDER must be either 'openai' or 'gemini'.")


settings = Settings()
