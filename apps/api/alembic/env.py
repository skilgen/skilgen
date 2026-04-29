import os
from logging.config import fileConfig
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv("../../.env.local")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL", "")
if "postgresql+asyncpg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
if DATABASE_URL:
    parsed = urlsplit(DATABASE_URL)
    if parsed.scheme.startswith("postgresql"):
        query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key not in {"ssl", "sslmode"}
        ]
        query.append(("sslmode", "require"))
        DATABASE_URL = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))

config.set_main_option("sqlalchemy.url", DATABASE_URL)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.db.models.base import Base
from packages.db.models.org import Org
from packages.db.models.repo import Repo
from packages.db.models.analysis_run import AnalysisRun
from packages.db.models.skill import Skill
from packages.db.models.agent_session import AgentSession
from packages.db.models.audit_event import AuditEvent
from packages.db.models.half_life import SkillHalfLife
from packages.db.models.org_llm_config import OrgLLMConfig
from packages.db.models.org_policy import OrgPolicy
from packages.db.models.pr_attribution import PRAttribution
from packages.db.models.pr_comment import PRComment
from packages.db.models.pull_request import Commit, PullRequest
from packages.db.models.skill_memory_stub import SkillMemoryStub
from packages.db.models.skill_snapshot import SkillSnapshot
from packages.db.models.skill_version import SkillVersion
from packages.db.models.registry import MarketplaceInstall, SkillDependency, SkillRegistryEntry
from packages.db.models.score_history import ScoreHistory
from packages.db.models.source_connection import SourceConnection
from packages.db.models.skill_usage_event import SkillUsageEvent
from packages.db.models.review_run import ReviewRun

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
