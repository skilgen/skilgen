from __future__ import annotations

import json
import re
from datetime import datetime

from apps.api.api.services.llm import call_llm


def _extract_section_bullets(content: str, heading: str) -> list[str]:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return []
    tail = content[match.end():]
    next_heading = re.search(r"^##\s+", tail, flags=re.MULTILINE)
    section = tail[: next_heading.start()] if next_heading else tail
    bullets: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            bullets.append(re.sub(r"^[-*]\s*", "", stripped).strip())
    return bullets


async def generate_skill_with_ai(
    org_settings: dict,
    domain: str,
    repo_name: str,
    context_files: list[str],
    enterprise_skills: list[dict],
    user_intent: str | None = None,
) -> dict:
    """Generate a concrete SKILL.md using the org-configured LLM provider."""
    system_prompt = f"""You are a Skillayer skill author. Write a SKILL.md document that teaches
AI agents how to work with the {domain} domain in the {repo_name} codebase.

Output structure (Markdown):
# {domain}
## Domain summary (2-3 sentences)
## Key patterns (bulleted, 4-8 items, reference real file paths)
## Anti-patterns (bulleted, 3-6 items - "Do NOT do X because Y")
## File references (bulleted file paths)
## Last verified - {{Month Year}}

Be concrete and specific. Reference actual files. No filler text."""
    enterprise_context = ""
    if enterprise_skills:
        enterprise_context = "Inherit from these enterprise skills:\n" + "\n".join([str(skill.get("content", ""))[:500] for skill in enterprise_skills])
    user_prompt = f"""Domain: {domain}
Repo: {repo_name}
Related files: {', '.join(context_files)}
{f'User intent: {user_intent}' if user_intent else ''}
{enterprise_context}
Write the SKILL.md now."""
    content = await call_llm(org_settings, system_prompt, user_prompt, max_tokens=2048)
    return {
        "content": content,
        "anti_patterns": _extract_section_bullets(content, "Anti-patterns"),
        "file_references": _extract_section_bullets(content, "File references"),
    }


SKILL_CHAT_SYSTEM_PROMPT = """You are Skillayer's AI skill author assistant. Your job is to
help the user create a high-quality SKILL.md artifact through a short conversation.

You need to gather four things before generating:
  1. Skill name / domain (e.g. "auth", "payments", "data pipeline")
  2. Target repo (which codebase this skill belongs to, or "global" for org-wide)
  3. Category (codebase-architecture / code-style / testing / security / data-schema /
     internal-tools / design-system / operational)
  4. At least one concrete behavior, pattern, or anti-pattern to encode

Ask only ONE clarifying question at a time. Be conversational. Once you have all four,
output EXACTLY this JSON block (no other text):

```READY
{
  "domain": "<name>",
  "repo": "<repo_name or global>",
  "category": "<category>",
  "draft_intent": "<one-sentence summary of what this skill should teach>",
  "ready_to_create": true
}
```

If the user says "just create it" or provides enough context to infer all four items, do not
ask more questions - output the READY block immediately.

Rules:
- Keep every message under 3 sentences when asking questions.
- Never refuse. If unsure about something, make a sensible assumption and state it.
- If enterprise skill examples are provided in context, match their style exactly.
- After outputting the READY block, do not say anything else."""


async def chat_create_skill(
    org_settings: dict,
    chat_history: list[dict],
    repo_context: dict | None,
    enterprise_skills: list[dict],
) -> dict:
    system = SKILL_CHAT_SYSTEM_PROMPT
    if repo_context:
        system += f"\n\nCurrent repo context: {repo_context['repo_name']}\nFile tree sample:\n{repo_context.get('file_tree_sample', '')}"
    if enterprise_skills:
        system += "\n\nEnterprise skill examples (match their style):\n" + "\n---\n".join([str(skill.get("content", ""))[:400] for skill in enterprise_skills[:3]])
    reply = await call_llm(
        org_settings,
        system,
        "\n".join([f"{m['role'].upper()}: {m['content']}" for m in chat_history]),
        max_tokens=512,
    )
    ready_to_create = False
    draft_skill = None
    if "```READY" in reply:
        match = re.search(r"```READY\s*(\{.*?\})\s*```", reply, re.DOTALL)
        if match:
            meta = json.loads(match.group(1))
            if meta.get("ready_to_create"):
                ready_to_create = True
                draft_skill = await generate_skill_with_ai(
                    org_settings,
                    domain=meta["domain"],
                    repo_name=meta["repo"],
                    context_files=[],
                    enterprise_skills=enterprise_skills,
                    user_intent=meta["draft_intent"],
                )
                draft_skill["meta"] = meta
                draft_skill["generated_at"] = datetime.utcnow().isoformat()
    return {"assistant_reply": reply, "draft_skill": draft_skill, "ready_to_create": ready_to_create}
