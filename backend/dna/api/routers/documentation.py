from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
from collections import defaultdict
from dna.api.routers.system import _get_store_path
from dna.storage.store import SCStore

router = APIRouter(prefix="/v1/documentation", tags=["documentation"])

@router.get("/generate/{doc_type}")
def generate_documentation(doc_type: str) -> Dict[str, Any]:
    store_path = _get_store_path()
    if not os.path.exists(store_path):
        return {"content": "# No Project Found\nPlease analyze a repository first."}
    with SCStore(store_path) as store:
        graph = store.load_entity_graph()
    
    # Strip noisy cache prefix from file paths for clean display
    def clean_path(p: str) -> str:
        parts = p.replace("\\", "/").split("/")
        # Drop everything up to and including 'cache/repos/REPONAME'
        try:
            ci = next(i for i, part in enumerate(parts) if part == "cache")
            # skip: cache / repos / reponame  = 3 segments
            return "/".join(parts[ci + 3:]) or p
        except StopIteration:
            return p

    file_entities = [e for e in graph.entities if e.kind == "file"]
    class_entities = [e for e in graph.entities if e.kind == "class"]
    func_entities = [e for e in graph.entities if e.kind == "function"]
    
    content = ""
    
    if doc_type == "architecture":
        content = "# 🏗️ Architecture Documentation\n\n"
        content += "## System Overview\n"
        content += f"This repository contains **{len(file_entities)} modules**, **{len(class_entities)} classes**, and **{len(func_entities)} functions**.\n\n"
        content += "## Core Components\n"
        components = defaultdict(list)
        for f in file_entities:
            cp = clean_path(f.file_path)
            folder = os.path.dirname(cp)
            components[folder if folder else "Root"].append(os.path.basename(cp))
        for comp, files in list(components.items())[:10]:
            content += f"### {comp}\n"
            for file in files[:5]:
                content += f"- `{file}`\n"
            if len(files) > 5:
                content += f"- ...and {len(files)-5} more\n"
                
    elif doc_type == "readme":
        content = "# 📖 Project Documentation\n\n"
        content += "> Automatically generated project README.\n\n"
        content += "## Quick Stats\n"
        content += f"- **Files**: {len(file_entities)}\n"
        content += f"- **Classes**: {len(class_entities)}\n"
        content += f"- **Functions**: {len(func_entities)}\n\n"
        content += "## Main Entry Points\n"
        entry_points = [f for f in file_entities if "main" in f.file_path.lower() or "app" in f.file_path.lower()]
        if not entry_points: entry_points = file_entities[:5]
        for ep in entry_points:
            content += f"- `{clean_path(ep.file_path)}`\n"
            
    elif doc_type == "api":
        content = "# 🔌 API Documentation\n\n"
        api_funcs = [f for f in func_entities if "api" in f.file_path.lower() or "router" in f.file_path.lower()]
        if not api_funcs: api_funcs = func_entities[:20]
        content += "The following functions represent the API surface of the system:\n\n"
        for idx, f in enumerate(api_funcs[:50]):
            content += f"### {idx+1}. `{f.name}`\n"
            content += f"- **Location**: `{clean_path(f.file_path)}`\n\n"
            
    elif doc_type == "sequence":
        content = "## 🔄 Sequence Diagram (Top Interactions)\n\n"
        calls = [r for r in graph.relations if r.kind == "CALLS"]
        if not calls:
            content += "> **Notice**: We couldn't detect any explicit function calls (AST relation `CALLS`) in this repository. This can happen if the language is not fully supported or if the codebase is entirely declarative.\n"
        else:
            content += "```mermaid\nsequenceDiagram\n"
            for r in calls[:20]:
                source = r.source_uid.split(":")[-1].replace("-", "_").replace(".", "_")
                target = r.target_uid.split(":")[-1].replace("-", "_").replace(".", "_")
                content += f'    "{source}"->>"{target}": invokes\n'
            content += "```\n"
        
    elif doc_type == "mermaid":
        content = "## 📊 System Flowchart\n\n"
        content += "```mermaid\ngraph TD\n"
        for i, f in enumerate(file_entities[:15]):
            name = os.path.basename(f.file_path)
            content += f'    F{i}["{name}"]\n'
        content += "```\n"

    elif doc_type == "c4":
        content = "## 🏗️ C4 Context Diagram\n\n"
        # Using standard graph to emulate C4 Context since native C4 requires plugins
        content += "```mermaid\ngraph TD\n"
        content += '    User(("🧑 User"))\n'
        content += '    System["🟦 Target Project"]\n'
        content += '    User -.->|"Uses"| System\n'
        for idx, f in enumerate(file_entities[:5]):
            content += f'    Ext{idx}["⬛ {os.path.basename(f.file_path)}"]\n'
            content += f'    System -.->|"Depends on"| Ext{idx}\n'
        content += "```\n"

    elif doc_type == "er":
        content = "## 💾 Entity-Relationship Diagram\n\n"
        models = [c for c in class_entities if "model" in c.file_path.lower() or "schema" in c.file_path.lower()]
        if not models: models = class_entities[:10]
        if not models:
            content += "> **Notice**: No classes or schemas were found in the codebase to generate an ER diagram.\n"
        else:
            content += "```mermaid\nerDiagram\n"
            for i, m in enumerate(models):
                name = m.name.replace("-", "_").replace(".", "_")
                content += f'    "{name}" {{\n        string id\n    }}\n'
                if i > 0:
                    prev = models[i-1].name.replace("-", "_").replace(".", "_")
                    content += f'    "{prev}" ||--o{{ "{name}" : links\n'
            content += "```\n"

    elif doc_type == "module":
        content = "# 📦 Module Documentation\n\n"
        for f in file_entities[:20]:
            cp = clean_path(f.file_path)
            content += f"## `{os.path.basename(cp)}`\n"
            content += f"- **Path**: `{cp}`\n"
            funcs = [func for func in func_entities if func.file_path == f.file_path]
            if funcs:
                content += "- **Functions**:\n"
                for func in funcs[:5]:
                    content += f"  - `{func.name}`\n"
            content += "\n"

    elif doc_type == "class":
        content = "# 🧩 Class Documentation\n\n"
        if not class_entities:
            content += "No classes detected in the codebase.\n"
        for c in class_entities[:20]:
            content += f"## `class {c.name}`\n"
            content += f"- **Defined in**: `{clean_path(c.file_path)}`\n\n"
            
    elif doc_type == "wiki":
        content = "# 📚 Project Wiki\n\n"
        content += "> *Welcome to the auto-generated project knowledge base. This wiki serves as a central hub for understanding the structural and functional aspects of your codebase.*\n\n"
        
        content += "## 📑 Table of Contents\n"
        content += "1. [Project Overview](#project-overview)\n"
        content += "2. [Core Architecture](#core-architecture)\n"
        content += "3. [Data Models & Entities](#data-models--entities)\n"
        content += "4. [Key Subsystems](#key-subsystems)\n\n"

        content += "---\n\n"

        content += "## 🚀 Project Overview\n"
        content += f"This repository is analyzed as a system composed of **{len(file_entities)} files**, housing **{len(class_entities)} classes** and **{len(func_entities)} functions**.\n\n"
        content += "### Primary Entry Points\n"
        entry_points = [f for f in file_entities if "main" in f.file_path.lower() or "app" in f.file_path.lower()]
        if entry_points:
            for ep in entry_points[:5]:
                content += f"- `{clean_path(ep.file_path)}`\n"
        else:
            content += "*(No explicit `main` or `app` files detected, system may be a library or use dynamic routing)*\n"
        content += "\n"

        content += "## 🏗️ Core Architecture\n"
        content += "The system is physically divided into several key directories:\n\n"
        components = defaultdict(list)
        for f in file_entities:
            cp = clean_path(f.file_path)
            folder = os.path.dirname(cp)
            components[folder if folder else "Root"].append(os.path.basename(cp))
        
        # Sort folders by size (number of files)
        sorted_components = sorted(components.items(), key=lambda x: len(x[1]), reverse=True)
        
        for comp, files in sorted_components[:8]:
            content += f"### 📁 `{comp}`\n"
            content += f"Contains {len(files)} files, including:\n"
            for file in files[:3]:
                content += f"- `{file}`\n"
            if len(files) > 3:
                content += f"- *(+{len(files)-3} more)*\n"
            content += "\n"

        content += "## 🧩 Data Models & Entities\n"
        models = [c for c in class_entities if "model" in c.file_path.lower() or "schema" in c.file_path.lower()]
        if not models:
            models = class_entities[:5]
        if models:
            content += "The following foundational entities dictate the data structures within the system:\n\n"
            for m in models:
                content += f"- **`{m.name}`** (defined in `{clean_path(m.file_path)}`)\n"
        else:
            content += "*(No class-based data models were detected)*\n"
        content += "\n"

        content += "## ⚙️ Key Subsystems\n"
        content += "The operational logic spans the following top-level components:\n\n"
        content += "| Component Name | Related File Count | Primary Responsibility |\n"
        content += "| -------------- | ------------------ | ---------------------- |\n"
        for idx, (comp, files) in enumerate(sorted_components[:5]):
            resp = "API Layer" if "api" in comp.lower() or "route" in comp.lower() else "Business Logic" if "service" in comp.lower() or "core" in comp.lower() else "Data Access" if "db" in comp.lower() or "store" in comp.lower() else "Application Module"
            content += f"| `{comp}` | {len(files)} files | {resp} |\n"
        content += "\n"

    else:
        raise HTTPException(status_code=404, detail="Documentation type not found")

    return {"content": content}


