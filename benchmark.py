#!/usr/bin/env python3
import json
import requests
import time
import os
import re
import threading
import itertools
from statistics import median

SYSTEM_PROMPT = "Du bist ein Kandidat bei 'Wer wird Millionär'. Wähle die richtige Antwort aus den vier Optionen. Antworte AUSCHLIESSLICH mit einem einzigen Buchstaben: A, B, C oder D. Keine andere Erklärung, nur der Buchstabe! Beispiel: Wenn A die richtige Antwort ist, antworte nur: A"
SERVER_URL = "http://localhost:1234" # e.g. https://openrouter.ai/api (/v1 not needed).
API_KEY = ""
MODEL_NAME = "mistral-small-3.2"
TEMPERATURE = 0.8
TOP_K = 40
TOP_P = 0.95

FAIL_CHARS = "123456789ABCDEF"
PRIZE_LEVELS = ["50€", "100€", "200€", "300€", "500€", "1.000€", "2.000€", "4.000€", "8.000€", "16.000€", "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"]
PRIZE_AMOUNTS = {i + 1: amount for i, amount in enumerate(PRIZE_LEVELS)}
AMOUNT_MAPPING_INT = {amount: int(amount.replace('€', '').replace('.', '')) for amount in PRIZE_LEVELS}
AMOUNT_MAPPING_INT["0€"] = 0

def calculate_average_amount(rounds):
    if not rounds: return "0€"
    total = sum(AMOUNT_MAPPING_INT[PRIZE_AMOUNTS.get(r["correct_answers"], "0€")] for r in rounds)
    average = total / len(rounds)
    return f"{average:,.0f}€".replace(",", ".") if average >= 1000 else f"{int(average)}€"

def calculate_median_amount(rounds):
    if not rounds: return "0€"
    amounts = [AMOUNT_MAPPING_INT[PRIZE_AMOUNTS.get(r["correct_answers"], "0€")] for r in rounds]
    median_amount = median(amounts)
    return f"{median_amount:,.0f}€".replace(",", ".") if median_amount >= 1000 else f"{int(median_amount)}€"

model_name = MODEL_NAME
header = f"""
Wer wird Millionär? Benchmark
=====================================
Model:    {model_name}
URL:      {SERVER_URL}
Sampling: T:{TEMPERATURE}, P:{TOP_P}, K:{TOP_K}
-------------------------------------"""
print(header)

try:
    with open("fragen_antworten.json", 'r', encoding='utf-8') as f:
        questions = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading questions: {e}")
    exit(1)

verbose_mode = input("Show full LLM response? [y/N] ").strip().lower() in ['y', 'yes']

session = requests.Session()
results = []

for question_num in range(1, 46):
    current_level = 1
    correct_answers = 0
    
    print(f"Game {question_num:02d}/45: [", end="", flush=True)
    
    while current_level <= 15:
        question_data = questions.get(str(current_level), [[]])[question_num - 1]
        if not question_data: continue

        question_text, *options, correct_answer = question_data
        prompt = f"{question_text}\n" + "\n".join(f"{chr(65+i)}: {opt}" for i, opt in enumerate(options))
        
        stop_event = threading.Event()
        def _spinner_animation():
            for char in itertools.cycle(['-', '\\', '|', '/']):
                if stop_event.is_set(): break
                print(char, end='\b', flush=True)
                time.sleep(0.2)
        
        spinner_thread = threading.Thread(target=_spinner_animation)
        spinner_thread.start()
        
        try:
            data = {"model": model_name, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], "stream": False, "temperature": TEMPERATURE, "top_k": TOP_K, "top_p": TOP_P}
            headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
            response = session.post(f"{SERVER_URL}/v1/chat/completions", json=data, headers=headers, timeout=300)
            if response.status_code == 200 and (choices := response.json().get("choices")):
                response_content = choices[0].get("message", {}).get("content", "").strip()
                if verbose_mode:
                    full_response = response_content
                letters = re.findall(r'\b[A-D]\b', response_content, re.IGNORECASE)
                llm_answer = letters[-1].upper() if letters else "INVALID"
            else:
                llm_answer = "ERROR"
                if verbose_mode:
                    full_response = ""
        except requests.exceptions.RequestException:
            llm_answer = "ERROR"
            if verbose_mode:
                full_response = ""
        finally:
            stop_event.set()
            spinner_thread.join()
        
        try:
            correct_letter = chr(65 + options.index(correct_answer))
            if llm_answer == correct_letter:
                print(".", end="", flush=True)
                correct_answers += 1
                current_level += 1
            else:
                fail_char = FAIL_CHARS[current_level - 1]
                print(f"{fail_char}]", flush=True)
                if verbose_mode:
                    print(f"└─ Failed at Level {current_level}")
                    q_limit = 70
                    display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
                    print(f"   ├─ Q: {display_q}")
                    print(f"   ├─ LLM Answer: '{llm_answer}'")
                    print(f"   ├─ Correct is: '{correct_letter}'")
                    print(f"   └─ Full Response: '{full_response}'")
                break
        except ValueError:
            print("E]", flush=True)
            if verbose_mode:
                q_limit = 50
                display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
                print(f"└─ Error: Correct answer '{correct_answer}' not in options for Q: {display_q}")
                print(f"   └─ Full Response: '{full_response}'")
            break
            
    if correct_answers == 15:
        print("✓]", flush=True)
    
    results.append({"correct_answers": correct_answers})
average_amount = calculate_average_amount(results)
median_amount = calculate_median_amount(results)
million_wins = sum(1 for r in results if r["correct_answers"] == 15)
results_data = {"model": model_name, "model_parameters": {"temperature": TEMPERATURE, "top_k": TOP_K, "top_p": TOP_P}, "rounds": results, "average_final_amount": average_amount, "median_final_amount": median_amount, "million_wins": million_wins}

if "localhost" in SERVER_URL or "127.0.0.1" in SERVER_URL:
    default_dir = "local"
else:
    default_dir = "cloud"

print(f"\nServer URL suggests saving in results/{default_dir}/")
save_choice = input(f"Save result in results/{default_dir}? (Y/n): ").strip().lower()

if save_choice in ['n', 'no']:
    save_option = input("Do not save=1, Save in results/cloud=2 (1/2): ").strip()
    if save_option == "2":
        results_dir = os.path.join("results", "cloud")
    elif save_option == "1":
        results_dir = None
    else:
        results_dir = os.path.join("results", "cloud")
else:
    results_dir = os.path.join("results", default_dir)

if results_dir:
    os.makedirs(results_dir, exist_ok=True)
    base_filename = f"result_{model_name.replace('/', '-')}.json"
    result_filename = os.path.join(results_dir, base_filename)
    counter = 2
    while os.path.exists(result_filename):
        result_filename = os.path.join(results_dir, f"{base_filename.rsplit('.', 1)[0]}_{counter}.json")
        counter += 1

    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
else:
    result_filename = None
    print("Results not saved.")

print(f"\nAverage Amount: {average_amount} | Million Wins: {million_wins}")
print(f"T:{TEMPERATURE}, K:{TOP_K}, P:{TOP_P}")
if result_filename:
    print(f"Saved results to: {result_filename}")
else:
    print("Results not saved to file.")

update_leaderboard = input("\nWant to update the Leaderboard? [Y/n] ").strip().lower()
if update_leaderboard in ['y', 'yes', '']:
    import subprocess
    import os
    try:
        subprocess.run(["python", "update.py"], 
                       cwd="leaderboard", check=True, stdin=None, stdout=None, stderr=None)
        print("Leaderboard updated successfully!")
    except subprocess.CalledProcessError as e:
        print("Error running leaderboard update script.")
        print("Return code:", e.returncode)
    except FileNotFoundError:
        print("Python not found. Please ensure Python is installed to update the leaderboard.")
