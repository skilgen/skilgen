from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

try:  # pragma: no cover - optional dependency
    from tree_sitter_language_pack import get_parser as get_tree_sitter_parser
except ImportError:  # pragma: no cover - optional dependency
    get_tree_sitter_parser = None


EXTENSION_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".vue": "vue",
    ".svelte": "svelte",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cbl": "cobol",
    ".cob": "cobol",
    ".cpy": "cobol",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".cs": "c_sharp",
    ".rb": "ruby",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".php": "php",
    ".swift": "swift",
    ".lua": "lua",
    ".zig": "zig",
    ".ps1": "powershell",
    ".psm1": "powershell",
    ".ex": "elixir",
    ".exs": "elixir",
    ".m": "objective_c",
    ".mm": "objective_c",
    ".dart": "dart",
    ".jl": "julia",
    ".sh": "bash",
    ".bash": "bash",
    ".r": "r",
    ".hs": "haskell",
    ".ml": "ocaml",
    ".fs": "f_sharp",
}
IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_:-]*")
CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
IMPORT_RE = re.compile(r"\b(?:import|from|use|COPY|copy)\s+([A-Za-z0-9_./:-]+)")
COBOL_DIVISION_RE = re.compile(r"^\s*([A-Z-]+\s+DIVISION)\.\s*$", re.MULTILINE)
COBOL_SECTION_RE = re.compile(r"^\s*([A-Z0-9-]+\s+SECTION)\.\s*$", re.MULTILINE)
EXTENDS_PATTERNS = [
    re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s+extends\s+([A-Za-z_][A-Za-z0-9_.:]*)"),
    re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*public\s+([A-Za-z_][A-Za-z0-9_:]*)"),
    re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_:]*)"),
    re.compile(r"\binterface\s+([A-Za-z_][A-Za-z0-9_]*)\s+extends\s+([A-Za-z_][A-Za-z0-9_.:]*)"),
    re.compile(r"\btype\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_.:]*)"),
]
IMPLEMENTS_PATTERN = re.compile(
    r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:extends\s+[A-Za-z_][A-Za-z0-9_.:<>]*\s+)?implements\s+([A-Za-z0-9_.,:\s<>]+)"
)
IMPORTS_FROM_PATTERN = re.compile(
    r"\bimport\s+(?:type\s+)?(?:\{?\s*([A-Za-z0-9_,\s]+)\s*\}?\s+from\s+)?[\"']([^\"']+)[\"']"
)


@dataclass(frozen=True)
class ParsedSymbolRelationship:
    symbol: str
    relationship: str
    targets: list[str]


@dataclass(frozen=True)
class ParsedLanguageEvidence:
    language: str
    backend: str
    symbols: list[str]
    calls: list[str]
    imports: list[str]
    relationships: list[ParsedSymbolRelationship] = field(default_factory=list)


def _safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _tree_sitter_parse(language: str, text: str) -> ParsedLanguageEvidence | None:
    if get_tree_sitter_parser is None:
        return None
    try:  # pragma: no cover - depends on optional parser runtime
        parser = get_tree_sitter_parser(language)
        tree = parser.parse(text.encode("utf-8", errors="ignore"))
    except Exception:
        return None

    identifiers: list[str] = []
    call_names: list[str] = []
    imports: list[str] = []
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        node_type = node.type.lower()
        if node_type in {
            "identifier",
            "type_identifier",
            "field_identifier",
            "property_identifier",
            "package_identifier",
            "namespace_identifier",
            "program_name",
            "entry_name",
            "section_name",
            "paragraph_name",
        }:
            value = text[node.start_byte : node.end_byte].strip()
            if value and len(value) < 120:
                identifiers.append(value)
        if "call" in node_type and node.children:
            for child in node.children[:3]:
                value = text[child.start_byte : child.end_byte].strip()
                if IDENTIFIER_RE.fullmatch(value):
                    call_names.append(value)
                    break
        if "import" in node_type or "using" in node_type or "include" in node_type:
            value = text[node.start_byte : node.end_byte].strip().replace("\n", " ")
            if value:
                imports.append(value[:180])
        stack.extend(reversed(node.children))
    return ParsedLanguageEvidence(
        language=language,
        backend="tree-sitter",
        symbols=sorted(dict.fromkeys(identifiers))[:30],
        calls=sorted(dict.fromkeys(call_names))[:30],
        imports=sorted(dict.fromkeys(imports))[:20],
    )


def _node_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        current: ast.expr | None = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))
    if isinstance(node, ast.Subscript):
        return _node_name(node.value)
    if isinstance(node, ast.Call):
        return _node_name(node.func)
    return None


def _python_ast_parse(text: str) -> ParsedLanguageEvidence:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ParsedLanguageEvidence(language="python", backend="python-ast", symbols=[], calls=[], imports=[], relationships=[])

    symbols: list[str] = []
    calls: list[str] = []
    imports: list[str] = []
    relationships: list[ParsedSymbolRelationship] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append(node.name)
            bases = [value for value in (_node_name(base) for base in node.bases) if value]
            if bases:
                relationships.append(ParsedSymbolRelationship(symbol=node.name, relationship="extends", targets=bases))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(node.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            target = "." * node.level + (node.module or "")
            if target:
                imports.append(target)
    return ParsedLanguageEvidence(
        language="python",
        backend="python-ast",
        symbols=sorted(dict.fromkeys(symbols))[:30],
        calls=sorted(dict.fromkeys(calls))[:30],
        imports=sorted(dict.fromkeys(imports))[:20],
        relationships=relationships[:20],
    )


def _regex_relationships(text: str) -> list[ParsedSymbolRelationship]:
    relationships: list[ParsedSymbolRelationship] = []
    for pattern in EXTENDS_PATTERNS:
        for symbol, target in pattern.findall(text):
            cleaned_target = target.split("<", 1)[0].split(".", 1)[0].strip()
            if symbol and cleaned_target:
                relationships.append(
                    ParsedSymbolRelationship(symbol=symbol, relationship="extends", targets=[cleaned_target])
                )
    for symbol, targets in IMPLEMENTS_PATTERN.findall(text):
        cleaned_targets = [
            candidate.split("<", 1)[0].split(".", 1)[0].strip()
            for candidate in re.split(r"[, ]+", targets)
            if candidate.strip()
        ]
        if cleaned_targets:
            relationships.append(
                ParsedSymbolRelationship(symbol=symbol, relationship="implements", targets=cleaned_targets[:6])
            )
    for imported_symbols, raw_import in IMPORTS_FROM_PATTERN.findall(text):
        if not imported_symbols.strip():
            continue
        names = [item.strip() for item in imported_symbols.split(",") if item.strip()]
        for name in names[:8]:
            relationships.append(
                ParsedSymbolRelationship(symbol=name, relationship="imports", targets=[raw_import.strip()])
            )
    return relationships[:24]


def parse_language_text(path: Path, text: str) -> ParsedLanguageEvidence:
    language = EXTENSION_LANGUAGE.get(path.suffix.lower(), "unknown")
    if not text:
        return ParsedLanguageEvidence(language=language, backend="empty", symbols=[], calls=[], imports=[], relationships=[])
    if language == "python":
        parsed = _python_ast_parse(text)
        if parsed.symbols or parsed.calls or parsed.imports or parsed.relationships:
            return parsed
    tree_sitter = _tree_sitter_parse(language, text)
    if tree_sitter is not None and (tree_sitter.symbols or tree_sitter.calls or tree_sitter.imports):
        if not tree_sitter.relationships:
            return ParsedLanguageEvidence(
                language=tree_sitter.language,
                backend=tree_sitter.backend,
                symbols=tree_sitter.symbols,
                calls=tree_sitter.calls,
                imports=tree_sitter.imports,
                relationships=_regex_relationships(text),
            )
        return tree_sitter
    return _regex_parse(language, text)


def _regex_parse(language: str, text: str) -> ParsedLanguageEvidence:
    symbols: list[str] = []
    if language == "cobol":
        symbols.extend(COBOL_DIVISION_RE.findall(text))
        symbols.extend(COBOL_SECTION_RE.findall(text))
        match = re.search(r"PROGRAM-ID\.\s*([A-Z0-9-]+)", text, re.IGNORECASE)
        if match:
            symbols.append(match.group(1))
    else:
        for pattern in [
            r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\binterface\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\benum\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\b(?:def|function|func)\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*function\b",
        ]:
            symbols.extend(re.findall(pattern, text))
    calls = [match.group(1) for match in CALL_RE.finditer(text) if match.group(1) not in {"if", "for", "while", "switch", "return", "catch", "new"}]
    imports = [match.group(1) for match in IMPORT_RE.finditer(text)]
    return ParsedLanguageEvidence(
        language=language,
        backend="regex",
        symbols=sorted(dict.fromkeys(symbols))[:30],
        calls=sorted(dict.fromkeys(calls))[:30],
        imports=sorted(dict.fromkeys(imports))[:20],
        relationships=_regex_relationships(text),
    )


def parse_language_evidence(path: Path) -> ParsedLanguageEvidence:
    return parse_language_text(path, _safe_text(path))
