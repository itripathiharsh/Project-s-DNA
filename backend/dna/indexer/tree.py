from dna.models import IndexedFile, DirectoryNode, DirectoryTree


def build_directory_tree(files: list[IndexedFile]) -> DirectoryTree:
    root = DirectoryNode(name=".", path=".")
    max_depth = 0
    total_dirs = 0

    for f in files:
        parts = f.relative_path.replace("\\", "/").split("/")
        parts = [p for p in parts if p]
        max_depth = max(max_depth, len(parts))

        if len(parts) == 1:
            root.files.append(f)
            continue

        node = root
        for i, part in enumerate(parts[:-1]):
            found = False
            for child in node.children:
                if child.name == part:
                    node = child
                    found = True
                    break
            if not found:
                new_node = DirectoryNode(
                    name=part,
                    path="/".join(parts[: i + 1]),
                )
                node.children.append(new_node)
                node = new_node
                total_dirs += 1

        node.files.append(f)

    return DirectoryTree(
        root=root,
        max_depth=max_depth,
        total_dirs=total_dirs,
    )
