import os
import json
from pathlib import Path

def run_metadata_gen(id, model, type, solved, pat1, pat3, avg_iter,embedder="all-mini-LLM-v3", k_value="3"):
    match type:
        case "vanilla":
            out= {
                "run_id": f"{model}_{type}_{id}",
                "model": f"{model}",
                "k_value": f"{k_value}",
                "run_results": {
                    "solved": f"{solved}",
                    "pass@1": f"{pat1}",
                    "pass@3": f"{pat3}"
                }
            }
        case _:
            out ={
                "run_id": f"{model}_{type}_{id}",
                "model": f"{model}",
                "memory_type": f"{type}",
                "embedding_model": f"{embedder}",
                "k_value": f"{k_value}",
                "run_results": {
                    "solved": f"{solved}",
                    "pass@1": f"{pat1}",
                    "pass@3": f"{pat3}",
                    "avg_iterations": f"{avg_iter:.3f}"
                }
            }

    return json.dumps(out)

def analyze_results(type):
    base_dir =Path(__file__).parent
    directory = f"{base_dir}/{type}"
    run_id=0

    file_map = {
        "vanilla": "samples_results.jsonl",
        "reflexion": "reflexion_samples.jsonl",
        "vector_mem": "reflexion_samples_vector.jsonl"
    }

    for filename in os.listdir(directory):
        folder = os.path.join(directory,filename)

        if os.path.isdir(folder):
            sample_file = os.path.join(folder,file_map.get(type))

            with open(sample_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                model = json.loads(lines[-1]).get("model")

                k_count = 1
                pass_count = 0
                pat1 = 0
                pat3 = 0
                avg_iter = None
                iterations = []
                for line in lines:

                    # Strip and clean lines
                    line=line.strip()
                    if(line[-1]==","):
                        line_json = json.loads(line[:-1])
                    else:
                        line_json = json.loads(line)

                    if(line_json.get("task_id")):
                        # Extract values
                        id = line_json.get("task_id")
                        completion = line_json.get("completion")
                        last_completion = line_json.get("last_completion")
                        passed = line_json.get("passed")

                        if(line_json.get("passed") and k_count<=3):
                            pass_count += 1
                            iterations.append(k_count)
                            if k_count==1:
                                pat1 +=1
                            elif k_count ==3:
                                pat3 += 1
                            k_count = 1
                        elif(k_count == 3):
                            k_count = 1
                        else:
                            k_count += 1
            
                if (type != "vanilla"):
                    avg_iter = sum(iterations)/len(iterations)

                with open(f"{type}_analysis.json", "a") as f:
                    f.write(run_metadata_gen(run_id,model,type, pass_count, pat1, pat3, avg_iter)+",")
        
        run_id += 1

analyze_results("vanilla")

analyze_results("reflexion")

analyze_results("vector_mem")