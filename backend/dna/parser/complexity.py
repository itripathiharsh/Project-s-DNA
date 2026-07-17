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


def calculate_cognitive_complexity(node, language: str) -> int:
    complexity = 0

    def visit(n, depth):
        nonlocal complexity

        increment_types = []
        if language == "Python":
            increment_types = ["if_statement", "elif_clause", "for_statement", "while_statement", "except_clause", "conditional_expression", "boolean_operator"]
        elif language in ("Go", "JavaScript", "TypeScript"):
            increment_types = ["if_statement", "for_statement", "while_statement", "do_statement", "catch_clause", "switch_case", "communication_case"]
        elif language == "Rust":
            increment_types = ["if_expression", "if_let_expression", "for_expression", "while_expression", "loop_expression", "match_arm"]

        inc = 0
        if n.type in increment_types:
            inc = 1
        elif n.type == "binary_expression" and language in ("Go", "JavaScript", "TypeScript", "Rust"):
            for child in n.children:
                if child.type in ("&&", "||"):
                    inc = 1
                    break

        if inc > 0:
            complexity += (1 + depth)

        new_depth = depth + inc
        for child in n.children:
            visit(child, new_depth)

    visit(node, 0)
    return complexity


def calculate_halstead(node, source_bytes: bytes) -> dict:
    operators = set()
    operands = set()
    total_operators = 0
    total_operands = 0

    def visit(n):
        nonlocal total_operators, total_operands

        if not n.is_named:
            if n.type.isalnum() or n.type in {"=", "+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"}:
                operators.add(n.type)
                total_operators += 1
        else:
            if n.type in ("identifier", "property_identifier", "type_identifier", "string", "integer", "float", "number", "boolean", "true", "false", "null", "none"):
                val = source_bytes[n.start_byte:n.end_byte].decode("utf-8", errors="replace")
                operands.add(val)
                total_operands += 1
            elif n.type.endswith("_statement") or n.type.endswith("_expression") or n.type.endswith("_declaration"):
                operators.add(n.type)
                total_operators += 1

        for child in n.children:
            visit(child)

    visit(node)

    n1 = len(operators)
    n2 = len(operands)
    N1 = total_operators
    N2 = total_operands
    
    import math
    N = N1 + N2
    n = n1 + n2
    
    # Avoid log(0)
    volume = 0
    if n > 0:
        volume = N * math.log2(n)
        
    difficulty = 0
    if n2 > 0:
        difficulty = (n1 / 2) * (N2 / n2)
        
    effort = volume * difficulty

    return {
        "n1": n1,
        "n2": n2,
        "N1": N1,
        "N2": N2,
        "volume": round(volume, 2),
        "difficulty": round(difficulty, 2),
        "effort": round(effort, 2)
    }


def calculate_nesting_depth(node, language: str) -> int:
    max_depth = 0

    def visit(n, current_depth):
        nonlocal max_depth
        if current_depth > max_depth:
            max_depth = current_depth

        increment_types = []
        if language == "Python":
            increment_types = ["if_statement", "elif_clause", "for_statement", "while_statement", "except_clause", "with_statement", "try_statement"]
        elif language in ("Go", "JavaScript", "TypeScript"):
            increment_types = ["if_statement", "for_statement", "while_statement", "do_statement", "catch_clause", "switch_statement", "try_statement"]
        elif language == "Rust":
            increment_types = ["if_expression", "if_let_expression", "for_expression", "while_expression", "loop_expression", "match_expression"]

        inc = 1 if n.type in increment_types else 0
        for child in n.children:
            visit(child, current_depth + inc)

    visit(node, 0)
    return max_depth

