from human_eval.human_eval.data import read_problems, write_jsonl
from human_eval.human_eval.execution import check_correctness

from utils.logger import get_logger
from utils.tools import extract_code
from utils.prompt import CODE_PROMPT_TEMPLATE, REFLEXION_PROMPT_TEMPLATE

MAX_TRIALS=3
TASK_ID = "HumanEval/2"

log = get_logger()
samples = []

problems = read_problems()
task_data = problems[TASK_ID]
task_prompt = task_data["prompt"]

def human_eval_loop(llm):
    for task_id in problems:
        task_data = problems[task_id]
        task_prompt = task_data["prompt"]
        reflexion_run(llm, task_id, task_data, task_prompt)
    
    write_jsonl("reflexion_samples.jsonl",samples)

def reflexion_run(llm, task_id, task_data, task_prompt):
    current_reflection = ""
    is_solved = False
    all_attempts = []

    log.info("ATTEMPTING PROBLEM:\n%s",task_prompt)

    for trial_num in range(1, MAX_TRIALS+1):
        log.info("------ TRIAL %s ------", trial_num)

        # action phase
        action_prompt = CODE_PROMPT_TEMPLATE.format(
            reflection=f"previous attempt: {current_reflection}\n" if current_reflection else "",
            task_prompt =task_prompt
        ).strip()
        log.info("ACTION PROMPT: ---------------------------\n %s \n", action_prompt)

        generation = llm.generate_one_completion(action_prompt, max_tokens=300)
        generation = extract_code(generation)
        log.info("GENERATED CODE: ---------------------------\n%s\n",generation)

        # evaluation phase
        check = check_correctness(
            task_data,
            generation,
            timeout=999
        )

        log.debug("CHECK CORRECTNESS:\n%s\n",check)

        all_attempts.append({
            "trial": trial_num,
            "code": generation,
            "passed": check["passed"]
        })

        # check result
        if check["passed"]:
            print(f"SUCCESS! Problem {TASK_ID} solved in {trial_num} trial(s).")
            is_solved = True
            break
        else:
            error = check.get("result", "Tests failed with an unknown error.")
            log.warning("FAILED TEST: %s...", error[:200])

        # reflection
        if trial_num < MAX_TRIALS:
            reflection_prompt = REFLEXION_PROMPT_TEMPLATE.format(
                attempt_code=generation,
                test_error=error,
            )

            current_reflection = llm.generate_one_completion(reflection_prompt, max_tokens=500, stop=["###"])
            log.info("GENERATED REFLECTION:\n %s\n",current_reflection)
    
    if is_solved:
        samples.append({'task_id':task_id, 'completion':generation, 'passed':True})
    else:
        log.warning("FINAL FAILURE. Problem %s was not solved within %s trials.", TASK_ID, MAX_TRIALS)
        samples.append({'task_id':task_id, 'last_completion':generation, 'passed':False})