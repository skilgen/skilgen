from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
import asyncio

import pytest

from apps.api.api.services import memory
from packages.db.models import AgentSession, Skill


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Message:
    role: str
    content: str


class FakeScalarResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class FakeResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.values)


class FakeDb:
    def __init__(self, session: AgentSession, skills: list[Skill]) -> None:
        self.session = session
        self.skills = skills
        self.added: list[object] = []
        self.commits = 0
        self.rollbacks = 0

    async def get(self, model: object, key: str) -> AgentSession | None:
        return self.session if key == self.session.id else None

    async def execute(self, statement: object) -> FakeResult:
        text = str(statement)
        if "UPDATE agent_sessions" in text:
            if "processing" in text:
                self.session.extraction_status = "processing"
            if "done" in text:
                self.session.extraction_status = "done"
        return FakeResult(self.skills)

    def add(self, value: object) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


def _session() -> AgentSession:
    return AgentSession(
        id="session_db",
        repo_id="repo_1",
        org_id="org_123",
        session_id="client_session",
        agent_runtime="codex",
        files_touched=["src/auth/jwt.py"],
        skill_paths_loaded=["auth/SKILL.md"],
        extraction_status="pending",
        discoveries_found=0,
    )


def test_session_ingestion_endpoint_contract_is_present() -> None:
    source = (ROOT / "apps/api/api/routes/repos.py").read_text(encoding="utf-8")
    assert "class SessionIngestionPayload(BaseModel)" in source
    assert '@router.post("/{repo_id}/sessions", response_model=SessionIngestionResponse, status_code=201)' in source
    assert "background_tasks.add_task(run_session_knowledge_extraction" in source
    assert 'extraction_status="pending"' in source
    assert "status=\"duplicate\"" in source


def test_memory_queue_review_contract_is_present() -> None:
    source = (ROOT / "apps/api/api/routes/orgs.py").read_text(encoding="utf-8")
    assert '@router.get("/{org_id}/memory-queue", response_model=MemoryQueueResponse)' in source
    assert '@router.patch("/{org_id}/memory-queue/{stub_id}", response_model=MemoryStubResponse)' in source
    assert 'stub.status = "merged"' in source
    assert 'stub.status = "rejected"' in source
    assert "SkillVersion(" in source


def test_build_transcript_keeps_recent_messages() -> None:
    messages = [Message(role="assistant", content=f"message-{index}-" + "x" * 300) for index in range(60)]
    text = memory._build_transcript_text(messages, max_chars=1200)
    assert text.startswith("...[earlier messages truncated]...")
    assert "message-59" in text
    assert "message-1-" not in text


def test_summarise_transcript_uses_first_substantial_assistant_message() -> None:
    assert memory._summarise_transcript([Message("user", "hello"), Message("assistant", "x" * 40)]) == "x" * 40


def test_extraction_noops_without_anthropic_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    session = _session()
    db = FakeDb(session, [_skill("auth")])
    asyncio.run(memory._extract_session_knowledge("session_db", [Message("assistant", "I found a JWT gotcha in src/auth/jwt.py")], "repo_1", db))  # type: ignore[arg-type]
    assert db.added == []
    assert db.commits >= 2


def test_extraction_mock_creates_memory_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_call(**kwargs: object) -> list[dict[str, object]]:
        return [{"domain": "auth", "type": "gotcha", "title": "JWT expiry gotcha", "content": "## JWT gotcha\nUse `src/auth/jwt.py`.", "evidence": "src/auth/jwt.py", "confidence": 0.85}]

    monkeypatch.setattr(memory, "_call_extraction_llm", fake_call)
    session = _session()
    db = FakeDb(session, [_skill("auth")])
    asyncio.run(memory._extract_session_knowledge("session_db", [Message("assistant", "I found a JWT gotcha in src/auth/jwt.py")], "repo_1", db))  # type: ignore[arg-type]
    assert len(db.added) == 1
    stub = db.added[0]
    assert getattr(stub, "domain") == "auth"
    assert getattr(stub, "skill_id") == "skill_auth"


def test_knowledge_velocity_contracts_exist() -> None:
    repos_source = (ROOT / "apps/api/api/routes/repos.py").read_text(encoding="utf-8")
    orgs_source = (ROOT / "apps/api/api/routes/orgs.py").read_text(encoding="utf-8")
    assert '@router.get("/{repo_id}/knowledge-velocity", response_model=list[KnowledgeVelocityPoint])' in repos_source
    assert '@router.get("/{org_id}/knowledge-velocity", response_model=KnowledgeVelocityResponse)' in orgs_source
    assert "approval_rate" in orgs_source


def _skill(domain: str) -> Skill:
    return Skill(
        id=f"skill_{domain}",
        repo_id="repo_1",
        run_id="run_1",
        domain=domain,
        skill_path=f"skills/{domain}/SKILL.md",
        content=f"## {domain}\nExisting content",
        created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1),
    )
