def calculate_complexity(node, language: str) -> int:
    complexity = 1

    def visit(n):
        nonlocal complexity

        if language == "Python":
            if n.type in (
                "if_statement",
                "elif_clause",
                "for_statement",
                "while_statement",
                "except_clause",
                "conditional_expression",
                "boolean_operator"
            ):
                complexity += 1

        elif language in ("Go", "JavaScript", "TypeScript"):
            if n.type in (
                "if_statement",
                "for_statement",
                "while_statement",
                "do_statement",
                "catch_clause",
                "case",
                "communication_case",
                "switch_case"
            ):
                complexity += 1
            elif n.type == "binary_expression":
                for child in n.children:
                    if child.type in ("&&", "||"):
                        complexity += 1
                        break

        elif language == "Rust":
            if n.type in (
                "if_expression",
                "if_let_expression",
                "for_expression",
                "while_expression",
                "loop_expression",
                "match_arm"
            ):
                complexity += 1
            elif n.type == "binary_expression":
                for child in n.children:
                    if child.type in ("&&", "||"):
                        complexity += 1
                        break

        for child in n.children:
            visit(child)

    visit(node)
    return complexity
