if __name__=="__main__":
    print("Adding current working directory to sys.path for module imports.")
    import sys
    from pathlib import Path

    sys.path.append(str(Path.cwd()))

import os
import json
from human_eval.human_eval.data import read_problems, write_jsonl
from human_eval.human_eval.execution import check_correctness

from utils.logger import get_logger
from utils.tools import extract_code, extract_reflection
from utils.vector_store import add_reflection, search
from utils.prompt import CODE_PROMPT_TEMPLATE, REFLEXION_PROMPT_TEMPLATE

log = get_logger()
samples = []

problems = read_problems()

def human_eval_loop(llm, log_results, vector_memory, max_trials):
    if log_results:
        os.makedirs("runtime_logs", exist_ok=True)
        with open(
            "runtime_logs/reflexion_samples_vector.jsonl" if vector_memory else "runtime_logs/reflexion_samples.jsonl",
            "a"
        ) as run_log:
        
            for task_id in problems:
                task_data = problems[task_id]
                task_prompt = task_data["prompt"]
                reflexion_run(llm, task_id, task_data, task_prompt, vector_memory, max_trials)
        
                results = [d for d in samples[-max_trials:] if d.get("task_id")==samples[-1].get("task_id")]
                log_entry = "\n".join(json.dumps(entry) for entry in results)
                run_log.write(log_entry+",\n")
                
            run_specs = json.dumps({
                "model":llm.get_llm().metadata['general.name'],
                "max_trials":max_trials,
                "passed":len([d for d in samples if d.get("passed")==True]),
                "failed":len(problems)-len([d for d in samples if d.get("passed")==True])
            })+"\n"

            run_log.write(run_specs)

    else:   # no logging to file for debugging purposes
        for task_id in problems:
            task_data = problems[task_id]
            task_prompt = task_data["prompt"]
            reflexion_run(llm, task_id, task_data, task_prompt, vector_memory, max_trials)


def reflexion_run(llm, task_id, task_data, task_prompt, vector_memory, max_trials):
    current_reflection = ""
    is_solved = False
    all_attempts = []

    log.info("ATTEMPTING PROBLEM:\n%s",task_prompt)

    for trial_num in range(1, max_trials+1):
        log.info("------ TRIAL %s ------", trial_num)

        # action phase
        action_prompt = CODE_PROMPT_TEMPLATE.format(
            reflection=f"previous reflections: {current_reflection}\n" if current_reflection else "",
            task_prompt =task_prompt
        ).strip()
        log.info("ACTION PROMPT: ---------------------------\n %s \n", action_prompt)

        generation = llm.generate_one_completion(action_prompt, max_tokens=500)
        log.info("NON EXTRACTED CODE:--------- \n%s\n-----------",generation)
        generation = extract_code(generation)

        # evaluation phase
        check = check_correctness(
            task_data,
            generation,
            timeout=60
        )

        log.info("CHECK CORRECTNESS:\n%s\n",check)

        all_attempts.append({
            "trial": trial_num,
            "code": generation,
            "passed": check["passed"]
        })

        # check result
        if check["passed"]:
            log.info(f"SUCCESS! Problem %s solved in %s trial(s).",task_id, trial_num)
            is_solved = True
            samples.append({'task_id':task_id, 'completion':generation, 'passed':True})
            break
        else:
            error = check.get("result", "Tests failed with an unknown error.")
            log.warning("FAILED TEST: %s...", error[:200])
            samples.append({'task_id':task_id, 'last_completion':generation, 'error-200':error[:200], 'passed':False})

        # reflection
        if trial_num < max_trials:
            reflection_prompt = REFLEXION_PROMPT_TEMPLATE.format(
                attempt_code=generation,
                test_error=error,
            )

            reflection = llm.generate_one_completion(reflection_prompt, max_tokens=500, stop=["###"])
            log.info("Generated Reflection\n%s\n",reflection)
            reflection = extract_reflection(reflection)

            if vector_memory:
                add_reflection(reflection)
                current_reflection = '\n'.join(search(reflection)["documents"][0])
            else:
                current_reflection = reflection
            
            log.info("RETRIEVED REFLECTION:\n %s\n",current_reflection)
    
    if not is_solved:
        log.warning("FINAL FAILURE. Problem %s was not solved within %s trials.", task_id, max_trials)
    
if __name__=="__main__":
    log.info("Running reflexion runner standalone.")
    from utils.local_llm import LocalLLM

    llm_model = "gguf/Phi-3-mini-4k-instruct-q4.gguf"
    n_ctx=700
    n_gpu_layers=999
    verbosity = False

    llm = LocalLLM(llm_model, n_ctx, n_gpu_layers, verbosity)

    # for independent runs
    task_id_list = [f"HumanEval/{i}" for i in range(100,110)]
    print(task_id_list)
    MAX_TRIALS=3

    for TASK_ID in task_id_list:
        reflexion_run(
            llm, TASK_ID,
            task_data=problems[TASK_ID],
            task_prompt=problems[TASK_ID]["prompt"],
            vector_memory=True,
            max_trials=MAX_TRIALS
        )
