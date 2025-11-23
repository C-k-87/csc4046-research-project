import re
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
        start = fence_indices[0]
        end = fence_indices[1]
        code_lines = lines[start+1:end]
        
        # Remove language identifier if present on first line
        if code_lines and code_lines[0].strip().lower() in ['python', 'py']:
            code_lines = code_lines[1:]
        
        return '\n'.join(code_lines).strip()
    
    # If no fences found, return the text as-is (stripped)
    log.warning("CODE EXTRACTOR MATCHED NO PATTERNS")
    return generation.strip()