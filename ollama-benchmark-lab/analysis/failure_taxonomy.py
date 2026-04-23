def classify(output: str) -> str:
    o = output.lower()

    if "syntaxerror" in o:
        return "syntax_error"
    if "assert" in o:
        return "logic_error"
    if "importerror" in o:
        return "api_error"
    if "timeout" in o:
        return "timeout"
    if "git apply" in o:
        return "patch_error"

    return "unknown"