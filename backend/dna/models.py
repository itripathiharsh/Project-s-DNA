from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from enum import Enum
import json


@dataclass
class FileInfo:
    path: str
    relative_path: str
    filename: str
    extension: str
    language: str
    size_bytes: int
    is_directory: bool
    is_source: bool


@dataclass
class BuildSystem:
    name: str
    config_file: str
    version: Optional[str] = None


@dataclass
class Framework:
    name: str
    category: str
    confidence: float


@dataclass
class LanguageStats:
    language: str
    file_count: int
    total_bytes: int
    percentage: float


@dataclass
class RepositoryMetadata:
    name: str
    path: str
    is_git: bool
    languages: list[LanguageStats] = field(default_factory=list)
    primary_language: Optional[str] = None
    build_systems: list[BuildSystem] = field(default_factory=list)
    frameworks: list[Framework] = field(default_factory=list)
    file_count: int = 0
    total_size_bytes: int = 0
    ignored_files_count: int = 0
    scan_duration_ms: float = 0.0
    has_dna_ignore: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)

    @classmethod
    def from_json(cls, data: str) -> "RepositoryMetadata":
        raw = json.loads(data)
        return cls(
            name=raw["name"],
            path=raw["path"],
            is_git=raw["is_git"],
            languages=[LanguageStats(**ls) for ls in raw.get("languages", [])],
            primary_language=raw.get("primary_language"),
            build_systems=[BuildSystem(**b) for b in raw.get("build_systems", [])],
            frameworks=[Framework(**f) for f in raw.get("frameworks", [])],
            file_count=raw.get("file_count", 0),
            total_size_bytes=raw.get("total_size_bytes", 0),
            ignored_files_count=raw.get("ignored_files_count", 0),
            scan_duration_ms=raw.get("scan_duration_ms", 0.0),
            has_dna_ignore=raw.get("has_dna_ignore", False),
        )


@dataclass
class Commit:
    @property
    def author(self) -> str:
        """Alias for author_name for backward compatibility"""
        return self.author_name
    sha: str
    @property
    def hash(self) -> str:
        """Alias for sha for backward compatibility"""
        return self.sha
    parents: list[str] = field(default_factory=list)
    author_name: str = ""
    author_email: str = ""
    authored_at: Optional[str] = None
    committer_name: str = ""
    committer_email: str = ""
    committed_at: Optional[str] = None
    message: str = ""
    insertions: int = 0
    deletions: int = 0
    files_changed: int = 0
    per_file_changes: list["FileChange"] = field(default_factory=list)


@dataclass
class Branch:
    name: str
    target_sha: str = ""
    is_head: bool = False
    is_remote: bool = False


@dataclass
class Tag:
    name: str
    target_sha: str = ""
    tagger_name: Optional[str] = None
    tagger_email: Optional[str] = None
    tagged_at: Optional[str] = None
    message: str = ""


@dataclass
class FileChange:
    file_path: str
    insertions: int = 0
    deletions: int = 0
    change_type: str = "modified"


@dataclass
class AuthorStats:
    name: str
    email: str = ""
    commit_count: int = 0
    first_commit_at: Optional[str] = None
    last_commit_at: Optional[str] = None
    insertions: int = 0
    deletions: int = 0


@dataclass
class CommitHistory:
    commits: list[Commit] = field(default_factory=list)
    branches: list[Branch] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    author_stats: list[AuthorStats] = field(default_factory=list)
    total_branches: int = 0
    total_tags: int = 0


class FileCategory(str, Enum):
    SOURCE = "source"
    TEST = "test"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    BUILD = "build"
    DATA = "data"
    OTHER = "other"


@dataclass
class IndexedFile(FileInfo):
    category: FileCategory = FileCategory.OTHER
    content_hash: str = ""
    mtime: float = 0.0
    change_type: str = "added"


@dataclass
class FileClassificationMap:
    source: list[str] = field(default_factory=list)
    test: list[str] = field(default_factory=list)
    config: list[str] = field(default_factory=list)
    documentation: list[str] = field(default_factory=list)
    build: list[str] = field(default_factory=list)
    data: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)

    def add(self, category: FileCategory, path: str):
        key = category.value
        getattr(self, key).append(path)


@dataclass
class FileInventory:
    files: list[IndexedFile] = field(default_factory=list)
    categories: FileClassificationMap = field(default_factory=FileClassificationMap)
    total_files: int = 0
    total_size_bytes: int = 0


@dataclass
class DirectoryNode:
    name: str = ""
    path: str = ""
    children: list["DirectoryNode"] = field(default_factory=list)
    files: list[IndexedFile] = field(default_factory=list)


@dataclass
class DirectoryTree:
    root: DirectoryNode = field(default_factory=DirectoryNode)
    max_depth: int = 0
    total_dirs: int = 0


@dataclass
class FunctionDef:
    name: str = ""
    params: list[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    is_method: bool = False
    complexity: int = 1
    cognitive_complexity: int = 0
    halstead_effort: float = 0.0
    halstead_volume: float = 0.0
    calls: list[str] = field(default_factory=list)
    nesting_depth: int = 0


@dataclass
class ClassDef:
    name: str = ""
    methods: list[FunctionDef] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0


@dataclass
class ImportEntry:
    source: str = ""
    names: list[str] = field(default_factory=list)
    kind: str = "import"


@dataclass
class ExportEntry:
    name: str = ""
    source: str = ""
    kind: str = "export"


@dataclass
class SymbolTable:
    functions: list[FunctionDef] = field(default_factory=list)
    classes: list[ClassDef] = field(default_factory=list)
    imports: list[ImportEntry] = field(default_factory=list)
    exports: list[ExportEntry] = field(default_factory=list)


@dataclass
class ParsedFile:
    file_path: str | None = None
    relative_path: str | None = None
    language: str | None = None
    content_hash: str = ""
    source_bytes: bytes = b""
    ast_tree: Any = None
    symbols: SymbolTable = field(default_factory=SymbolTable)


@dataclass
class LanguageInfo:
    name: str
    extensions: list[str] = field(default_factory=list)
    parser_module: str = ""
    query_function: str | None = None
    query_class: str | None = None
    query_method: str | None = None


@dataclass
class CanonicalNode:
    kind: str = ""
    name: str = ""
    children: list["CanonicalNode"] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class NormalizedFile:
    relative_path: str = ""
    language: str = ""
    content_hash: str = ""
    root: CanonicalNode = field(default_factory=CanonicalNode)
    symbols: SymbolTable = field(default_factory=SymbolTable)


@dataclass
class SymbolOccurrence:
    symbol_name: str = ""
    kind: str = ""
    file_path: str = ""
    line: int = 0
    role: str = "definition"


@dataclass
class SymbolIndex:
    symbols: dict[str, list[SymbolOccurrence]] = field(default_factory=dict)

    def add(self, name: str, occ: SymbolOccurrence):
        if name not in self.symbols:
            self.symbols[name] = []
        self.symbols[name].append(occ)

    def get_definitions(self, name: str) -> list[SymbolOccurrence]:
        return [o for o in self.symbols.get(name, []) if o.role == "definition"]

    def get_references(self, name: str) -> list[SymbolOccurrence]:
        return [o for o in self.symbols.get(name, []) if o.role == "reference"]

    def find(self, name: str) -> list[SymbolOccurrence]:
        return self.symbols.get(name, [])


@dataclass
class DependencyNode:
    name: str = ""
    kind: str = "file"
    file_path: str = ""


@dataclass
class DependencyEdge:
    source: str = ""
    target: str = ""
    kind: str = "import"
    weight: int = 1


@dataclass
class DependencyGraph:
    nodes: list[DependencyNode] = field(default_factory=list)
    edges: list[DependencyEdge] = field(default_factory=list)
    _node_map: dict[str, DependencyNode] = field(default_factory=dict)
    _adjacency: dict[str, list[DependencyEdge]] = field(default_factory=dict)

    def add_node(self, node: DependencyNode):
        if node.name not in self._node_map:
            self._node_map[node.name] = node
            self.nodes.append(node)
            self._adjacency[node.name] = []

    def add_edge(self, edge: DependencyEdge):
        self.add_node(DependencyNode(name=edge.source, file_path=edge.source))
        self.add_node(DependencyNode(name=edge.target, file_path=edge.target))
        self.edges.append(edge)
        self._adjacency[edge.source].append(edge)

    def get_dependents(self, name: str) -> list[DependencyEdge]:
        return [e for e in self.edges if e.target == name]

    def get_dependencies(self, name: str) -> list[DependencyEdge]:
        return self._adjacency.get(name, [])

    def detect_cycles(self) -> list[list[str]]:
        visited: set[str] = set()
        path: list[str] = []
        cycles: list[list[str]] = []

        def dfs(node: str):
            if node in path:
                idx = path.index(node)
                cycles.append(path[idx:] + [node])
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            for edge in self._adjacency.get(node, []):
                dfs(edge.target)
            path.pop()

        for n in self.nodes:
            dfs(n.name)
        return cycles


ENTITY_TYPES = ["file", "module", "class", "function", "variable", "import"]


@dataclass
class Entity:
    def __eq__(self, other):
        if isinstance(other, str):
            return self.uid == other
        return super().__eq__(other)
    uid: str = ""
    name: str = ""
    kind: str = ""
    file_path: str = ""
    line: int = 0
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class EntityRelation:
    source_uid: str = ""
    target_uid: str = ""
    kind: str = ""  # IMPORTS, CONTAINS, DEFINES, CALLS, EXTENDS


@dataclass
class EntityGraph:
    entities: list[Entity] = field(default_factory=list)
    relations: list[EntityRelation] = field(default_factory=list)
    _entity_map: dict[str, Entity] = field(default_factory=dict)

    def add_entity(self, entity: Entity) -> None:
        if entity.uid not in self._entity_map:
            self._entity_map[entity.uid] = entity
            self.entities.append(entity)

    def add_relation(self, relation: EntityRelation) -> None:
        self.relations.append(relation)

    def get_entity(self, uid: str) -> Entity | None:
        return self._entity_map.get(uid)

    def get_relations(self, uid: str) -> list[EntityRelation]:
        return [r for r in self.relations if r.source_uid == uid or r.target_uid == uid]

    def query(self, kind: str | None = None, file_path: str | None = None) -> list[Entity]:
        result = self.entities
        if kind:
            result = [e for e in result if e.kind == kind]
        if file_path:
            result = [e for e in result if e.file_path == file_path]
        return result


@dataclass
class Evidence:
    id: str = ""
    type: str = ""
    value: str = ""
    source: str = ""
    file_path: str = ""
    timestamp: str = ""


EVIDENCE_TYPES = frozenset([
    "commit_metadata", "change_frequency", "author_contribution",
    "module_structure", "dependency_graph", "complexity_metrics",
    "size_metrics", "hotspot_list", "growth_trend",
    "refactoring_events", "temporal_coupling", "ownership_score",
    "expertise_score", "bus_factor", "risk_metrics", "commit_distribution",
])
