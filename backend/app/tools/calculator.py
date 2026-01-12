import math

def calculator(expression: str) -> str:
    """
    Simple calculator tool.
    Supports basic arithmetic safely.
    """
    try:
        allowed_names = {
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs,
            "round": round
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"
