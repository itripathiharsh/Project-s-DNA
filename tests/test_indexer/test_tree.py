from dna.indexer.tree import build_directory_tree
from dna.models import IndexedFile, FileCategory


def _if(rel_path: str) -> IndexedFile:
    return IndexedFile(
        path="/repo/" + rel_path,
        relative_path=rel_path,
        filename=rel_path.split("/")[-1],
        extension=".py",
        language="Python",
        size_bytes=0,
        is_directory=False,
        is_source=True,
        category=FileCategory.SOURCE,
    )


def test_build_tree_flat():
    files = [_if("main.py"), _if("utils.py")]
    tree = build_directory_tree(files)
    assert len(tree.root.files) == 2
    assert tree.max_depth == 1


def test_build_tree_nested():
    files = [_if("src/main.py"), _if("src/utils.py"), _if("README.md")]
    tree = build_directory_tree(files)
    assert len(tree.root.files) == 1  # README.md
    assert len(tree.root.children) == 1
    assert tree.root.children[0].name == "src"
    assert len(tree.root.children[0].files) == 2


def test_build_tree_deep():
    files = [_if("a/b/c/d.py")]
    tree = build_directory_tree(files)
    assert tree.max_depth == 4
    assert tree.total_dirs == 3


def test_build_tree_empty():
    tree = build_directory_tree([])
    assert tree.max_depth == 0
    assert tree.total_dirs == 0
    assert len(tree.root.files) == 0
