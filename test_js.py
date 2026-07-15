from tree_sitter import Language, Parser
from tree_sitter_javascript import language

p = Parser(Language(language()))
t = p.parse(b'import {x} from "a"; function f() {} class Y {}')
r = t.root_node
print(r.type, r.child_count)
print(r.child(0).type)
print(r.child(1).type)
print(r.child(2).type)
