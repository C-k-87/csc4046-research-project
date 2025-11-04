from logger import get_logger
from llama_cpp import Llama

logger = get_logger("localLLM_test")

class localLLM:
    def __init__(self, llm_model = "src/gguf/stable-code-instruct-3b-Q6_K.gguf", n_ctx=4096, n_gpu_layers=999):
        self.client = Llama(model_path=llm_model, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, n_threads=4, verbose=True)
        logger.info("Loaded model"+(llm_model))

    def prompt(self, user_prompts, system_prompts=None, assistant_prompts=None, max_tokens=200, stop=None, temperature=0.8) -> str:
        try:
            logger.info("generating response from LLM...")
            user_text = "<|user|>"+"<|user|>".join(user_prompts)
            system_text = ("<|system|>"+"<|system|>".join(system_prompts)) if system_prompts else ""
            assistant_text = ("<|assistant|>"+"<|assistant|>".join(assistant_prompts)) if assistant_prompts else "<|assistant|>"
            prompt = " ".join(filter(None, [system_text, user_text, assistant_text]))

            logger.info("LLM | recieved prompt -----------\n " + str(prompt) + "\n------------")
            response = self.client(prompt,max_tokens=max_tokens, temperature=temperature, stop=stop)
            
            return response
        except Exception as e:
            logger.error(f"prompt | Error {str(e)}")
            return {"choices":[{"text":"error occured"+str(e)}], "usage":{"total_tokens":0}}
        
    def get_tokens(self, prompt)-> int:
        tokens = self.client.tokenize(prompt.encode("utf-8"))
        return len(tokens)
    
    def extract_prompts(self, chat_prompts):
        try:
            system_instruction = []
            user_prompts = []
            assistant_prompts = []
            for prompt in chat_prompts:
                if prompt["role"] == "system":
                    system_instruction.append(prompt["content"])
                    system_instruction
                elif prompt["role"] == "user":
                    user_prompts.append(prompt["content"])
                elif prompt["role"] == "assistant":
                    assistant_prompts.append(prompt["content"])
            return system_instruction, user_prompts, assistant_prompts
        except Exception as e:
            logger.error(f"extract_prompts | Error {str(e)}")
            return [], [], []
    
if __name__ == "__main__":
    # simple REPL to test the local LLM
    agent = localLLM()
    responses = [""]

    while(True):        
        logger.info("\n------------responses so far------------" + responses[-1]+"\n")
        user_prompts = []
        system_instructions = []

        # prompt = input("\nEnter system instructions : ")

        # while prompt!="":
        #     system_instructions.append(prompt)
        #     prompt = input("Add more instructions or [ENTER] to continue: ")

        prompt = input("\nEnter your prompt : ")
        user_prompts.append(prompt) if prompt else None

        logger.info("getting token count...")
        p_count = 0
        for prompt in user_prompts:
            p_count += agent.get_tokens(prompt)

        logger.info(f"Total prompt token count: {p_count}")

        if len(responses)>0:
            user_prompts.insert(0, "your previous response: "+ responses[-1])
        
        res = agent.prompt(user_prompts=user_prompts)

        logger.info("got response from LLM ------------\n")
        print(res["choices"][0]["text"])
        logger.info("response token count: " + str(res["usage"]["total_tokens"]))
        logger.info("----------------------------------")

        responses.append(res["choices"][0]["text"])