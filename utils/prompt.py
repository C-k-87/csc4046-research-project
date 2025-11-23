# 3. PROMPT TEMPLATES

# A. The ACTOR Prompt (for initial attempt and subsequent attempts with reflection)
CODE_PROMPT_TEMPLATE = """
<|system|>
You are an expert Python programmer. Your task is to implement the function described below.
Your response MUST be ONLY the function implementation ensuring the retention of orginal imports defined in the problem. Do not include any explanations, examples, or tests.
The function signature is already provided. Format your answer with the python code markdown (```python ```)

<|user|>
function to implement:
{task_prompt}

<|assistant|>
{reflection}
"""

# B. The REFLECTION Prompt (for generating feedback after a failed test)
REFLEXION_PROMPT_TEMPLATE = """
Your previous attempt to solve the function:
{attempt_code}

The unit tests failed with the following traceback/error:
{test_error}

Analyze the failed attempt and the error. Provide a concise, one-paragraph reflection on the likely cause of the bug and a high-level strategy for fixing it.
Your reflection will be used to guide your next attempt.

Reflection:
"""