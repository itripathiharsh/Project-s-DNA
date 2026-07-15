from dna.parser.ast_builder import parse_source


def test_python_functions():
    result = parse_source("def foo(a, b): pass\ndef bar(): return 1", "Python")
    assert result is not None
    assert len(result.symbols.functions) == 2
    assert result.symbols.functions[0].name == "foo"
    assert result.symbols.functions[0].params == ["a", "b"]
    assert result.symbols.functions[1].name == "bar"
    assert result.symbols.functions[1].params == []


def test_python_class():
    source = """
class MyClass(Base):
    def method(self, x):
        pass
"""
    result = parse_source(source, "Python")
    assert result is not None
    assert len(result.symbols.classes) == 1
    cls = result.symbols.classes[0]
    assert cls.name == "MyClass"
    assert "Base" in cls.base_classes
    assert len(cls.methods) == 1
    assert cls.methods[0].name == "method"
    assert cls.methods[0].is_method is True


def test_python_imports():
    source = "import os\nfrom pathlib import Path\n"
    result = parse_source(source, "Python")
    assert result is not None
    assert len(result.symbols.imports) == 2
    assert result.symbols.imports[0].kind == "import"
    assert result.symbols.imports[1].kind == "from"


def test_javascript_functions():
    source = "function add(a, b) { return a + b; }\nfunction empty() {}"
    result = parse_source(source, "JavaScript")
    assert result is not None
    assert len(result.symbols.functions) == 2
    assert result.symbols.functions[0].name == "add"
    assert "a" in result.symbols.functions[0].params


def test_javascript_class():
    source = """
class Animal {
    constructor(name) { this.name = name; }
    speak() { return this.name; }
}
"""
    result = parse_source(source, "JavaScript")
    assert result is not None
    assert len(result.symbols.classes) == 1
    assert result.symbols.classes[0].name == "Animal"
    assert len(result.symbols.classes[0].methods) >= 2


def test_javascript_imports():
    source = 'import { foo } from "./bar";\nimport React from "react";'
    result = parse_source(source, "JavaScript")
    assert result is not None
    assert len(result.symbols.imports) == 2


def test_javascript_exports():
    source = "export function hello() {}\nexport class X {}"
    result = parse_source(source, "JavaScript")
    assert result is not None
    assert len(result.symbols.exports) >= 2


def test_empty_source():
    result = parse_source("", "Python")
    assert result is not None
    assert len(result.symbols.functions) == 0
    assert len(result.symbols.classes) == 0


def test_python_nested_class():
    source = """
class Outer:
    class Inner:
        def inside(self): pass
"""
    result = parse_source(source, "Python")
    assert result is not None
    assert len(result.symbols.classes) == 2
    names = {c.name for c in result.symbols.classes}
    assert names == {"Outer", "Inner"}


def test_typescript_symbols():
    source = """
import { Axios } from "axios";
export interface User {
    id: number;
    name: string;
}
export enum Role {
    Admin,
    User
}
type ID = string | number;
export class Account {
    constructor(public id: ID) {}
    login(): void {}
}
"""
    result = parse_source(source, "TypeScript")
    assert result is not None
    assert result.language == "TypeScript"
    
    # Imports
    assert len(result.symbols.imports) == 1
    assert result.symbols.imports[0].source == "axios"
    
    # Exports (User, Role, Account)
    assert len(result.symbols.exports) >= 3
    export_names = {e.name for e in result.symbols.exports}
    assert "User" in export_names
    assert "Role" in export_names
    assert "Account" in export_names
    
    # Classes / Types / Interfaces / Enums (User, Role, ID, Account)
    class_names = {c.name for c in result.symbols.classes}
    assert "User" in class_names
    assert "Role" in class_names
    assert "ID" in class_names
    assert "Account" in class_names
    
    # Functions / Methods
    methods = [f for f in result.symbols.functions if f.is_method]
    assert len(methods) >= 1
    method_names = {m.name for m in methods}
    assert "login" in method_names


def test_go_symbols():
    source = """package main
import (
    "fmt"
    "os"
)
type User struct {
    Name string
}
func Hello(a int) {}
func (u *User) GetName() string { return u.Name }
"""
    result = parse_source(source, "Go")
    assert result is not None
    assert result.language == "Go"
    
    # Imports
    assert len(result.symbols.imports) == 2
    sources = {imp.source for imp in result.symbols.imports}
    assert "fmt" in sources
    assert "os" in sources
    
    # Classes / Structs
    assert len(result.symbols.classes) == 1
    assert result.symbols.classes[0].name == "User"
    
    # Functions and methods
    assert len(result.symbols.functions) == 2
    funcs = {f.name: f for f in result.symbols.functions}
    assert "Hello" in funcs
    assert "GetName" in funcs
    assert funcs["GetName"].is_method is True
    
    # Check that GetName is associated with User methods
    assert len(result.symbols.classes[0].methods) == 1
    assert result.symbols.classes[0].methods[0].name == "GetName"
    
    # Exports
    exports = {exp.name for exp in result.symbols.exports}
    assert "Hello" in exports
    assert "User" in exports


def test_rust_symbols():
    source = """
pub struct Point {
    pub x: i32,
    pub y: i32,
}
fn add(a: i32, b: i32) -> i32 { a + b }
impl Point {
    pub fn distance(&self) -> f64 { 0.0 }
}
"""
    result = parse_source(source, "Rust")
    assert result is not None
    assert result.language == "Rust"
    
    # Classes / Structs
    assert len(result.symbols.classes) == 1
    assert result.symbols.classes[0].name == "Point"
    
    # Functions
    assert len(result.symbols.functions) == 2
    funcs = {f.name: f for f in result.symbols.functions}
    assert "add" in funcs
    assert "distance" in funcs
    assert funcs["distance"].is_method is True
    
    # Check that distance is associated with Point methods
    assert len(result.symbols.classes[0].methods) == 1
    assert result.symbols.classes[0].methods[0].name == "distance"
    
    # Exports
    exports = {exp.name for exp in result.symbols.exports}
    assert "Point" in exports
