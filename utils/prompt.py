# 3. PROMPT TEMPLATES

# A. The ACTOR Prompt (for initial attempt and subsequent attempts with reflection)
CODE_PROMPT_TEMPLATE = """
<|system|>
You are an expert Python programmer. Your task is to implement the function described below.
Your response MUST be ONLY the function implementation ensuring the retention of orginal imports defined in the problem. Do not include any explanations, examples, or tests.
The function signature is already provided. Make sure to wrap your answer with the python code markdown (```python ```).

<|user|>
function to implement:
{task_prompt}

{reflection}
<|assistant|>
"""

# B. The REFLECTION Prompt (for generating feedback after a failed test)
REFLEXION_PROMPT_TEMPLATE = """
<|system|>
You are an expert Python programmer. Your task is to analyze faulty code and advise on fixes.
Your response MUST be ONLY a single solution to the problem. Do not include any examples, or tests.
The faulty code and error are provided.

<|user|>
The previous attempt to solve the function:
{attempt_code}

The unit tests failed with the following traceback/error:
{test_error}

Analyze the failed attempt and the error. Provide a concise, one-paragraph reflection on the likely cause of the bug and a high-level strategy for fixing it.
Your reflection will be used to guide your next attempt.

<|assistant|>
"""