from utils.local_llm import LocalLLM
from runners.reflexion import human_eval_loop
from runners.vanilla import vanilla_run

# --- LLM Specifications ---

llm_model = "gguf/Phi-3-mini-4k-instruct-q4.gguf"
n_ctx=4096
n_gpu_layers=999
verbosity = False
logging =True
vector_memory =True

llm = LocalLLM(llm_model, n_ctx, n_gpu_layers, verbosity)

# ---------------------------

human_eval_loop(llm, logging, vector_memory, max_trials=3)
# vanilla_run(llm, max_trials=3)