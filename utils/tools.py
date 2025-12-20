import re

from collections import Counter
from .taxonomy import bug_taxonomy
from .logger import get_logger

log = get_logger()

def extract_code(generation):
    # Try markdown code blocks with ```
    # [\s\S]*```python\s*([\s\S]*)(?:```[\s\S]*)
    pattern = r'(?:[\s\S]*)?```python\s*([\s\S]*?)\s*(?:```[\s\S]*)'

    match = re.search(pattern, generation)
    if match:
        log.info("CODE EXTRACTION | MATCHED PATTERN for python MD")
        return match.group(1).strip()
    
    # We could try to implement a few more possibilities to extract code from prompts.
    # Depending on the model we can get quite random answers
    # Try code blocks with ===
    pattern = r'(?:[\s\S]*)?===([\s\S]*)\s(?:[\s\S]*)'
    match = re.search(pattern, generation)
    if match:
        log.info("CODE EXTRACTION | MATCHED PATTERN for ===")
        return match.group(1).strip()
    
    # Try to find content between various fence patterns (===, ---, etc.)
    # Look for lines that are just repeated characters
    lines = generation.split('\n')
    fence_indices = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check if line is a fence (3+ repeated chars from common fence set)
        if len(stripped) >= 3 and len(set(stripped)) == 1 and stripped[0] in '`~=-#*':
            fence_indices.append(i)
    
    # If we found at least 2 fences, extract content between first pair
    if len(fence_indices) >= 2:
        code_lines = lines[fence_indices[0]+1:fence_indices[1]]
        
        # Remove language identifier if present on first line
        if code_lines and code_lines[0].strip().lower() in ['python', 'py']:
            code_lines = code_lines[1:]
        
        return '\n'.join(code_lines).strip()
    
    # If no fences found, return the text as-is (stripped)
    log.warning("CODE EXTRACTOR MATCHED NO PATTERNS")
    return generation.strip()

def extract_reflection(reflection):
    pattern = r'^([^\n]+(?:\n(?!\n)[^\n]+)*)'
    match = re.match(pattern, reflection)

    if match:
        log.info("REFLECTION EXTRACTION | MATCHED REFLECTION")
        return match.group(1).strip()
    else:
        log.warning("REFLECTION EXTRACTION | NO MATCH")
        return reflection

def classify_bug(reflection):
    t = reflection.lower()

    if "return" in t or "output" in t:
        return "RETURN_CONTRACT_VIOLATION"
    if "empty" in t or "none" in t or "minimal" in t:
        return "EDGE_CASE_MISSING"
    if "input" in t and ("valid" in t or "format" in t):
        return "INPUT_VALIDATION_ERROR"
    if "loop" in t or "iterate" in t:
        return "ITERATION_LOGIC_ERROR"
    if "index" in t or "out of range" in t or "pop" in t:
        return "INDEX_BOUND_ERROR"
    if "data structure" in t or "stack" in t or "list" in t:
        return "DATA_STRUCTURE_MISUSE"
    if "recursion" in t or "base case" in t:
        return "RECURSION_STRUCTURE_ERROR"

    return "PROBLEM_INTERPRETATION_ERROR"

def get_top_k_bugs(reflections, k):
    bug_types = []
    for reflection in reflections:
        bug_type = classify_bug(reflection)
        bug_types.append(bug_type)

    counts = Counter(bug_types)
    
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1]))
    return dict(list(sorted_counts.items())[:k])

def create_injection(bug_list):
    injection =[]
    for bug_type in bug_list:
        injection.append(bug_taxonomy[bug_type])
    
    print("created injection ", injection)

    return "\n-".join(injection)