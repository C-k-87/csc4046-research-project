from utils.logger import get_logger
from utils.local_llm import LocalLLM
from utils.reflexion import reflexion_run, human_eval_loop
# from utils.vanilla import vanilla_run

log = get_logger()

# --- LLM Specifications ---

llm_model = "gguf/Phi-3-mini-4k-instruct-q4.gguf"
n_ctx=4096
n_gpu_layers=999
verbosity = False

llm = LocalLLM(llm_model, n_ctx, n_gpu_layers, verbosity)

# ---------------------------

# reflexion_run(llm)
human_eval_loop(llm)
