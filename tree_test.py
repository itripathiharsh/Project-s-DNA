from tree_sitter import Language, Parser
from tree_sitter_python import language as py_lang

parser = Parser(Language(py_lang()))
source = b'''
import os
from pathlib import Path

class MyClass:
    def method(self, x):
        pass

def hello(name):
    return f"hi {name}"
'''
tree = parser.parse(source)
root = tree.root_node

def walk(node, depth=0):
    prefix = "  " * depth
    text = source[node.start_byte:node.end_byte].decode("utf-8")[:50]
    print(f'{prefix}{node.type} [{node.start_point}->{node.end_point}] "{text}"')
    for c in node.children:
        walk(c, depth+1)

walk(root)
