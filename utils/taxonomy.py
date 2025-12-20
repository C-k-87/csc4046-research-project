bug_taxonomy = {
    "RETURN_CONTRACT_VIOLATION" : "Always return exactly the value, type, and structure specified by the problem—no extra nesting, missing elements, or intermediate results.",

    "EDGE_CASE_MISSING" : "Explicitly handle empty, None, or minimal inputs before applying general logic.",

    "INPUT_VALIDATION_ERROR" : "Ensure the input matches the expected format and assumptions before processing it.",

    "ITERATION_LOGIC_ERROR" : "Verify loop boundaries, update conditions, and accumulation logic so that all elements are processed exactly once as intended.",

    "INDEX_BOUND_ERROR" : "Never index, pop, or access elements without first ensuring the data structure is non-empty and the index is valid.",

    "DATA_STRUCTURE_MISUSE" : "Use data structures that match the required operations, and avoid mutating a structure while iterating over it unless explicitly safe.",

    "RECURSION_STRUCTURE_ERROR" : "Ensure recursive functions have a reachable base case and that each recursive call moves strictly closer to it.",

    "PROBLEM_INTERPRETATION_ERROR" : "Re-read the problem description and examples to confirm the intended behavior before modifying the implementation.",
}
