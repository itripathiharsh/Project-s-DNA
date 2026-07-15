from dna.engines.risk import analyze_risks
from dna.models import EntityGraph, Entity, DependencyGraph


def test_no_source_files():
    g = EntityGraph()
    g.add_entity(Entity(uid="file:test_x.py", name="test_x.py", kind="file", file_path="test_x.py"))
    result = analyze_risks(g)
    assert result["source_files"] == 0
    assert result["overall_risk_score"] >= 0


def test_all_source_no_tests():
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    g.add_entity(Entity(uid="file:utils.py", name="utils.py", kind="file", file_path="utils.py"))
    result = analyze_risks(g)
    assert result["test_files"] == 0
    assert result["test_file_ratio"] == 0


def test_orphaned_modules():
    g = EntityGraph()
    g.add_entity(Entity(uid="file:a.py", name="a.py", kind="file", file_path="a.py"))
    g.add_entity(Entity(uid="file:b.py", name="b.py", kind="file", file_path="b.py"))
    dg = DependencyGraph()
    result = analyze_risks(g, dg)
    orphans = result["orphaned_modules"]
    assert len(orphans) >= 2


def test_high_complexity_limit():
    g = EntityGraph()
    g.add_entity(Entity(uid="file:main.py", name="main.py", kind="file", file_path="main.py"))
    for i in range(20):
        g.add_entity(Entity(uid=f"function:main.py:f{i}", name=f"f{i}", kind="function", file_path="main.py"))
    result = analyze_risks(g)
    assert len(result["high_complexity_files"]) == 1
    assert result["high_complexity_files"][0]["file"] == "main.py"
