import sys
from llama_cpp import Llama
from .logger import get_logger

log = get_logger()

# LLM SPECIFICATIONS -------------------------------------------------------------------------------------

class LocalLLM():
    def __init__(self, llm_model, n_ctx, n_gpu_layers, verbose, n_threads=4):
        self._llm = None

        try:
            self._llm = Llama(model_path=llm_model, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, n_threads=4, verbose=verbose)
        except Exception as e:
            log.error("Error loading LLM: ", e)
            sys.exit(1)

    def get_llm(self):
        return self._llm

    def generate_one_completion(self, user_prompt, max_tokens, temperature=0.8, stop=None,):
        completion= self._llm(
            user_prompt,
            max_tokens=max_tokens, 
            temperature=temperature, 
            stop=stop
        )
        return completion["choices"][0]["text"].strip()
    
# --------------------------------------------------------------------------------------------------------